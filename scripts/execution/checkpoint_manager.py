"""
Checkpoint Manager for AI_agents

Manages checkpoint triggering, approval flow, and notification
for interactive and supervised execution modes.

Usage:
    from scripts.execution.checkpoint_manager import CheckpointManager

    manager = CheckpointManager(config)

    # Check if checkpoint needed
    if manager.should_checkpoint("turn_interval"):
        checkpoint = manager.create_checkpoint("turn_interval", context)
        result = manager.wait_for_approval(checkpoint)

        if result.approved:
            continue_execution()
        else:
            handle_rejection(result)
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class CheckpointType(Enum):
    """Types of checkpoints that can be triggered"""
    TURN_INTERVAL = "turn_interval"
    BEFORE_NEW_ISSUE = "before_new_issue"
    AFTER_ISSUE_COMPLETE = "after_issue_complete"
    REGRESSION_FAILURE = "regression_failure"
    BLOCKER = "blocker"
    UNCERTAINTY = "uncertainty"
    CONTEXT_HIGH = "context_high"
    FILE_DELETE = "file_delete"
    GIT_PUSH = "git_push"
    DEPLOY = "deploy"
    SCHEMA_CHANGE = "schema_change"


class CheckpointStatus(Enum):
    """Status of a checkpoint"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"


class ApprovalAction(Enum):
    """Actions that can be taken at a checkpoint"""
    CONTINUE = "continue"
    PAUSE = "pause"
    ABORT = "abort"
    REDIRECT = "redirect"


@dataclass
class CheckpointContext:
    """Context data for a checkpoint"""
    task_id: Optional[str] = None
    task_title: Optional[str] = None
    action_description: Optional[str] = None
    files_affected: List[str] = field(default_factory=list)
    progress_summary: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    turn_number: int = 0
    context_usage: float = 0.0
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Checkpoint:
    """Represents a checkpoint event"""
    id: str
    type: CheckpointType
    triggered_at: datetime
    context: CheckpointContext
    status: CheckpointStatus = CheckpointStatus.PENDING
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    action_taken: Optional[ApprovalAction] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "triggered_at": self.triggered_at.isoformat(),
            "context": {
                "task_id": self.context.task_id,
                "task_title": self.context.task_title,
                "action_description": self.context.action_description,
                "files_affected": self.context.files_affected,
                "progress_summary": self.context.progress_summary,
                "error_details": self.context.error_details,
                "turn_number": self.context.turn_number,
                "context_usage": self.context.context_usage
            },
            "status": self.status.value,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "action_taken": self.action_taken.value if self.action_taken else None
        }


@dataclass
class ApprovalResult:
    """Result of a checkpoint approval"""
    approved: bool
    action: ApprovalAction
    notes: Optional[str] = None
    redirect_instructions: Optional[str] = None
    resolved_by: str = "user"


class CheckpointManager:
    """
    Manages checkpoint triggering and approval workflow.

    Supports:
    - Turn-based checkpoints
    - Event-based checkpoints
    - Action-based checkpoints
    - Multiple notification channels
    - Configurable timeouts
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize checkpoint manager with execution configuration.

        Args:
            config: Execution configuration from .ai-agents/config.yml
        """
        self.config = config
        self.mode = config.get("mode", "interactive")
        self.checkpoints_config = config.get("checkpoints", {})
        self.approval_config = config.get("approval", {})
        self.limits_config = config.get("limits", {})

        # State tracking
        self.current_turn = 0
        self.last_checkpoint_turn = 0
        self.checkpoints_history: List[Checkpoint] = []
        self.pending_checkpoint: Optional[Checkpoint] = None

        # Checkpoint file for persistence
        self.checkpoint_file = Path(".ai-agents/state/checkpoints.json")

        # Load any pending checkpoint from previous session
        self._load_pending_checkpoint()

    def _load_pending_checkpoint(self):
        """Load pending checkpoint from previous session."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                if data.get("pending"):
                    # Reconstruct pending checkpoint
                    pending = data["pending"]
                    self.pending_checkpoint = Checkpoint(
                        id=pending["id"],
                        type=CheckpointType(pending["type"]),
                        triggered_at=datetime.fromisoformat(pending["triggered_at"]),
                        context=CheckpointContext(**pending.get("context", {})),
                        status=CheckpointStatus(pending["status"])
                    )

    def _save_checkpoint_state(self):
        """Save checkpoint state for persistence."""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "current_turn": self.current_turn,
            "last_checkpoint_turn": self.last_checkpoint_turn,
            "pending": self.pending_checkpoint.to_dict() if self.pending_checkpoint else None,
            "history": [c.to_dict() for c in self.checkpoints_history[-10:]]  # Keep last 10
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def increment_turn(self):
        """Increment turn counter. Call this at start of each agent turn."""
        self.current_turn += 1

    def should_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        context: Optional[CheckpointContext] = None
    ) -> bool:
        """
        Check if a checkpoint should be triggered.

        Args:
            checkpoint_type: Type of checkpoint to check
            context: Optional context for context-dependent checks

        Returns:
            True if checkpoint should trigger
        """
        # Autonomous mode only stops on failures
        if self.mode == "autonomous":
            return checkpoint_type in [
                CheckpointType.REGRESSION_FAILURE,
                CheckpointType.CONTEXT_HIGH
            ] and self.checkpoints_config.get(checkpoint_type.value, False)

        # Check specific checkpoint type
        config_key = checkpoint_type.value

        if checkpoint_type == CheckpointType.TURN_INTERVAL:
            interval = self.checkpoints_config.get("turn_interval", 0)
            if interval <= 0:
                return False
            return (self.current_turn - self.last_checkpoint_turn) >= interval

        elif checkpoint_type == CheckpointType.CONTEXT_HIGH:
            if not context:
                return False
            threshold = self.limits_config.get("context_pause_threshold", 0.85)
            return context.context_usage >= threshold

        else:
            # Boolean checkpoint - check if enabled
            return self.checkpoints_config.get(config_key, False)

    def create_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        context: CheckpointContext
    ) -> Checkpoint:
        """
        Create a new checkpoint.

        Args:
            checkpoint_type: Type of checkpoint
            context: Context data for the checkpoint

        Returns:
            Created Checkpoint object
        """
        checkpoint = Checkpoint(
            id=f"cp-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{checkpoint_type.value}",
            type=checkpoint_type,
            triggered_at=datetime.now(),
            context=context
        )

        self.pending_checkpoint = checkpoint
        self.last_checkpoint_turn = self.current_turn
        self._save_checkpoint_state()

        return checkpoint

    def wait_for_approval(
        self,
        checkpoint: Checkpoint,
        cli_handler: Optional[Callable] = None
    ) -> ApprovalResult:
        """
        Wait for checkpoint approval.

        Args:
            checkpoint: Checkpoint to wait for
            cli_handler: Optional CLI handler for interactive approval

        Returns:
            ApprovalResult with user decision
        """
        # Send notifications
        self._send_notifications(checkpoint)

        # Get approval settings
        timeout_minutes = self.approval_config.get("timeout_minutes", 60)
        default_action = self.approval_config.get("default_action", "pause")

        # If CLI handler provided, use interactive approval
        if cli_handler:
            result = cli_handler(checkpoint)
        else:
            # Use default CLI approval
            result = self._cli_approval(checkpoint, timeout_minutes)

        # Handle timeout
        if result is None:
            if default_action == "continue":
                result = ApprovalResult(
                    approved=True,
                    action=ApprovalAction.CONTINUE,
                    resolved_by="timeout"
                )
            elif default_action == "abort":
                result = ApprovalResult(
                    approved=False,
                    action=ApprovalAction.ABORT,
                    resolved_by="timeout"
                )
            else:  # pause
                result = ApprovalResult(
                    approved=False,
                    action=ApprovalAction.PAUSE,
                    resolved_by="timeout"
                )

        # Update checkpoint status
        checkpoint.status = (
            CheckpointStatus.APPROVED if result.approved
            else CheckpointStatus.REJECTED if result.action == ApprovalAction.ABORT
            else CheckpointStatus.TIMED_OUT if result.resolved_by == "timeout"
            else CheckpointStatus.PENDING
        )
        checkpoint.resolved_at = datetime.now()
        checkpoint.resolved_by = result.resolved_by
        checkpoint.resolution_notes = result.notes
        checkpoint.action_taken = result.action

        # Archive checkpoint
        self.checkpoints_history.append(checkpoint)
        self.pending_checkpoint = None
        self._save_checkpoint_state()

        return result

    def _cli_approval(
        self,
        checkpoint: Checkpoint,
        timeout_minutes: int
    ) -> Optional[ApprovalResult]:
        """
        Handle CLI-based approval.

        Args:
            checkpoint: Checkpoint to approve
            timeout_minutes: Timeout in minutes

        Returns:
            ApprovalResult or None on timeout
        """
        # Format checkpoint display
        display = self._format_checkpoint_display(checkpoint)
        print(display)

        # Calculate timeout
        timeout_seconds = timeout_minutes * 60 if timeout_minutes > 0 else float('inf')
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            remaining = timeout_seconds - elapsed

            if remaining <= 0:
                print("\n⏰ Timeout reached")
                return None

            try:
                # Show remaining time
                if timeout_minutes > 0:
                    remaining_str = str(timedelta(seconds=int(remaining)))
                    prompt = f"\n[Auto-action in {remaining_str}] Enter choice (c/p/d/r/a): "
                else:
                    prompt = "\nEnter choice (c/p/d/r/a): "

                # Non-blocking input with timeout would require more complex implementation
                # For simplicity, using standard input
                choice = input(prompt).strip().lower()

                if choice == 'c':
                    return ApprovalResult(
                        approved=True,
                        action=ApprovalAction.CONTINUE,
                        resolved_by="user"
                    )
                elif choice == 'p':
                    return ApprovalResult(
                        approved=False,
                        action=ApprovalAction.PAUSE,
                        resolved_by="user"
                    )
                elif choice == 'd':
                    self._show_details(checkpoint)
                elif choice == 'r':
                    instructions = input("Enter new instructions: ").strip()
                    return ApprovalResult(
                        approved=True,
                        action=ApprovalAction.REDIRECT,
                        redirect_instructions=instructions,
                        resolved_by="user"
                    )
                elif choice == 'a':
                    confirm = input("Confirm abort? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return ApprovalResult(
                            approved=False,
                            action=ApprovalAction.ABORT,
                            resolved_by="user"
                        )
                else:
                    print("Invalid choice. Use: c=continue, p=pause, d=details, r=redirect, a=abort")

            except KeyboardInterrupt:
                print("\n\nInterrupted - treating as pause")
                return ApprovalResult(
                    approved=False,
                    action=ApprovalAction.PAUSE,
                    resolved_by="interrupt"
                )

    def _format_checkpoint_display(self, checkpoint: Checkpoint) -> str:
        """Format checkpoint for CLI display."""
        ctx = checkpoint.context

        lines = [
            "",
            "╔" + "═" * 60 + "╗",
            "║" + "CHECKPOINT TRIGGERED".center(60) + "║",
            "╠" + "═" * 60 + "╣",
            f"║ Type: {checkpoint.type.value.replace('_', ' ').title():<52} ║",
            f"║ Time: {checkpoint.triggered_at.strftime('%Y-%m-%d %H:%M:%S'):<52} ║",
            f"║ Turn: {ctx.turn_number:<52} ║",
            "╠" + "═" * 60 + "╣",
        ]

        # Add context-specific info
        if ctx.task_id:
            lines.append(f"║ Task: {ctx.task_id} - {ctx.task_title or 'Untitled':<42} ║")

        if ctx.action_description:
            desc = ctx.action_description[:50] + "..." if len(ctx.action_description) > 50 else ctx.action_description
            lines.append(f"║ Action: {desc:<50} ║")

        if ctx.progress_summary:
            lines.append("║" + " " * 60 + "║")
            lines.append("║ Progress:" + " " * 50 + "║")
            for key, value in ctx.progress_summary.items():
                lines.append(f"║   {key}: {value:<50} ║")

        if ctx.context_usage > 0:
            usage_pct = f"{ctx.context_usage * 100:.1f}%"
            lines.append(f"║ Context Usage: {usage_pct:<44} ║")

        if ctx.error_details:
            lines.append("║" + " " * 60 + "║")
            lines.append("║ Error: " + " " * 52 + "║")
            error_lines = ctx.error_details[:100].split('\n')
            for err_line in error_lines[:3]:
                lines.append(f"║   {err_line:<56} ║")

        lines.extend([
            "╠" + "═" * 60 + "╣",
            "║ Options:" + " " * 51 + "║",
            "║   [c] Continue - Resume agent work" + " " * 23 + "║",
            "║   [p] Pause - Save state and stop" + " " * 24 + "║",
            "║   [d] Details - Show more information" + " " * 20 + "║",
            "║   [r] Redirect - Give new instructions" + " " * 19 + "║",
            "║   [a] Abort - Stop immediately" + " " * 27 + "║",
            "╚" + "═" * 60 + "╝",
        ])

        return "\n".join(lines)

    def _show_details(self, checkpoint: Checkpoint):
        """Show detailed checkpoint information."""
        ctx = checkpoint.context

        print("\n" + "=" * 60)
        print("CHECKPOINT DETAILS")
        print("=" * 60)

        print(f"\nType: {checkpoint.type.value}")
        print(f"ID: {checkpoint.id}")
        print(f"Triggered: {checkpoint.triggered_at.isoformat()}")
        print(f"Turn: {ctx.turn_number}")
        print(f"Context Usage: {ctx.context_usage * 100:.1f}%")

        if ctx.task_id:
            print(f"\nTask: {ctx.task_id}")
            print(f"Title: {ctx.task_title}")

        if ctx.action_description:
            print(f"\nAction: {ctx.action_description}")

        if ctx.files_affected:
            print(f"\nFiles Affected ({len(ctx.files_affected)}):")
            for f in ctx.files_affected[:10]:
                print(f"  - {f}")
            if len(ctx.files_affected) > 10:
                print(f"  ... and {len(ctx.files_affected) - 10} more")

        if ctx.progress_summary:
            print("\nProgress Summary:")
            for key, value in ctx.progress_summary.items():
                print(f"  {key}: {value}")

        if ctx.error_details:
            print(f"\nError Details:\n{ctx.error_details}")

        print("\n" + "=" * 60)

    def _send_notifications(self, checkpoint: Checkpoint):
        """Send notifications to configured channels."""
        notification_config = self.approval_config.get("notification", {})

        # Slack notification
        slack_webhook = notification_config.get("slack_webhook")
        if slack_webhook and not slack_webhook.startswith("$"):
            self._send_slack_notification(checkpoint, slack_webhook)

        # Email notification (placeholder - would need email service)
        email = notification_config.get("email")
        if email:
            # Would integrate with email service
            pass

        # Linear comment
        if notification_config.get("linear_comment"):
            # Would integrate with state provider
            pass

    def _send_slack_notification(self, checkpoint: Checkpoint, webhook_url: str):
        """Send Slack notification for checkpoint."""
        ctx = checkpoint.context

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 Checkpoint: {checkpoint.type.value.replace('_', ' ').title()}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Turn:* {ctx.turn_number}"},
                    {"type": "mrkdwn", "text": f"*Context:* {ctx.context_usage * 100:.0f}%"}
                ]
            }
        ]

        if ctx.task_id:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Task:* {ctx.task_id} - {ctx.task_title}"}
            })

        if ctx.progress_summary:
            progress_text = " | ".join([f"{k}: {v}" for k, v in ctx.progress_summary.items()])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Progress:* {progress_text}"}
            })

        try:
            requests.post(webhook_url, json={"blocks": blocks})
        except Exception as e:
            print(f"Warning: Failed to send Slack notification: {e}")

    def get_checkpoint_history(self, limit: int = 10) -> List[Dict]:
        """Get recent checkpoint history."""
        return [c.to_dict() for c in self.checkpoints_history[-limit:]]

    def has_pending_checkpoint(self) -> bool:
        """Check if there's a pending checkpoint from previous session."""
        return self.pending_checkpoint is not None

    def get_pending_checkpoint(self) -> Optional[Checkpoint]:
        """Get the pending checkpoint if any."""
        return self.pending_checkpoint
