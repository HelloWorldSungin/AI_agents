"""
Autonomous Runner (SDK-Based) for AI_agents

Executes development tasks autonomously using the Claude Code SDK.
Provides real-time streaming, tool visibility, and MCP integration.

Key Benefits over CLI runner:
- ✅ Real-time async streaming (no blocking)
- ✅ Live progress updates posted to Linear
- ✅ Tool use visibility in real-time
- ✅ Direct Linear MCP integration
- ✅ Better error messages
- ✅ No 30-minute timeout limits
- ✅ Stop-on-failure to prevent cascading errors

Usage:
    from scripts.autonomous.runner_sdk import AutonomousRunnerSDK

    config = {...}
    runner = AutonomousRunnerSDK(config)
    await runner.start()  # Note: async!
"""

import os
import sys
import json
import yaml
import asyncio
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Claude Code SDK imports
try:
    from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
    from claude_code_sdk.types import AssistantMessage, UserMessage, TextBlock, ToolUseBlock
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

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
    """Configuration for the SDK-based autonomous runner"""
    # Model to use
    model: str = "claude-opus-4-5-20251101"
    max_tokens: int = 8192

    # OAuth token for SDK authentication
    oauth_token_env: str = "CLAUDE_CODE_OAUTH_TOKEN"

    # Linear API key (for MCP)
    linear_api_key_env: str = "LINEAR_API_KEY"

    # System prompt
    system_prompt_path: str = "prompts/roles/software-developer.md"

    # Execution settings
    max_turns_per_task: int = 150  # Increased for complex tasks
    max_tasks_per_session: int = 10
    pause_between_tasks: int = 2  # seconds

    # Project directory
    project_dir: str = "."

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunnerConfig":
        """Create config from dictionary"""
        autonomous = data.get("autonomous", {})

        return cls(
            model=autonomous.get("model", "claude-opus-4-5-20251101"),
            max_tokens=autonomous.get("max_tokens", 8192),
            oauth_token_env=autonomous.get("oauth_token_env", "CLAUDE_CODE_OAUTH_TOKEN"),
            linear_api_key_env=autonomous.get("linear_api_key_env", "LINEAR_API_KEY"),
            system_prompt_path=autonomous.get("system_prompt_path", "prompts/roles/software-developer.md"),
            max_turns_per_task=autonomous.get("max_turns_per_task", 150),
            max_tasks_per_session=autonomous.get("max_tasks_per_session", 10),
            pause_between_tasks=autonomous.get("pause_between_tasks", 2),
            project_dir=autonomous.get("project_dir", "."),
            state_provider_config=data.get("state_provider", {}),
            execution_mode=data.get("execution", {}).get("mode", "autonomous"),
            checkpoint_config=data.get("execution", {}).get("checkpoints", {}),
            log_level=autonomous.get("log_level", "INFO"),
            log_file=autonomous.get("log_file"),
            rate_limit_rpm=autonomous.get("rate_limit_rpm", 50)
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


class AutonomousRunnerSDK:
    """
    SDK-based autonomous runner for AI development tasks.

    Key improvements over CLI runner:
    - Async streaming for real-time updates
    - Tool visibility for debugging
    - MCP integration for Linear access
    - Better error handling
    - Stop-on-failure pattern
    """

    def __init__(self, config: RunnerConfig):
        """
        Initialize the SDK-based autonomous runner.

        Args:
            config: Runner configuration
        """
        if not SDK_AVAILABLE:
            raise ImportError(
                "claude-code-sdk not installed. "
                "Install with: pip install claude-code-sdk>=0.0.25"
            )

        self.config = config
        self.state = RunnerState.IDLE

        # Setup logging
        self._setup_logging()

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # SDK client (created per task)
        self.sdk_client: Optional[ClaudeSDKClient] = None

        # Initialize state provider
        self.provider: Optional[StateProvider] = None
        try:
            self.provider = get_provider(config.state_provider_config)
            self.logger.info(f"Using state provider: {type(self.provider).__name__}")
        except Exception as e:
            self.logger.error(f"Could not initialize state provider: {e}")

        # Session tracking
        self.session_id: Optional[str] = None
        self.tasks_completed: int = 0

        # Execution control
        self.checkpoint_manager = CheckpointManager(
            config.checkpoint_config,
            mode=config.execution_mode
        )
        self.turn_counter = TurnCounter()

        # Progress tracking
        self.progress_tracker: Optional[ProgressTracker] = None

        # State file
        self.state_file = Path(".ai-agents/state/runner_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Signal handlers
        import signal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Setup logging configuration."""
        self.logger = logging.getLogger("AutonomousRunnerSDK")
        self.logger.setLevel(getattr(logging, self.config.log_level))

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_path = Path(self.config.system_prompt_path)

        if not prompt_path.exists():
            self.logger.warning(f"System prompt not found: {prompt_path}")
            return "You are a helpful AI assistant for software development."

        with open(prompt_path, 'r') as f:
            return f.read()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def _save_state(self):
        """Save current state to file."""
        state = {
            "session_id": self.session_id,
            "tasks_completed": self.tasks_completed,
            "checkpoint_manager_turn": self.checkpoint_manager.current_turn,
            "timestamp": datetime.now().isoformat()
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> bool:
        """Load state from file. Returns True if successful."""
        if not self.state_file.exists():
            return False

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.session_id = state.get("session_id")
            self.tasks_completed = state.get("tasks_completed", 0)
            self.checkpoint_manager.current_turn = state.get("checkpoint_manager_turn", 0)

            self.logger.info(f"Resumed from state: session={self.session_id}, tasks={self.tasks_completed}")
            return True
        except Exception as e:
            self.logger.warning(f"Could not load state: {e}")
            return False

    async def start(self, resume: bool = False):
        """
        Start the autonomous runner.

        Args:
            resume: If True, try to resume from previous state
        """
        if self.state == RunnerState.RUNNING:
            self.logger.warning("Runner already running")
            return

        self.logger.info("Starting SDK-based autonomous runner...")

        # Try to resume if requested
        if resume:
            self._load_state()

        # Start new session if needed
        if not self.session_id:
            self.session_id = self.provider.start_session() if self.provider else datetime.now().strftime("%Y%m%d-%H%M%S")
            self.tasks_completed = 0

        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(self.provider)
        self.progress_tracker.start_tracking(self.session_id)

        self.state = RunnerState.RUNNING
        self._save_state()

        try:
            await self._run_loop()
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
                f"Session complete. Tasks: {self.tasks_completed}"
            )

        if self.provider and self.session_id:
            self.provider.end_session(
                f"Completed {self.tasks_completed} tasks"
            )

    async def _run_loop(self):
        """Main execution loop (async)."""
        while self.state == RunnerState.RUNNING:
            if self.tasks_completed >= self.config.max_tasks_per_session:
                self.logger.info(f"Task limit reached: {self.tasks_completed}")
                break

            # Get next task
            task = self._get_next_task()
            if not task:
                self.logger.info("No more tasks available")
                break

            self.logger.info(f"Starting task: {task.id} - {task.title}")

            # Execute task (async)
            result = await self._execute_task(task)

            # Update task status
            self._update_task_status(task, result)

            # CRITICAL: Stop on failure to prevent dependent tasks from running
            if result.success:
                self.tasks_completed += 1
                if self.progress_tracker:
                    self.progress_tracker.task_completed(task.id, task.title)
                self.logger.info(f"Task {task.id} completed successfully")
            else:
                # Stop runner immediately when any task fails
                self.logger.error(f"Task {task.id} failed: {result.error}")
                self.logger.error("Stopping runner - cannot proceed with failed task")
                self.state = RunnerState.ERROR
                break  # Exit loop immediately

            self._save_state()

            # Pause between tasks
            if self.state == RunnerState.RUNNING:
                await asyncio.sleep(self.config.pause_between_tasks)

        self.logger.info(f"Run loop complete. Tasks: {self.tasks_completed}")

    def _get_next_task(self) -> Optional[Task]:
        """Get the next task to execute (with phase-aware sorting and dependency checking)."""
        if not self.provider:
            return None

        # Get tasks in TODO status
        tasks = self.provider.get_tasks(status=TaskStatus.TODO)

        if not tasks:
            # Try in_progress tasks (might be resuming)
            tasks = self.provider.get_tasks(status=TaskStatus.IN_PROGRESS)

        if not tasks:
            return None

        # Sort by phase order, then task number, then priority
        def sort_key(task):
            # Pattern 1: META tasks always first
            if 'META' in task.title.upper():
                return (0, 0, '', task.priority.value)

            # Pattern 2: [PREFIX-1.2a] format (any project prefix, optional letter suffix)
            match = re.search(r'\[\w+-(\d+)\.(\d+)([a-z]?)\]', task.title)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 3: Standalone "1.2a" or "1.2:" at start of title
            match = re.search(r'^(\d+)\.(\d+)([a-z]?)[\s:\-]', task.title)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 4: "Phase X.Y" or "Task X.Y"
            match = re.search(r'(?:phase|task)\s*(\d+)\.(\d+)([a-z]?)', task.title, re.IGNORECASE)
            if match:
                phase = int(match.group(1))
                task_num = int(match.group(2))
                subtask = match.group(3) if match.group(3) else ''
                return (phase, task_num, subtask, task.priority.value)

            # Pattern 5: Linear-style ID
            id_match = re.search(r'[A-Z]+-(\d+)', task.id)
            if id_match:
                task_id = int(id_match.group(1))
                return (99, task_id, '', task.priority.value)

            # Fallback
            return (999, 999, '', task.priority.value)

        tasks.sort(key=sort_key)

        # Cross-phase dependency checking
        all_tasks = self.provider.get_tasks()

        def extract_phase_task(title: str) -> Optional[tuple]:
            """Extract (phase, task_num, subtask) from title."""
            match = re.search(r'\[\w+-(\d+)\.(\d+)([a-z]?)\]', title)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)

            match = re.search(r'^(\d+)\.(\d+)([a-z]?)[\s:\-]', title)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)

            match = re.search(r'(?:phase|task)\s*(\d+)\.(\d+)([a-z]?)', title, re.IGNORECASE)
            if match:
                subtask = match.group(3) if match.group(3) else ''
                return (int(match.group(1)), int(match.group(2)), subtask)

            return None

        # Find first task that's not blocked by dependencies
        for candidate in tasks:
            candidate_pt = extract_phase_task(candidate.title)
            if not candidate_pt:
                # Not a phased task, can proceed
                return candidate

            phase, task_num, subtask = candidate_pt

            # Check for blocking tasks
            blocking_tasks = []
            for other_task in all_tasks:
                if other_task.id == candidate.id:
                    continue

                other_pt = extract_phase_task(other_task.title)
                if not other_pt:
                    continue

                other_phase, other_task_num, other_subtask = other_pt

                # Block if:
                # 1. Earlier phase not done
                # 2. Same phase, earlier task not done
                # 3. Same task, earlier subtask not done
                is_blocker = False
                if other_phase < phase:
                    is_blocker = True
                elif other_phase == phase and other_task_num < task_num:
                    is_blocker = True
                elif other_phase == phase and other_task_num == task_num and other_subtask < subtask:
                    is_blocker = True

                if is_blocker and other_task.status != TaskStatus.DONE:
                    blocking_tasks.append(f"{other_task.id} ({other_task.status.value})")

            if not blocking_tasks:
                # No blockers, this task is ready
                return candidate
            else:
                # Task is blocked, log and try next
                blockers_str = ", ".join(blocking_tasks)
                self.logger.info(f"Skipping {candidate.id} - blocked by: {blockers_str}")

        # All tasks are blocked
        self.logger.warning("No tasks ready - all TODO tasks blocked by dependencies")
        return None

    def _create_sdk_client(self) -> ClaudeSDKClient:
        """
        Create SDK client with MCP configuration.

        CRITICAL: Must include allowed_tools parameter for Write tool to work!
        """
        # SDK automatically uses Claude CLI credentials
        # No need to manually extract OAuth token

        linear_api_key = os.getenv(self.config.linear_api_key_env)

        # Configure MCP servers
        mcp_servers = {}
        if linear_api_key:
            mcp_servers["linear"] = {
                "type": "http",
                "url": "https://mcp.linear.app/mcp",
                "headers": {"Authorization": f"Bearer {linear_api_key}"}
            }
            self.logger.info("Configured Linear MCP server")

        # CRITICAL FIX: Must explicitly configure allowed_tools
        # Without this, Write operations will fail silently!
        options = ClaudeCodeOptions(
            model=self.config.model,
            system_prompt=self.system_prompt,
            max_turns=self.config.max_turns_per_task * 2,  # Allow extra turns for streaming
            cwd=str(Path(self.config.project_dir).absolute()),
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash", "TodoWrite"],  # ← CRITICAL
            mcp_servers=mcp_servers
        )

        self.logger.info(f"SDK configured with tools: {options.allowed_tools}")
        return ClaudeSDKClient(options)

    async def _execute_task(self, task: Task) -> TaskResult:
        """
        Execute a task with async streaming.

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

        # Create SDK client for this task
        self.sdk_client = self._create_sdk_client()

        # Build initial prompt
        initial_prompt = self._build_task_prompt(task)

        turns = 0
        full_response_parts = []
        files_changed = []
        success = False
        error = None

        # Retry logic for initialization timeout
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                async with self.sdk_client:
                    # Send initial prompt
                    await self.sdk_client.query(initial_prompt)

                    # Stream responses in real-time
                    async for msg in self.sdk_client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            turns += 1
                            self.checkpoint_manager.increment_turn()
                            self.turn_counter.increment()

                            # Process message content
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    text = block.text
                                    full_response_parts.append(text)

                                    # Log text block
                                    self.logger.debug(f"Received text block: {len(text)} chars")

                                    # Post progress updates in real-time
                                    await self._post_progress_updates(task.id, text)

                                elif isinstance(block, ToolUseBlock):
                                    # Log tool use in real-time
                                    self.logger.info(f"Tool use: {block.name}")
                                    if self.provider:
                                        self.provider.add_task_comment(
                                            task.id,
                                            f"🔧 **Tool Used:** `{block.name}`"
                                        )

                            # Check completion after each message
                            full_text = "\n".join(full_response_parts)
                            if self._is_task_complete(full_text):
                                success = True
                                files_changed = self._extract_files_changed(full_text)
                                break

                    # Success - exit retry loop
                    break

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"SDK execution error: {type(e).__name__}: {e}")

                # Retry on initialization timeout (first task only)
                if "Control request timeout: initialize" in error_msg and attempt < max_retries:
                    self.logger.warning(f"Initialization timeout on attempt {attempt + 1}, retrying...")
                    if self.provider:
                        self.provider.update_task(task.id, {"status": TaskStatus.TODO})
                    continue

                # Other errors - don't retry
                error = error_msg
                break

        # CRITICAL: Detect when Claude finishes without completion marker
        if not success and error is None:
            error = "Task did not complete - no completion marker found in response. Claude may have finished work without explicitly stating 'TASK COMPLETE'."
            self.logger.warning(error)

        return TaskResult(
            task_id=task.id,
            success=success,
            turns_used=turns,
            output="\n\n---\n\n".join(full_response_parts),
            error=error,
            files_changed=files_changed
        )

    async def _post_progress_updates(self, task_id: str, text: str):
        """Extract and post progress updates to Linear in real-time."""
        # Find [PROGRESS] markers
        progress_lines = re.findall(r'^\[PROGRESS\]\s*(.+)', text, re.MULTILINE)

        if progress_lines and self.provider:
            for update in progress_lines:
                comment = f"🤖 **Progress Update:**\n{update}"
                self.provider.add_task_comment(task_id, comment)
                self.logger.info(f"Posted progress: {update}")

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
            "**CRITICAL**: You MUST explicitly state \"TASK COMPLETE\" in your final message when you finish.",
            "",
            "Please complete this task. Remember to:",
            "1. Implement the required changes",
            "2. Run tests to verify your work",
            "3. State \"TASK COMPLETE\" when done",
        ])

        return "\n".join(prompt_parts)

    def _is_task_complete(self, response: str) -> bool:
        """Check if task is complete based on response."""
        complete_indicators = [
            "task complete",
            "successfully completed",
            "implementation complete",
            "all acceptance criteria met"
        ]
        return any(indicator in response.lower() for indicator in complete_indicators)

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

    def _update_task_status(self, task: Task, result: TaskResult):
        """Update task status based on execution result."""
        if not self.provider:
            return

        if result.success:
            # Task completed successfully
            update_data = {
                "status": TaskStatus.DONE,
                "completion_notes": f"Completed in {result.turns_used} turns\n\n{result.output[:500]}"
            }
            self.provider.update_task(task.id, update_data)
            self.logger.info(f"Task {task.id} marked as DONE")

        elif result.error:
            # Task failed or blocked
            update_data = {
                "status": TaskStatus.BLOCKED,
                "blocker": result.error
            }
            self.provider.update_task(task.id, update_data)
            self.logger.error(f"Task {task.id} marked as BLOCKED: {result.error}")

    def get_status(self) -> Dict[str, Any]:
        """Get current runner status."""
        return {
            "state": self.state.value,
            "session_id": self.session_id,
            "tasks_completed": self.tasks_completed,
        }


async def main():
    """Async main entry point for testing."""
    config = RunnerConfig.from_yaml(".ai-agents/config.yml")
    runner = AutonomousRunnerSDK(config)

    try:
        await runner.start()
    except KeyboardInterrupt:
        runner.stop()


if __name__ == "__main__":
    asyncio.run(main())
