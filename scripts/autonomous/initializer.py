"""
Initializer Agent for AI_agents

Implements the first part of the two-agent pattern recommended by Anthropic.
The initializer agent:
1. Reads a requirements/spec file
2. Uses Claude to analyze and break it into tasks
3. Creates tasks in the state provider (Linear, GitHub, File)
4. Creates a META tracking issue
5. Writes a project state marker file

This enables optimal context window management by separating planning
from implementation.

Usage:
    from scripts.autonomous.initializer import ProjectInitializer

    initializer = ProjectInitializer(config)
    result = initializer.initialize("requirements.md")
"""

import os
import sys
import json
import yaml
import subprocess
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Check for Claude Code CLI
CLAUDE_CODE_AVAILABLE = shutil.which("claude") is not None

from scripts.state_providers import get_provider, Task, TaskStatus, TaskPriority, TaskCategory, StateProvider


class InitializerState(Enum):
    """State of the initializer"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    CREATING_TASKS = "creating_tasks"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class InitializerConfig:
    """Configuration for the project initializer"""
    # Execution backend: "claude-code" (subscription) or "anthropic-sdk" (API)
    backend: str = "claude-code"

    # Model to use
    model: str = "opus"
    max_tokens: int = 8192

    # API key (only needed for anthropic-sdk backend)
    api_key_env: str = "ANTHROPIC_API_KEY"

    # System prompt
    system_prompt_path: str = "prompts/roles/initializer-agent.md"

    # State provider
    state_provider_config: Dict[str, Any] = field(default_factory=dict)

    # Project state file
    project_state_file: str = ".project_state.json"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InitializerConfig":
        """Create config from dictionary"""
        autonomous = data.get("autonomous", {})

        return cls(
            backend=autonomous.get("backend", data.get("backend", "claude-code")),
            model=autonomous.get("model", data.get("model", "opus")),
            max_tokens=autonomous.get("max_tokens", data.get("max_tokens", 8192)),
            api_key_env=autonomous.get("api_key_env", data.get("api_key_env", "ANTHROPIC_API_KEY")),
            system_prompt_path=autonomous.get(
                "initializer_prompt_path",
                data.get("initializer_prompt_path", "prompts/roles/initializer-agent.md")
            ),
            state_provider_config=data.get("state_provider", {}),
            project_state_file=data.get("project_state_file", ".project_state.json"),
            log_level=autonomous.get("log_level", data.get("log_level", "INFO")),
            log_file=autonomous.get("log_file", data.get("log_file"))
        )

    @classmethod
    def from_yaml(cls, path: str) -> "InitializerConfig":
        """Load config from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)


@dataclass
class InitializerResult:
    """Result of project initialization"""
    success: bool
    project_id: str
    tasks_created: int
    meta_task_id: Optional[str] = None
    task_breakdown: Dict[str, int] = field(default_factory=dict)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    raw_analysis: Optional[str] = None


@dataclass
class ParsedTask:
    """A task parsed from the analysis"""
    title: str
    description: str
    priority: TaskPriority
    category: TaskCategory
    acceptance_criteria: List[str] = field(default_factory=list)
    test_steps: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class ProjectInitializer:
    """
    Project Initializer Agent.

    Implements the first part of the two-agent pattern:
    1. Analyzes requirements/spec using Claude
    2. Creates structured tasks in state provider
    3. Sets up project tracking
    """

    def __init__(self, config: InitializerConfig):
        """
        Initialize the project initializer.

        Args:
            config: Initializer configuration
        """
        self.config = config
        self.state = InitializerState.IDLE

        # Setup logging
        self._setup_logging()

        # Initialize backend
        self.client = None

        if config.backend == "claude-code":
            if not CLAUDE_CODE_AVAILABLE:
                raise RuntimeError(
                    "Claude Code CLI not found. "
                    "Install from: https://claude.ai/code or ensure 'claude' is in PATH"
                )
            self.logger.info("Using Claude Code CLI backend (subscription)")
        elif config.backend == "anthropic-sdk":
            try:
                import anthropic
                api_key = os.environ.get(config.api_key_env)
                if not api_key:
                    raise ValueError(f"API key not found: {config.api_key_env}")
                self.client = anthropic.Anthropic(api_key=api_key)
                self.logger.info("Using Anthropic SDK backend (API)")
            except ImportError:
                raise ImportError("anthropic package not installed")
        else:
            raise ValueError(f"Unknown backend: {config.backend}")

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Initialize state provider
        self.provider: Optional[StateProvider] = None
        self._init_provider()

    def _setup_logging(self):
        """Setup logging configuration."""
        log_format = "%(asctime)s [%(levelname)s] %(message)s"

        handlers = [logging.StreamHandler()]
        if self.config.log_file:
            handlers.append(logging.FileHandler(self.config.log_file))

        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            handlers=handlers
        )
        self.logger = logging.getLogger("initializer-agent")

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_path = Path(self.config.system_prompt_path)

        if not prompt_path.exists():
            self.logger.warning(f"System prompt not found: {prompt_path}")
            return self._default_system_prompt()

        with open(prompt_path, 'r') as f:
            return f.read()

    def _default_system_prompt(self) -> str:
        """Return default system prompt."""
        return """You are a Project Initializer Agent. Your job is to analyze requirements
and break them down into structured, actionable tasks.

For each requirement, create a task with:
- Clear, actionable title
- Detailed description
- Priority (1=urgent, 2=high, 3=normal, 4=low)
- Category (functional, style, infrastructure, testing, documentation, bugfix)
- Acceptance criteria (testable conditions)
- Test steps (how to verify completion)

Output your analysis in JSON format with a "tasks" array."""

    def _init_provider(self):
        """Initialize state provider."""
        try:
            self.provider = get_provider()
            self.logger.info("Initialized state provider")
        except Exception as e:
            self.logger.error(f"Failed to initialize state provider: {e}")
            raise

    def initialize(
        self,
        spec_path: str,
        project_name: Optional[str] = None,
        project_dir: Optional[str] = None
    ) -> InitializerResult:
        """
        Initialize a project from a requirements/spec file.

        Args:
            spec_path: Path to requirements or spec file
            project_name: Optional project name (derived from spec if not provided)
            project_dir: Optional project directory (current dir if not provided)

        Returns:
            InitializerResult with initialization details
        """
        project_dir = project_dir or os.getcwd()

        self.logger.info(f"Initializing project from: {spec_path}")
        self.state = InitializerState.ANALYZING

        try:
            # Read spec file
            spec_content = self._read_spec_file(spec_path)

            # Derive project name if not provided
            if not project_name:
                project_name = Path(spec_path).stem.replace("_", " ").replace("-", " ").title()

            # Analyze spec and generate tasks
            self.logger.info("Analyzing requirements with Claude...")
            analysis = self._analyze_requirements(spec_content, project_name)

            # Parse tasks from analysis
            self.logger.info("Parsing tasks from analysis...")
            tasks = self._parse_tasks(analysis)

            if not tasks:
                return InitializerResult(
                    success=False,
                    project_id="",
                    tasks_created=0,
                    error="No tasks could be parsed from analysis",
                    raw_analysis=analysis
                )

            self.logger.info(f"Parsed {len(tasks)} tasks")

            # Create tasks in state provider
            self.state = InitializerState.CREATING_TASKS
            created_tasks = self._create_tasks(tasks)

            # Create META tracking task
            meta_task_id = self._create_meta_task(project_name, created_tasks, analysis)

            # Write project state file
            project_id = self._write_project_state(
                project_name,
                project_dir,
                meta_task_id,
                created_tasks
            )

            # Calculate breakdown stats
            task_breakdown = self._calculate_task_breakdown(tasks)
            priority_distribution = self._calculate_priority_distribution(tasks)

            self.state = InitializerState.COMPLETE

            return InitializerResult(
                success=True,
                project_id=project_id,
                tasks_created=len(created_tasks),
                meta_task_id=meta_task_id,
                task_breakdown=task_breakdown,
                priority_distribution=priority_distribution,
                raw_analysis=analysis
            )

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.state = InitializerState.ERROR
            return InitializerResult(
                success=False,
                project_id="",
                tasks_created=0,
                error=str(e)
            )

    def _read_spec_file(self, spec_path: str) -> str:
        """Read and return spec file content."""
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        with open(path, 'r') as f:
            return f.read()

    def _analyze_requirements(self, spec_content: str, project_name: str) -> str:
        """
        Analyze requirements using Claude.

        Args:
            spec_content: Content of spec/requirements file
            project_name: Name of the project

        Returns:
            Analysis response from Claude
        """
        prompt = f"""# Project: {project_name}

## Requirements/Specification

{spec_content}

---

## Your Task

Analyze the above requirements and break them down into structured, actionable development tasks.

For EACH task, provide:
1. **Title**: Clear, actionable (e.g., "Implement user login endpoint")
2. **Description**: Detailed explanation of what needs to be done
3. **Priority**: 1 (urgent), 2 (high), 3 (normal), or 4 (low)
4. **Category**: One of: functional, style, infrastructure, testing, documentation, bugfix
5. **Acceptance Criteria**: List of testable conditions for completion
6. **Test Steps**: How to verify the task is complete
7. **Labels**: Relevant tags (e.g., ["frontend", "auth"])
8. **Dependencies**: IDs of tasks that must be completed first (use task numbers like "task-1")

Output your analysis as a JSON object with this structure:

```json
{{
  "project_summary": "Brief project description",
  "total_estimated_tasks": <number>,
  "tasks": [
    {{
      "id": "task-1",
      "title": "Task title",
      "description": "Detailed description",
      "priority": 2,
      "category": "functional",
      "acceptance_criteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "test_steps": [
        "Step 1",
        "Step 2"
      ],
      "labels": ["label1", "label2"],
      "dependencies": []
    }}
  ]
}}
```

Be thorough - break down complex features into smaller, manageable tasks.
Order tasks by logical implementation sequence.
Ensure each task is independently completable within a few hours."""

        return self._call_claude(prompt)

    def _call_claude(self, prompt: str) -> str:
        """
        Call Claude with the given prompt.

        Args:
            prompt: The prompt to send

        Returns:
            Response text from Claude
        """
        if self.config.backend == "claude-code":
            return self._call_claude_code(prompt)
        else:
            return self._call_anthropic_sdk(prompt)

    def _call_claude_code(self, prompt: str) -> str:
        """Call Claude Code CLI."""
        full_prompt = f"{self.system_prompt}\n\n---\n\n{prompt}"

        cmd = [
            "claude",
            "-p",
            "--output-format", "text",
        ]

        if self.config.model and self.config.model not in ["opus", "sonnet", "haiku"]:
            cmd.extend(["--model", self.config.model])
        elif self.config.model:
            cmd.extend(["--model", self.config.model])

        try:
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for analysis
                check=True
            )

            response = result.stdout.strip()
            if result.stderr:
                self.logger.debug(f"Claude Code stderr: {result.stderr}")

            return response

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code CLI timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Claude Code CLI failed: {e.stderr or str(e)}")

    def _call_anthropic_sdk(self, prompt: str) -> str:
        """Call Anthropic SDK."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _parse_tasks(self, analysis: str) -> List[ParsedTask]:
        """
        Parse tasks from Claude's analysis.

        Args:
            analysis: Raw analysis text from Claude

        Returns:
            List of parsed tasks
        """
        tasks = []

        # Try to extract JSON from the response
        json_content = self._extract_json(analysis)

        if not json_content:
            self.logger.warning("Could not extract JSON from analysis")
            return tasks

        try:
            data = json.loads(json_content)
            task_list = data.get("tasks", [])

            for task_data in task_list:
                priority = self._parse_priority(task_data.get("priority", 3))
                category = self._parse_category(task_data.get("category", "functional"))

                task = ParsedTask(
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    priority=priority,
                    category=category,
                    acceptance_criteria=task_data.get("acceptance_criteria", []),
                    test_steps=task_data.get("test_steps", []),
                    labels=task_data.get("labels", []),
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")

        return tasks

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from text that may contain markdown code blocks."""
        import re

        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # Try to find raw JSON object
        json_match = re.search(r'\{[\s\S]*"tasks"[\s\S]*\}', text)
        if json_match:
            return json_match.group(0)

        return None

    def _parse_priority(self, priority: Any) -> TaskPriority:
        """Parse priority value to TaskPriority enum."""
        if isinstance(priority, int):
            priority_map = {
                1: TaskPriority.URGENT,
                2: TaskPriority.HIGH,
                3: TaskPriority.NORMAL,
                4: TaskPriority.LOW
            }
            return priority_map.get(priority, TaskPriority.NORMAL)
        elif isinstance(priority, str):
            priority_lower = priority.lower()
            if "urgent" in priority_lower:
                return TaskPriority.URGENT
            elif "high" in priority_lower:
                return TaskPriority.HIGH
            elif "low" in priority_lower:
                return TaskPriority.LOW
        return TaskPriority.NORMAL

    def _parse_category(self, category: str) -> TaskCategory:
        """Parse category string to TaskCategory enum."""
        category_lower = category.lower()
        category_map = {
            "functional": TaskCategory.FUNCTIONAL,
            "style": TaskCategory.STYLE,
            "infrastructure": TaskCategory.INFRASTRUCTURE,
            "testing": TaskCategory.TESTING,
            "documentation": TaskCategory.DOCUMENTATION,
            "bugfix": TaskCategory.BUGFIX
        }
        return category_map.get(category_lower, TaskCategory.FUNCTIONAL)

    def _create_tasks(self, parsed_tasks: List[ParsedTask]) -> List[str]:
        """
        Create tasks in the state provider.

        Args:
            parsed_tasks: List of parsed tasks

        Returns:
            List of created task IDs
        """
        if not self.provider:
            raise RuntimeError("State provider not initialized")

        created_ids = []

        for i, parsed in enumerate(parsed_tasks):
            now = datetime.now()
            task = Task(
                id=f"task-{i+1}",  # Will be replaced by provider
                title=parsed.title,
                description=parsed.description,
                status=TaskStatus.TODO,
                priority=parsed.priority,
                category=parsed.category,
                acceptance_criteria=parsed.acceptance_criteria or [],
                test_steps=parsed.test_steps or [],
                labels=parsed.labels or [],
                created_at=now,
                updated_at=now
            )

            try:
                task_id = self.provider.create_task(task)
                created_ids.append(task_id)
                self.logger.info(f"Created task: {task_id} - {parsed.title}")
            except Exception as e:
                self.logger.error(f"Failed to create task '{parsed.title}': {e}")

        return created_ids

    def _create_meta_task(
        self,
        project_name: str,
        task_ids: List[str],
        analysis: str
    ) -> Optional[str]:
        """
        Create META tracking task.

        Args:
            project_name: Name of the project
            task_ids: List of created task IDs
            analysis: Raw analysis from Claude

        Returns:
            META task ID if created
        """
        if not self.provider:
            return None

        meta_description = f"""# META: {project_name}

## Project Tracking Issue

This is the META tracking issue for the {project_name} project.
Created by Initializer Agent on {datetime.now().strftime('%Y-%m-%d %H:%M')}.

### Statistics
- Total Tasks: {len(task_ids)}
- Created: {datetime.now().isoformat()}

### Task IDs
{chr(10).join(f'- {tid}' for tid in task_ids)}

### Session Log
| Session | Started | Ended | Tasks Completed | Notes |
|---------|---------|-------|-----------------|-------|
| 1 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | - | 0 | Initialization |

### Architecture Decisions
(To be updated by coding agents)

### Regression Status
- Status: Unknown
- Last Run: N/A

---

## Original Analysis

<details>
<summary>Click to expand</summary>

{analysis[:2000]}{'...' if len(analysis) > 2000 else ''}

</details>
"""

        now = datetime.now()
        meta_task = Task(
            id="meta",
            title=f"META: {project_name}",
            description=meta_description,
            status=TaskStatus.IN_PROGRESS,  # META is always in progress
            priority=TaskPriority.URGENT,
            category=TaskCategory.DOCUMENTATION,
            acceptance_criteria=[],
            test_steps=[],
            labels=["meta", "tracking"],
            created_at=now,
            updated_at=now
        )

        try:
            meta_id = self.provider.create_task(meta_task)
            self.logger.info(f"Created META task: {meta_id}")
            return meta_id
        except Exception as e:
            self.logger.error(f"Failed to create META task: {e}")
            return None

    def _write_project_state(
        self,
        project_name: str,
        project_dir: str,
        meta_task_id: Optional[str],
        task_ids: List[str]
    ) -> str:
        """
        Write project state marker file.

        Args:
            project_name: Name of the project
            project_dir: Project directory
            meta_task_id: META task ID
            task_ids: List of created task IDs

        Returns:
            Project ID
        """
        project_id = f"proj-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        state = {
            "project_id": project_id,
            "project_name": project_name,
            "initialized_at": datetime.now().isoformat(),
            "provider_type": self.config.state_provider_config.get("type", "file"),
            "meta_task_id": meta_task_id,
            "total_tasks": len(task_ids),
            "task_ids": task_ids,
            "sessions": [
                {
                    "session": 1,
                    "type": "initialization",
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "tasks_created": len(task_ids)
                }
            ]
        }

        state_file = Path(project_dir) / self.config.project_state_file
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        self.logger.info(f"Wrote project state to: {state_file}")
        return project_id

    def _calculate_task_breakdown(self, tasks: List[ParsedTask]) -> Dict[str, int]:
        """Calculate task breakdown by category."""
        breakdown = {}
        for task in tasks:
            cat = task.category.value
            breakdown[cat] = breakdown.get(cat, 0) + 1
        return breakdown

    def _calculate_priority_distribution(self, tasks: List[ParsedTask]) -> Dict[str, int]:
        """Calculate priority distribution."""
        distribution = {}
        for task in tasks:
            pri = task.priority.name
            distribution[pri] = distribution.get(pri, 0) + 1
        return distribution

    def check_initialized(self, project_dir: Optional[str] = None) -> bool:
        """
        Check if project is already initialized.

        Args:
            project_dir: Project directory to check

        Returns:
            True if project state file exists
        """
        project_dir = project_dir or os.getcwd()
        state_file = Path(project_dir) / self.config.project_state_file
        return state_file.exists()

    def get_project_state(self, project_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get existing project state.

        Args:
            project_dir: Project directory

        Returns:
            Project state dict if exists
        """
        project_dir = project_dir or os.getcwd()
        state_file = Path(project_dir) / self.config.project_state_file

        if not state_file.exists():
            return None

        with open(state_file, 'r') as f:
            return json.load(f)

    def get_status(self) -> Dict[str, Any]:
        """Get current initializer status."""
        return {
            "state": self.state.value,
            "backend": self.config.backend,
            "model": self.config.model,
            "provider": self.config.state_provider_config.get("type", "unknown")
        }


def create_initializer(config_path: str = ".ai-agents/config.yml") -> ProjectInitializer:
    """
    Create a project initializer from config file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configured ProjectInitializer
    """
    config = InitializerConfig.from_yaml(config_path)
    return ProjectInitializer(config)
