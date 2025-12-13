"""
File-based State Provider for AI_agents

Implements StateProvider using local JSON files for state persistence.
This is the default/fallback provider for local development and projects
that don't need external state synchronization.

State files are stored in .ai-agents/state/:
- tasks.json - All task data
- meta.json - Session metadata
- sessions/ - Session logs

Configuration in .ai-agents/config.yml:
    state_provider:
      type: "file"
      state_dir: ".ai-agents/state"  # Optional, defaults to .ai-agents/state
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

from . import (
    StateProvider,
    Task,
    TaskStatus,
    TaskPriority,
    TaskCategory,
    SessionMeta
)


class FileStateProvider(StateProvider):
    """
    File-based state provider implementation.

    Stores all state in JSON files within the project directory.
    Suitable for:
    - Local development
    - Single-agent scenarios
    - Projects without external service requirements

    Limitations:
    - State doesn't survive if files are deleted
    - No real-time synchronization across contexts
    - Manual session handoff required
    """

    def __init__(self):
        self.state_dir: Path = Path(".ai-agents/state")
        self.tasks_file: Path = Path()
        self.meta_file: Path = Path()
        self.sessions_dir: Path = Path()
        self.session_id: Optional[str] = None
        self._tasks: Dict[str, Dict] = {}
        self._meta: Optional[Dict] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize file provider with directory configuration."""
        # Get state directory from config
        state_dir = config.get("state_dir", ".ai-agents/state")
        self.state_dir = Path(state_dir)

        # Set up file paths
        self.tasks_file = self.state_dir / "tasks.json"
        self.meta_file = self.state_dir / "meta.json"
        self.sessions_dir = self.state_dir / "sessions"

        # Create directories if needed
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self._load_tasks()
        self._load_meta()

        return True

    def _load_tasks(self):
        """Load tasks from file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                self._tasks = json.load(f)
        else:
            self._tasks = {}

    def _save_tasks(self):
        """Save tasks to file."""
        with open(self.tasks_file, 'w') as f:
            json.dump(self._tasks, f, indent=2, default=str)

    def _load_meta(self):
        """Load meta from file."""
        if self.meta_file.exists():
            with open(self.meta_file, 'r') as f:
                self._meta = json.load(f)
        else:
            self._meta = {
                "project_id": str(uuid.uuid4())[:8],
                "total_sessions": 0,
                "last_session_start": None,
                "last_session_end": None,
                "completed_task_count": 0,
                "current_focus": None,
                "known_issues": [],
                "architecture_decisions": [],
                "regression_status": "unknown",
                "notes": ""
            }
            self._save_meta()

    def _save_meta(self):
        """Save meta to file."""
        with open(self.meta_file, 'w') as f:
            json.dump(self._meta, f, indent=2, default=str)

    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        # Find highest existing task number
        max_num = 0
        for task_id in self._tasks.keys():
            if task_id.startswith("TASK-"):
                try:
                    num = int(task_id.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    pass
        return f"TASK-{max_num + 1:03d}"

    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task."""
        task_id = self._generate_task_id()
        now = datetime.now().isoformat()

        # Normalize status
        status = task_data.get("status", "todo")
        if isinstance(status, TaskStatus):
            status = status.value

        # Normalize priority
        priority = task_data.get("priority", 3)
        if isinstance(priority, TaskPriority):
            priority = priority.value

        # Normalize category
        category = task_data.get("category", "functional")
        if isinstance(category, TaskCategory):
            category = category.value

        task = {
            "id": task_id,
            "title": task_data["title"],
            "description": task_data.get("description", ""),
            "status": status,
            "priority": priority,
            "category": category,
            "acceptance_criteria": task_data.get("acceptance_criteria", []),
            "test_steps": task_data.get("test_steps", []),
            "created_at": now,
            "updated_at": now,
            "assigned_to": task_data.get("assigned_to"),
            "labels": task_data.get("labels", []),
            "parent_id": task_data.get("parent_id"),
            "metadata": task_data.get("metadata", {})
        }

        self._tasks[task_id] = task
        self._save_tasks()

        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        task_data = self._tasks.get(task_id)
        if not task_data:
            return None
        return Task.from_dict(task_data)

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task properties."""
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]

        for key, value in updates.items():
            if key == "status" and isinstance(value, TaskStatus):
                value = value.value
            elif key == "priority" and isinstance(value, TaskPriority):
                value = value.value
            elif key == "category" and isinstance(value, TaskCategory):
                value = value.value

            task[key] = value

        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks()

        return True

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        self._save_tasks()

        return True

    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[TaskCategory] = None,
        assigned_to: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> List[Task]:
        """Query tasks with filters."""
        tasks = []

        for task_data in self._tasks.values():
            # Apply filters
            if status:
                task_status = task_data.get("status", "todo")
                if task_status != status.value:
                    continue

            if priority:
                task_priority = task_data.get("priority", 3)
                if task_priority != priority.value:
                    continue

            if category:
                task_category = task_data.get("category", "functional")
                if task_category != category.value:
                    continue

            if assigned_to:
                if task_data.get("assigned_to") != assigned_to:
                    continue

            if labels:
                task_labels = task_data.get("labels", [])
                if not any(l in task_labels for l in labels):
                    continue

            tasks.append(Task.from_dict(task_data))

        # Sort by priority then created_at
        tasks.sort(key=lambda t: (t.priority.value, t.created_at))

        return tasks

    def get_meta(self) -> Optional[SessionMeta]:
        """Get session metadata."""
        if not self._meta:
            return None

        return SessionMeta(
            project_id=self._meta.get("project_id", "unknown"),
            total_sessions=self._meta.get("total_sessions", 0),
            last_session_start=datetime.fromisoformat(self._meta["last_session_start"]) if self._meta.get("last_session_start") else datetime.now(),
            last_session_end=datetime.fromisoformat(self._meta["last_session_end"]) if self._meta.get("last_session_end") else None,
            completed_task_count=self._meta.get("completed_task_count", 0),
            current_focus=self._meta.get("current_focus"),
            known_issues=self._meta.get("known_issues", []),
            architecture_decisions=self._meta.get("architecture_decisions", []),
            regression_status=self._meta.get("regression_status", "unknown"),
            notes=self._meta.get("notes", "")
        )

    def update_meta(self, updates: Dict[str, Any]) -> bool:
        """Update session metadata."""
        if not self._meta:
            self._load_meta()

        for key, value in updates.items():
            self._meta[key] = value

        self._save_meta()
        return True

    def start_session(self) -> str:
        """Mark session start."""
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        self._meta["total_sessions"] = self._meta.get("total_sessions", 0) + 1
        self._meta["last_session_start"] = datetime.now().isoformat()
        self._meta["last_session_end"] = None
        self._save_meta()

        # Create session log file
        session_file = self.sessions_dir / f"session-{self.session_id}.json"
        progress = self.get_progress_summary()

        session_log = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "initial_state": progress,
            "events": [],
            "summary": None
        }

        with open(session_file, 'w') as f:
            json.dump(session_log, f, indent=2)

        return self.session_id

    def end_session(self, summary: str) -> bool:
        """Mark session end with summary."""
        if not self.session_id:
            return False

        self._meta["last_session_end"] = datetime.now().isoformat()
        self._save_meta()

        # Update session log
        session_file = self.sessions_dir / f"session-{self.session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_log = json.load(f)

            session_log["ended_at"] = datetime.now().isoformat()
            session_log["final_state"] = self.get_progress_summary()
            session_log["summary"] = summary

            with open(session_file, 'w') as f:
                json.dump(session_log, f, indent=2)

        return True

    def add_session_comment(self, comment: str) -> bool:
        """Add event to session log."""
        if not self.session_id:
            return False

        session_file = self.sessions_dir / f"session-{self.session_id}.json"
        if not session_file.exists():
            return False

        with open(session_file, 'r') as f:
            session_log = json.load(f)

        session_log["events"].append({
            "timestamp": datetime.now().isoformat(),
            "comment": comment
        })

        with open(session_file, 'w') as f:
            json.dump(session_log, f, indent=2)

        return True

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary."""
        counts = {
            "todo": 0,
            "in_progress": 0,
            "blocked": 0,
            "in_review": 0,
            "done": 0,
            "cancelled": 0
        }

        for task in self._tasks.values():
            status = task.get("status", "todo")
            counts[status] = counts.get(status, 0) + 1

        total = len(self._tasks)
        done = counts["done"]

        return {
            **counts,
            "total": total,
            "completion_rate": done / total if total > 0 else 0,
            "active": counts["in_progress"] + counts["in_review"],
            "blocked_count": counts["blocked"]
        }
