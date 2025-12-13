"""
Progress Tracking Module for AI_agents

Provides real-time progress tracking and notifications
for multi-agent development sessions.

Usage:
    from scripts.progress import ProgressTracker, create_progress_tracker

    tracker = create_progress_tracker(provider, slack_webhook="...")
    tracker.start_tracking()

    tracker.task_completed("TASK-001", "Implement login")
    print(tracker.get_cli_display())

    tracker.stop_tracking()
"""

from .progress_tracker import (
    ProgressTracker,
    ProgressEvent,
    ProgressMetrics,
    EventType,
    create_progress_tracker
)

__all__ = [
    "ProgressTracker",
    "ProgressEvent",
    "ProgressMetrics",
    "EventType",
    "create_progress_tracker"
]
