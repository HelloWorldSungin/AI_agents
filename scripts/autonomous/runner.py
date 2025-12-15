"""
Autonomous Runner for AI_agents

Executes development tasks autonomously using the Anthropic Claude API.
Integrates with state providers for task management and execution control
for safety checkpoints.

Usage:
    from scripts.autonomous.runner import AutonomousRunner

    config = {...}
    runner = AutonomousRunner(config)
    runner.start()
"""

import os
import sys
import json
import yaml
import time
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import subprocess
import shutil

# Check for Claude Code CLI
CLAUDE_CODE_AVAILABLE = shutil.which("claude") is not None

# Optional: Check for Anthropic SDK (as fallback)
try:
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_SDK_AVAILABLE = False

from scripts.state_providers import get_provider, Task, TaskStatus, StateProvider
from scripts.execution.checkpoint_manager import (
    CheckpointManager, CheckpointType, CheckpointContext, ApprovalResult, ApprovalAction
)
from scripts.execution.turn_counter import TurnCounter
from scripts.progress.progress_tracker import ProgressTracker


class RunnerState(Enum):
    """State of the autonomous runner"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class RunnerConfig:
    """Configuration for the autonomous runner"""
    # Execution backend: "claude-code" (subscription) or "anthropic-sdk" (API)
    backend: str = "claude-code"

    # Model to use (applies to both backends)
    model: str = "opus"
    max_tokens: int = 8192

    # API key (only needed for anthropic-sdk backend)
    api_key_env: str = "ANTHROPIC_API_KEY"

    # System prompt
    system_prompt_path: str = "prompts/roles/software-developer.md"

    # Execution settings
    max_turns_per_task: int = 50
    max_tasks_per_session: int = 10
    pause_between_tasks: int = 5  # seconds

    # State provider
    state_provider_config: Dict[str, Any] = field(default_factory=dict)

    # Execution mode (autonomous, interactive, supervised)
    execution_mode: str = "autonomous"

    # Checkpoint settings
    checkpoint_config: Dict[str, Any] = field(default_factory=dict)

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Safety
    rate_limit_rpm: int = 50  # requests per minute
    cost_limit_per_session: float = 10.0  # USD

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunnerConfig":
        """Create config from dictionary"""
        # Get autonomous section for nested config
        autonomous = data.get("autonomous", {})

        return cls(
            backend=autonomous.get("backend", data.get("backend", "claude-code")),
            model=autonomous.get("model", data.get("model", "claude-sonnet-4-20250514")),
            max_tokens=autonomous.get("max_tokens", data.get("max_tokens", 8192)),
            api_key_env=autonomous.get("api_key_env", data.get("api_key_env", "ANTHROPIC_API_KEY")),
            system_prompt_path=autonomous.get("system_prompt_path", data.get("system_prompt_path", "prompts/roles/software-developer.md")),
            max_turns_per_task=autonomous.get("max_turns_per_task", data.get("max_turns_per_task", 50)),
            max_tasks_per_session=autonomous.get("max_tasks_per_session", data.get("max_tasks_per_session", 10)),
            pause_between_tasks=autonomous.get("pause_between_tasks", data.get("pause_between_tasks", 5)),
            state_provider_config=data.get("state_provider", {}),
            execution_mode=data.get("execution", {}).get("mode", "autonomous"),
            checkpoint_config=data.get("execution", {}).get("checkpoints", {}),
            log_level=autonomous.get("log_level", data.get("log_level", "INFO")),
            log_file=autonomous.get("log_file", data.get("log_file")),
            rate_limit_rpm=autonomous.get("rate_limit_rpm", data.get("rate_limit_rpm", 50)),
            cost_limit_per_session=autonomous.get("cost_limit_per_session", data.get("cost_limit_per_session", 10.0))
        )

    @classmethod
    def from_yaml(cls, path: str) -> "RunnerConfig":
        """Load config from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)


@dataclass
class TaskResult:
    """Result of executing a task"""
    task_id: str
    success: bool
    turns_used: int
    output: str
    error: Optional[str] = None
    files_changed: List[str] = field(default_factory=list)
    tests_passed: Optional[bool] = None


class AutonomousRunner:
    """
    Autonomous runner for AI development tasks.

    This runner:
    1. Fetches tasks from a state provider (Linear, GitHub, File)
    2. Executes each task using Claude API
    3. Updates task status based on results
    4. Respects checkpoints and execution modes
    5. Tracks progress and sends notifications
    """

    def __init__(self, config: RunnerConfig):
        """
        Initialize the autonomous runner.

        Args:
            config: Runner configuration
        """
        self.config = config
        self.state = RunnerState.IDLE

        # Setup logging
        self._setup_logging()

        # Initialize backend
        self.client = None  # Only used for anthropic-sdk backend

        if config.backend == "claude-code":
            # Use Claude Code CLI (subscription-based)
            if not CLAUDE_CODE_AVAILABLE:
                raise RuntimeError(
                    "Claude Code CLI not found. "
                    "Install from: https://claude.ai/code or ensure 'claude' is in PATH"
                )
            self.logger.info("Using Claude Code CLI backend (subscription)")
        elif config.backend == "anthropic-sdk":
            # Use Anthropic SDK (API-based)
            if not ANTHROPIC_SDK_AVAILABLE:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
            api_key = os.environ.get(config.api_key_env)
            if not api_key:
                raise ValueError(f"API key not found in environment variable: {config.api_key_env}")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.logger.info("Using Anthropic SDK backend (API)")
        else:
            raise ValueError(f"Unknown backend: {config.backend}. Use 'claude-code' or 'anthropic-sdk'")

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Initialize state provider
        self.provider: Optional[StateProvider] = None
        self._init_provider()

        # Initialize execution components
        self.checkpoint_manager = CheckpointManager({
            "mode": config.execution_mode,
            "checkpoints": config.checkpoint_config
        })
        self.turn_counter = TurnCounter()
        self.progress_tracker: Optional[ProgressTracker] = None

        # Session tracking
        self.session_id: Optional[str] = None
        self.tasks_completed = 0
        self.total_cost = 0.0
        self.last_request_time = 0.0

        # Conversation history per task
        self.messages: List[Dict[str, Any]] = []

        # State file for persistence
        self.state_file = Path(".ai-agents/state/runner-state.json")

        # Signal handling for graceful shutdown
        self._setup_signal_handlers()

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
        self.logger = logging.getLogger("autonomous-runner")

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_path = Path(self.config.system_prompt_path)

        if not prompt_path.exists():
            self.logger.warning(f"System prompt not found: {prompt_path}")
            return self._default_system_prompt()

        with open(prompt_path, 'r') as f:
            content = f.read()

        # Add autonomous execution context
        autonomous_context = """

## Autonomous Execution Context

You are running in autonomous mode. This means:

1. **Task-Driven**: You receive structured tasks with acceptance criteria
2. **Self-Directed**: Complete tasks without human intervention
3. **Result-Oriented**: Focus on meeting acceptance criteria
4. **Test-Verified**: Run tests to verify your work

### Task Execution Protocol

For each task:
1. Understand the acceptance criteria
2. Plan your approach
3. Implement the solution
4. Run tests to verify
5. Report completion with results

### Communication Format

When completing a task, respond with:
```
## Task Complete: [TASK_ID]

### Changes Made:
- [List of changes]

### Files Modified:
- [List of files]

### Test Results:
- [Test output or "Tests passed"]

### Notes:
- [Any important observations]
```

When encountering issues, respond with:
```
## Task Blocked: [TASK_ID]

### Issue:
[Description of the blocker]

### Attempted Solutions:
- [What you tried]

### Help Needed:
[What assistance would help]
```
"""
        return content + autonomous_context

    def _default_system_prompt(self) -> str:
        """Return default system prompt if file not found."""
        return """You are an expert software developer working autonomously on development tasks.

You receive structured tasks with acceptance criteria and must complete them without human intervention.

For each task:
1. Analyze the requirements
2. Plan your implementation
3. Write the code
4. Run tests to verify
5. Report your results

Always be thorough, test your work, and report both successes and failures clearly."""

    def _init_provider(self):
        """Initialize state provider."""
        try:
            self.provider = get_provider()
            self.logger.info(f"Initialized state provider")
        except Exception as e:
            self.logger.error(f"Failed to initialize state provider: {e}")
            raise

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def handle_signal(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    def _rate_limit(self):
        """Enforce rate limiting."""
        if self.config.rate_limit_rpm <= 0:
            return

        min_interval = 60.0 / self.config.rate_limit_rpm
        elapsed = time.time() - self.last_request_time

        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _check_cost_limit(self) -> bool:
        """Check if cost limit exceeded."""
        if self.config.cost_limit_per_session <= 0:
            return True
        return self.total_cost < self.config.cost_limit_per_session

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model and tokens."""
        # Pricing as of 2024 (approximate)
        pricing = {
            "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
            "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        }

        model_pricing = pricing.get(self.config.model, {"input": 3.0, "output": 15.0})
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

        return input_cost + output_cost

    def _save_state(self):
        """Save runner state for persistence."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "state": self.state.value,
            "session_id": self.session_id,
            "tasks_completed": self.tasks_completed,
            "total_cost": self.total_cost,
            "checkpoint_manager_turn": self.checkpoint_manager.current_turn,
            "updated_at": datetime.now().isoformat()
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> bool:
        """Load runner state from file."""
        if not self.state_file.exists():
            return False

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.session_id = state.get("session_id")
            self.tasks_completed = state.get("tasks_completed", 0)
            self.total_cost = state.get("total_cost", 0.0)
            self.checkpoint_manager.current_turn = state.get("checkpoint_manager_turn", 0)

            self.logger.info(f"Resumed from state: session={self.session_id}, tasks={self.tasks_completed}")
            return True
        except Exception as e:
            self.logger.warning(f"Could not load state: {e}")
            return False

    def start(self, resume: bool = False):
        """
        Start the autonomous runner.

        Args:
            resume: If True, try to resume from previous state
        """
        if self.state == RunnerState.RUNNING:
            self.logger.warning("Runner already running")
            return

        self.logger.info("Starting autonomous runner...")

        # Try to resume if requested
        if resume:
            self._load_state()

        # Start new session if needed
        if not self.session_id:
            self.session_id = self.provider.start_session() if self.provider else datetime.now().strftime("%Y%m%d-%H%M%S")
            self.tasks_completed = 0
            self.total_cost = 0.0

        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(self.provider)
        self.progress_tracker.start_tracking(self.session_id)

        self.state = RunnerState.RUNNING
        self._save_state()

        try:
            self._run_loop()
        except Exception as e:
            self.logger.error(f"Runner error: {e}")
            self.state = RunnerState.ERROR
            self._save_state()
            raise
        finally:
            self._cleanup()

    def stop(self):
        """Stop the runner gracefully."""
        self.logger.info("Stopping runner...")
        self.state = RunnerState.STOPPED
        self._save_state()

    def pause(self):
        """Pause the runner."""
        self.logger.info("Pausing runner...")
        self.state = RunnerState.PAUSED
        self._save_state()

    def _cleanup(self):
        """Cleanup after run."""
        if self.progress_tracker:
            self.progress_tracker.stop_tracking(
                f"Session complete. Tasks: {self.tasks_completed}, Cost: ${self.total_cost:.2f}"
            )

        if self.provider and self.session_id:
            self.provider.end_session(
                f"Completed {self.tasks_completed} tasks. Total cost: ${self.total_cost:.2f}"
            )

    def _run_loop(self):
        """Main execution loop."""
        while self.state == RunnerState.RUNNING:
            # Check limits
            if not self._check_cost_limit():
                self.logger.warning(f"Cost limit reached: ${self.total_cost:.2f}")
                break

            if self.tasks_completed >= self.config.max_tasks_per_session:
                self.logger.info(f"Task limit reached: {self.tasks_completed}")
                break

            # Get next task
            task = self._get_next_task()
            if not task:
                self.logger.info("No more tasks available")
                break

            self.logger.info(f"Starting task: {task.id} - {task.title}")

            # Execute task
            result = self._execute_task(task)

            # Update task status
            self._update_task_status(task, result)

            # Track progress
            if result.success:
                self.tasks_completed += 1
                if self.progress_tracker:
                    self.progress_tracker.task_completed(task.id, task.title)

            self._save_state()

            # Pause between tasks
            if self.state == RunnerState.RUNNING:
                time.sleep(self.config.pause_between_tasks)

        self.logger.info(f"Run loop complete. Tasks: {self.tasks_completed}, Cost: ${self.total_cost:.2f}")

    def _get_next_task(self) -> Optional[Task]:
        """Get the next task to execute."""
        if not self.provider:
            return None

        # Get tasks in priority order
        tasks = self.provider.get_tasks(status=TaskStatus.TODO)

        if not tasks:
            # Try in_progress tasks (might be resuming)
            tasks = self.provider.get_tasks(status=TaskStatus.IN_PROGRESS)

        if not tasks:
            return None

        # Sort by phase order, then task number, then priority
        # Extracts phase/task from titles like "[PROJECT-1.2]", "1.2:", "Phase 1.2"
        import re

        def sort_key(task):
            # Pattern 1: META tasks always first
            if 'META' in task.title.upper():
                return (0, 0, '', task.priority.value)

            # Pattern 2: [PREFIX-1.2a] format (any project prefix, optional letter suffix)
            # Matches: [AUTH-1.2], [CI-2.3a], [API-1.5b], etc.
            match = re.search(r'\[\w+-(\d+)\.(\d+)([a-z]?)\]', task.title)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 3: Standalone "1.2a" or "1.2:" at start of title
            # Matches: "1.2: Implement feature", "1.2a - Setup database"
            match = re.search(r'^(\d+)\.(\d+)([a-z]?)[\s:\-]', task.title)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 4: "Phase X.Y" or "Task X.Y" anywhere in title
            match = re.search(r'(?:phase|task)\s*(\d+)\.(\d+)([a-z]?)', task.title, re.IGNORECASE)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 5: Linear-style ID with number - sort by ID number
            id_match = re.search(r'[A-Z]+-(\d+)', task.id)
            if id_match:
                task_id = int(id_match.group(1))
                return (99, task_id, '', task.priority.value)

            # Fallback: just priority
            return (999, 999, '', task.priority.value)

        tasks.sort(key=sort_key)

        # Cross-phase dependency checking
        # Ensure prerequisite tasks are complete before starting dependent tasks
        # For phase-ordered tasks ([PREFIX-X.Y]):
        # 1. All earlier tasks in the same phase must be DONE
        # 2. All tasks in earlier phases must be DONE
        all_tasks = self.provider.get_tasks()  # Get all tasks to check dependencies

        def extract_phase_task(title: str) -> Optional[tuple]:
            """Extract (phase, task_num, subtask) from title, or None if not phased."""
            # Pattern: [PREFIX-X.Ya] format (with optional letter suffix)
            match = re.search(r'\[\w+-(\d+)\.(\d+)([a-z]?)\]', title)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)
            # Pattern: X.Ya: at start
            match = re.search(r'^(\d+)\.(\d+)([a-z]?)[\s:\-]', title)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)
            # Pattern: Phase X.Y or Task X.Y
            match = re.search(r'(?:phase|task)\s*(\d+)\.(\d+)([a-z]?)', title, re.IGNORECASE)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)
            return None

        for candidate in tasks:
            # Extract phase and task number from candidate
            candidate_pt = extract_phase_task(candidate.title)
            if not candidate_pt:
                # Not a phased task, no dependency check needed
                return candidate

            phase, task_num, subtask = candidate_pt

            # Check dependencies
            blocking_tasks = []
            for other_task in all_tasks:
                if other_task.id == candidate.id:
                    continue  # Skip self

                other_pt = extract_phase_task(other_task.title)
                if not other_pt:
                    continue

                other_phase, other_task_num, other_subtask = other_pt

                # Block if:
                # 1. Earlier phase (any task not DONE blocks this phase)
                # 2. Same phase, earlier task number
                # 3. Same phase and task number, earlier subtask (a < b < c)
                is_blocker = False
                if other_phase < phase:
                    is_blocker = True  # Earlier phase must be complete
                elif other_phase == phase and other_task_num < task_num:
                    is_blocker = True  # Earlier task in same phase
                elif other_phase == phase and other_task_num == task_num and other_subtask < subtask:
                    is_blocker = True  # Earlier subtask (1.2a blocks 1.2b)

                if is_blocker and other_task.status != TaskStatus.DONE:
                    blocking_tasks.append(f"{other_task.id} ({other_task.status.value})")

            if not blocking_tasks:
                # No blockers, this task is ready
                return candidate
            else:
                # Log why task was skipped
                blockers_str = ', '.join(blocking_tasks[:5])
                if len(blocking_tasks) > 5:
                    blockers_str += '...'
                self.logger.info(f"Skipping {candidate.id} - blocked by: {blockers_str}")

        # All tasks are blocked by dependencies
        self.logger.warning("No tasks ready - all TODO tasks blocked by dependencies")
        return None

    def _execute_task(self, task: Task) -> TaskResult:
        """
        Execute a single task.

        Args:
            task: Task to execute

        Returns:
            TaskResult with execution results
        """
        # Mark task as in progress
        if self.provider:
            self.provider.update_task(task.id, {"status": TaskStatus.IN_PROGRESS})

        if self.progress_tracker:
            self.progress_tracker.task_started(task.id, task.title)

        # Reset conversation for this task
        self.messages = []

        # Build initial prompt
        initial_prompt = self._build_task_prompt(task)

        turns = 0
        output_parts = []
        files_changed = []
        error = None
        success = False

        try:
            while turns < self.config.max_turns_per_task:
                turns += 1
                self.checkpoint_manager.increment_turn()
                self.turn_counter.increment()

                # Check for checkpoints
                if self._should_checkpoint():
                    checkpoint_result = self._handle_checkpoint(task)
                    if checkpoint_result.action == ApprovalAction.ABORT:
                        error = "Aborted at checkpoint"
                        break
                    elif checkpoint_result.action == ApprovalAction.PAUSE:
                        self.pause()
                        break

                # Rate limit
                self._rate_limit()

                # Build message for this turn
                if turns == 1:
                    self.messages.append({"role": "user", "content": initial_prompt})

                # Call appropriate backend
                self.logger.debug(f"Task {task.id}: Turn {turns}")

                if self.config.backend == "claude-code":
                    # Use Claude Code CLI
                    assistant_message = self._call_claude_code(self.messages[-1]["content"])
                else:
                    # Use Anthropic SDK
                    response = self.client.messages.create(
                        model=self.config.model,
                        max_tokens=self.config.max_tokens,
                        system=self.system_prompt,
                        messages=self.messages
                    )

                    # Track cost for SDK backend
                    self.total_cost += self._estimate_cost(
                        response.usage.input_tokens,
                        response.usage.output_tokens
                    )

                    assistant_message = response.content[0].text

                output_parts.append(assistant_message)

                # Add to conversation
                self.messages.append({"role": "assistant", "content": assistant_message})

                # Check for completion
                if self._is_task_complete(assistant_message):
                    success = True
                    files_changed = self._extract_files_changed(assistant_message)
                    break

                # Check for blocker
                if self._is_task_blocked(assistant_message):
                    error = self._extract_blocker(assistant_message)
                    break

                # Continue conversation if needed
                follow_up = self._generate_follow_up(assistant_message, task)
                if follow_up:
                    self.messages.append({"role": "user", "content": follow_up})
                else:
                    # No follow-up needed, consider complete
                    success = True
                    break

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Claude Code CLI error: {e}")
            error = str(e)
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            error = str(e)

        return TaskResult(
            task_id=task.id,
            success=success,
            turns_used=turns,
            output="\n\n---\n\n".join(output_parts),
            error=error,
            files_changed=files_changed
        )

    def _build_task_prompt(self, task: Task) -> str:
        """Build the initial prompt for a task."""
        prompt_parts = [
            f"# Task: {task.title}",
            f"**ID:** {task.id}",
            f"**Priority:** {task.priority.name}",
            f"**Category:** {task.category.value}",
            "",
            "## Description",
            task.description,
        ]

        if task.acceptance_criteria:
            prompt_parts.extend([
                "",
                "## Acceptance Criteria",
                *[f"- [ ] {criterion}" for criterion in task.acceptance_criteria]
            ])

        if task.test_steps:
            prompt_parts.extend([
                "",
                "## Test Steps",
                *[f"{i+1}. {step}" for i, step in enumerate(task.test_steps)]
            ])

        prompt_parts.extend([
            "",
            "---",
            "",
            "Please complete this task. Remember to:",
            "1. Implement the required changes",
            "2. Run tests to verify your work",
            "3. Report completion with the standard format",
        ])

        return "\n".join(prompt_parts)

    def _should_checkpoint(self) -> bool:
        """Check if a checkpoint should be triggered."""
        context = CheckpointContext(
            turn_number=self.checkpoint_manager.current_turn
        )
        return self.checkpoint_manager.should_checkpoint(
            CheckpointType.TURN_INTERVAL, context
        )

    def _handle_checkpoint(self, task: Task) -> ApprovalResult:
        """Handle a checkpoint."""
        context = CheckpointContext(
            task_id=task.id,
            task_title=task.title,
            turn_number=self.checkpoint_manager.current_turn,
            progress_summary={
                "tasks_completed": self.tasks_completed,
                "total_cost": f"${self.total_cost:.2f}"
            }
        )

        checkpoint = self.checkpoint_manager.create_checkpoint(
            CheckpointType.TURN_INTERVAL, context
        )

        if self.progress_tracker:
            self.progress_tracker.checkpoint(
                CheckpointType.TURN_INTERVAL.value,
                {"task_id": task.id, "turn": self.checkpoint_manager.current_turn}
            )

        return self.checkpoint_manager.wait_for_approval(checkpoint)

    def _is_task_complete(self, response: str) -> bool:
        """Check if task is complete based on response."""
        complete_indicators = [
            "## Task Complete",
            "Task completed",
            "Successfully completed",
            "Implementation complete",
            "All acceptance criteria met"
        ]
        return any(indicator.lower() in response.lower() for indicator in complete_indicators)

    def _is_task_blocked(self, response: str) -> bool:
        """Check if task is blocked based on response."""
        blocked_indicators = [
            "## Task Blocked",
            "Task blocked",
            "Cannot proceed",
            "Need help",
            "Blocked by"
        ]
        return any(indicator.lower() in response.lower() for indicator in blocked_indicators)

    def _extract_blocker(self, response: str) -> str:
        """Extract blocker description from response."""
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if 'blocked' in line.lower() or 'issue' in line.lower():
                # Return next few lines as blocker description
                return '\n'.join(lines[i:min(i+5, len(lines))])
        return "Unknown blocker"

    def _extract_files_changed(self, response: str) -> List[str]:
        """Extract list of changed files from response."""
        files = []
        lines = response.split('\n')
        in_files_section = False

        for line in lines:
            if 'files modified' in line.lower() or 'files changed' in line.lower():
                in_files_section = True
                continue

            if in_files_section:
                if line.strip().startswith('-'):
                    file_path = line.strip()[1:].strip()
                    if file_path:
                        files.append(file_path)
                elif line.strip() and not line.startswith(' '):
                    in_files_section = False

        return files

    def _generate_follow_up(self, response: str, task: Task) -> Optional[str]:
        """Generate follow-up prompt if needed."""
        # Check if agent needs more information
        if '?' in response and any(q in response.lower() for q in ['should i', 'would you like', 'do you want']):
            # Agent is asking a question - in autonomous mode, give direction
            return "Please proceed with the most appropriate approach based on best practices."

        # Check if tests need to be run
        if 'run tests' not in response.lower() and 'test results' not in response.lower():
            if not self._is_task_complete(response):
                return "Please run the relevant tests and report the results."

        return None

    def _call_claude_code(self, prompt: str) -> str:
        """
        Call Claude Code CLI with the given prompt.

        Uses the Claude Code subscription instead of Anthropic API.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Response text from Claude
        """
        # Create a temporary file for the prompt (Claude Code can read from file)
        import tempfile

        # Prepare the full prompt with system context
        full_prompt = f"""
{self.system_prompt}

---

{prompt}
"""

        # Use Claude Code in print mode (-p) for non-interactive output
        # The --dangerously-skip-permissions flag allows automated execution
        cmd = [
            "claude",
            "-p",  # Print mode - non-interactive, outputs response
            "--output-format", "text",  # Plain text output
        ]

        # Add model if specified and different from default
        if self.config.model and self.config.model != "claude-sonnet-4-20250514":
            cmd.extend(["--model", self.config.model])

        try:
            # Run Claude Code CLI with prompt via stdin
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per call
                check=True
            )

            response = result.stdout.strip()

            # Log any stderr (warnings, etc.)
            if result.stderr:
                self.logger.debug(f"Claude Code stderr: {result.stderr}")

            return response

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code CLI timed out after 5 minutes")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Claude Code CLI failed: {error_msg}")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude Code CLI not found. "
                "Ensure 'claude' is installed and in your PATH"
            )

    def _update_task_status(self, task: Task, result: TaskResult):
        """Update task status based on result."""
        if not self.provider:
            return

        if result.success:
            self.provider.update_task(task.id, {
                "status": TaskStatus.DONE,
                "metadata": {
                    "turns_used": result.turns_used,
                    "files_changed": result.files_changed,
                    "completed_at": datetime.now().isoformat()
                }
            })
        elif result.error:
            if "blocker" in result.error.lower() or "blocked" in result.error.lower():
                self.provider.update_task(task.id, {
                    "status": TaskStatus.BLOCKED,
                    "metadata": {
                        "blocker": result.error,
                        "turns_used": result.turns_used
                    }
                })
                if self.progress_tracker:
                    self.progress_tracker.task_blocked(task.id, result.error)
            else:
                # Keep in progress for retry
                self.provider.update_task(task.id, {
                    "metadata": {
                        "last_error": result.error,
                        "turns_used": result.turns_used
                    }
                })

    def get_status(self) -> Dict[str, Any]:
        """Get current runner status."""
        return {
            "state": self.state.value,
            "session_id": self.session_id,
            "tasks_completed": self.tasks_completed,
            "total_cost": f"${self.total_cost:.2f}",
            "current_turn": self.checkpoint_manager.current_turn,
            "model": self.config.model,
            "execution_mode": self.config.execution_mode
        }


def create_runner(config_path: str = ".ai-agents/config.yml") -> AutonomousRunner:
    """
    Create an autonomous runner from config file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configured AutonomousRunner
    """
    config = RunnerConfig.from_yaml(config_path)
    return AutonomousRunner(config)
