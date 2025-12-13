"""
Progress Tracker for AI_agents

Provides real-time progress tracking and human-visible status updates
for multi-agent development sessions.

Features:
- Task completion tracking
- Session progress metrics
- CLI progress display
- Webhook notifications
- Integration with state providers

Usage:
    from scripts.progress.progress_tracker import ProgressTracker

    tracker = ProgressTracker(provider)
    tracker.start_tracking()

    # Update on events
    tracker.task_started("TASK-001")
    tracker.task_completed("TASK-001")

    # Get summary
    print(tracker.get_summary())
"""

import os
import json
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class EventType(Enum):
    """Types of progress events"""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    CHECKPOINT = "checkpoint"
    REGRESSION_RUN = "regression_run"
    REGRESSION_FAIL = "regression_fail"
    ERROR = "error"


@dataclass
class ProgressEvent:
    """Represents a progress event"""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


@dataclass
class ProgressMetrics:
    """Current progress metrics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    blocked_tasks: int = 0
    session_tasks_completed: int = 0
    completion_rate: float = 0.0
    session_duration: timedelta = field(default_factory=lambda: timedelta())
    tasks_per_hour: float = 0.0
    regression_status: str = "unknown"


class ProgressTracker:
    """
    Tracks and displays progress for agent sessions.

    Provides:
    - Real-time metrics
    - CLI progress display
    - Webhook notifications
    - Integration with Linear/GitHub
    """

    def __init__(
        self,
        state_provider=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize progress tracker.

        Args:
            state_provider: StateProvider instance for task queries
            config: Optional configuration
        """
        self.provider = state_provider
        self.config = config or {}

        # Session tracking
        self.session_id: Optional[str] = None
        self.session_start: Optional[datetime] = None
        self.events: List[ProgressEvent] = []

        # Metrics
        self.metrics = ProgressMetrics()

        # Notification config
        self.notification_interval = self.config.get('notification_interval', 300)  # 5 min
        self.slack_webhook = self.config.get('slack_webhook')
        self.notify_on_complete = self.config.get('notify_on_complete', True)
        self.notify_on_blocked = self.config.get('notify_on_blocked', True)

        # State file
        self.state_dir = Path('.ai-agents/state')
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.state_dir / 'progress.json'

        # Background notification thread
        self._notification_thread: Optional[threading.Thread] = None
        self._stop_notifications = threading.Event()

    def start_tracking(self, session_id: Optional[str] = None):
        """Start a new tracking session."""
        self.session_id = session_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_start = datetime.now()
        self.events = []

        self._record_event(EventType.SESSION_START, {
            "session_id": self.session_id
        })

        # Load initial metrics from provider
        if self.provider:
            self._update_metrics_from_provider()

        # Start notification thread
        self._start_notification_thread()

        # Save initial state
        self._save_state()

    def stop_tracking(self, summary: Optional[str] = None):
        """Stop tracking session."""
        self._stop_notification_thread()

        self._record_event(EventType.SESSION_END, {
            "session_id": self.session_id,
            "summary": summary,
            "tasks_completed": self.metrics.session_tasks_completed,
            "duration_minutes": self.metrics.session_duration.total_seconds() / 60
        })

        # Final notification
        if self.slack_webhook:
            self._send_session_summary()

        self._save_state()

    def task_started(self, task_id: str, task_title: Optional[str] = None):
        """Record task started."""
        self._record_event(EventType.TASK_STARTED, {
            "task_id": task_id,
            "title": task_title
        })
        self._update_metrics()
        self._save_state()

    def task_completed(self, task_id: str, task_title: Optional[str] = None):
        """Record task completed."""
        self._record_event(EventType.TASK_COMPLETED, {
            "task_id": task_id,
            "title": task_title
        })
        self.metrics.session_tasks_completed += 1
        self._update_metrics()
        self._save_state()

        if self.notify_on_complete and self.slack_webhook:
            self._send_task_notification(task_id, task_title, "completed")

    def task_blocked(self, task_id: str, blocker: str):
        """Record task blocked."""
        self._record_event(EventType.TASK_BLOCKED, {
            "task_id": task_id,
            "blocker": blocker
        })
        self._update_metrics()
        self._save_state()

        if self.notify_on_blocked and self.slack_webhook:
            self._send_blocker_notification(task_id, blocker)

    def regression_run(self, status: str, details: Optional[Dict] = None):
        """Record regression test run."""
        self.metrics.regression_status = status

        self._record_event(EventType.REGRESSION_RUN, {
            "status": status,
            "details": details
        })

        if status == "failing":
            self._record_event(EventType.REGRESSION_FAIL, details or {})
            if self.slack_webhook:
                self._send_regression_failure()

        self._save_state()

    def checkpoint(self, checkpoint_type: str, context: Dict):
        """Record checkpoint event."""
        self._record_event(EventType.CHECKPOINT, {
            "type": checkpoint_type,
            "context": context
        })
        self._save_state()

    def _record_event(self, event_type: EventType, data: Dict):
        """Record a progress event."""
        event = ProgressEvent(
            type=event_type,
            timestamp=datetime.now(),
            data=data
        )
        self.events.append(event)

        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

    def _update_metrics(self):
        """Update metrics from provider."""
        if self.session_start:
            self.metrics.session_duration = datetime.now() - self.session_start

            # Calculate tasks per hour
            hours = self.metrics.session_duration.total_seconds() / 3600
            if hours > 0:
                self.metrics.tasks_per_hour = self.metrics.session_tasks_completed / hours

        if self.provider:
            self._update_metrics_from_provider()

    def _update_metrics_from_provider(self):
        """Update metrics from state provider."""
        try:
            summary = self.provider.get_progress_summary()
            self.metrics.total_tasks = summary.get('total', 0)
            self.metrics.completed_tasks = summary.get('done', 0)
            self.metrics.in_progress_tasks = summary.get('in_progress', 0)
            self.metrics.blocked_tasks = summary.get('blocked', 0)
            self.metrics.completion_rate = summary.get('completion_rate', 0)

            # Get regression status from META
            meta = self.provider.get_meta()
            if meta:
                self.metrics.regression_status = meta.regression_status

        except Exception as e:
            print(f"Warning: Could not update metrics from provider: {e}")

    def get_summary(self) -> str:
        """Get formatted progress summary."""
        self._update_metrics()

        duration_str = str(self.metrics.session_duration).split('.')[0]

        return f"""
Progress Summary
================

Session: {self.session_id}
Duration: {duration_str}

Tasks:
  Total: {self.metrics.total_tasks}
  Done: {self.metrics.completed_tasks} ({self.metrics.completion_rate:.1%})
  In Progress: {self.metrics.in_progress_tasks}
  Blocked: {self.metrics.blocked_tasks}

Session Stats:
  Completed This Session: {self.metrics.session_tasks_completed}
  Rate: {self.metrics.tasks_per_hour:.1f} tasks/hour

Regression Status: {self.metrics.regression_status.upper()}
"""

    def get_cli_display(self) -> str:
        """Get compact CLI display string."""
        self._update_metrics()

        # Progress bar
        bar_width = 20
        if self.metrics.total_tasks > 0:
            filled = int(bar_width * self.metrics.completion_rate)
            bar = '█' * filled + '░' * (bar_width - filled)
        else:
            bar = '░' * bar_width

        status_emoji = {
            "passing": "✓",
            "failing": "✗",
            "unknown": "?"
        }.get(self.metrics.regression_status, "?")

        return (
            f"[{bar}] {self.metrics.completion_rate:.0%} "
            f"| Done: {self.metrics.completed_tasks}/{self.metrics.total_tasks} "
            f"| Session: {self.metrics.session_tasks_completed} "
            f"| Regr: {status_emoji}"
        )

    def _save_state(self):
        """Save progress state to file."""
        state = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "completed_tasks": self.metrics.completed_tasks,
                "in_progress_tasks": self.metrics.in_progress_tasks,
                "blocked_tasks": self.metrics.blocked_tasks,
                "session_tasks_completed": self.metrics.session_tasks_completed,
                "completion_rate": self.metrics.completion_rate,
                "tasks_per_hour": self.metrics.tasks_per_hour,
                "regression_status": self.metrics.regression_status
            },
            "recent_events": [e.to_dict() for e in self.events[-20:]],
            "updated_at": datetime.now().isoformat()
        }

        with open(self.progress_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _start_notification_thread(self):
        """Start background notification thread."""
        if self.slack_webhook and self.notification_interval > 0:
            self._stop_notifications.clear()
            self._notification_thread = threading.Thread(
                target=self._notification_loop,
                daemon=True
            )
            self._notification_thread.start()

    def _stop_notification_thread(self):
        """Stop background notification thread."""
        if self._notification_thread:
            self._stop_notifications.set()
            self._notification_thread.join(timeout=5)
            self._notification_thread = None

    def _notification_loop(self):
        """Background loop for periodic notifications."""
        while not self._stop_notifications.is_set():
            self._stop_notifications.wait(self.notification_interval)
            if not self._stop_notifications.is_set():
                self._send_periodic_update()

    def _send_periodic_update(self):
        """Send periodic progress update to Slack."""
        if not self.slack_webhook:
            return

        self._update_metrics()

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 Progress Update* | Session: `{self.session_id}`"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Done:* {self.metrics.completed_tasks}/{self.metrics.total_tasks}"},
                    {"type": "mrkdwn", "text": f"*Completion:* {self.metrics.completion_rate:.0%}"},
                    {"type": "mrkdwn", "text": f"*This Session:* {self.metrics.session_tasks_completed}"},
                    {"type": "mrkdwn", "text": f"*Rate:* {self.metrics.tasks_per_hour:.1f}/hr"}
                ]
            }
        ]

        self._send_slack(blocks)

    def _send_task_notification(self, task_id: str, title: Optional[str], status: str):
        """Send task status notification to Slack."""
        if not self.slack_webhook:
            return

        emoji = "✅" if status == "completed" else "🔄"
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Task {status.title()}:* `{task_id}` - {title or 'Untitled'}"
                }
            }
        ]

        self._send_slack(blocks)

    def _send_blocker_notification(self, task_id: str, blocker: str):
        """Send blocker notification to Slack."""
        if not self.slack_webhook:
            return

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚫 *Task Blocked:* `{task_id}`\n> {blocker}"
                }
            }
        ]

        self._send_slack(blocks)

    def _send_regression_failure(self):
        """Send regression failure notification to Slack."""
        if not self.slack_webhook:
            return

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🔴 *Regression Tests FAILING*\nNew features blocked until fixed."
                }
            }
        ]

        self._send_slack(blocks)

    def _send_session_summary(self):
        """Send session summary to Slack."""
        if not self.slack_webhook:
            return

        duration_str = str(self.metrics.session_duration).split('.')[0]

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Session Complete: {self.session_id}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Duration:* {duration_str}"},
                    {"type": "mrkdwn", "text": f"*Tasks Completed:* {self.metrics.session_tasks_completed}"},
                    {"type": "mrkdwn", "text": f"*Overall Progress:* {self.metrics.completion_rate:.0%}"},
                    {"type": "mrkdwn", "text": f"*Regression:* {self.metrics.regression_status}"}
                ]
            }
        ]

        self._send_slack(blocks)

    def _send_slack(self, blocks: List[Dict]):
        """Send message to Slack webhook."""
        if not self.slack_webhook or self.slack_webhook.startswith("$"):
            return

        try:
            requests.post(self.slack_webhook, json={"blocks": blocks})
        except Exception as e:
            print(f"Warning: Failed to send Slack notification: {e}")


def create_progress_tracker(
    provider=None,
    slack_webhook: Optional[str] = None,
    notification_interval: int = 300
) -> ProgressTracker:
    """
    Create a progress tracker with common defaults.

    Args:
        provider: StateProvider instance
        slack_webhook: Slack webhook URL
        notification_interval: Seconds between periodic updates

    Returns:
        Configured ProgressTracker
    """
    config = {
        'slack_webhook': slack_webhook,
        'notification_interval': notification_interval,
        'notify_on_complete': True,
        'notify_on_blocked': True
    }

    return ProgressTracker(provider, config)
