"""
State Provider Abstraction for AI_agents

This module provides an abstraction layer for state persistence,
allowing multi-agent systems to survive context resets by storing
state in external systems (Linear, GitHub Issues, Notion, etc.)
instead of relying solely on local files.

Usage:
    from state_providers import get_provider

    # Get configured provider (reads from .ai-agents/config.yml)
    provider = get_provider()

    # Create/update task
    task_id = provider.create_task({
        "title": "Implement authentication",
        "description": "Add JWT-based auth",
        "priority": 1,
        "category": "functional"
    })

    # Update task status
    provider.update_task(task_id, {"status": "in_progress"})

    # Get all tasks
    tasks = provider.get_tasks(status="in_progress")

    # Store session metadata (META issue equivalent)
    provider.update_meta({
        "last_session": "2024-01-15T10:30:00Z",
        "completed_tasks": 5,
        "current_focus": "authentication"
    })
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from datetime import datetime


class TaskStatus(Enum):
    """Task status values aligned with Linear workflow"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels (1=urgent, 4=low)"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskCategory(Enum):
    """Task categories for organizing work"""
    FUNCTIONAL = "functional"
    STYLE = "style"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    BUGFIX = "bugfix"


@dataclass
class Task:
    """Represents a task/issue in the external system"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    category: TaskCategory
    acceptance_criteria: List[str]
    test_steps: List[str]
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    labels: Optional[List[str]] = None
    parent_id: Optional[str] = None  # For subtasks
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "category": self.category.value,
            "acceptance_criteria": self.acceptance_criteria,
            "test_steps": self.test_steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_to": self.assigned_to,
            "labels": self.labels,
            "parent_id": self.parent_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "todo")),
            priority=TaskPriority(data.get("priority", 3)),
            category=TaskCategory(data.get("category", "functional")),
            acceptance_criteria=data.get("acceptance_criteria", []),
            test_steps=data.get("test_steps", []),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.now()),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.now()),
            assigned_to=data.get("assigned_to"),
            labels=data.get("labels"),
            parent_id=data.get("parent_id"),
            metadata=data.get("metadata")
        )


@dataclass
class SessionMeta:
    """META issue equivalent - tracks cross-session knowledge"""
    project_id: str
    total_sessions: int
    last_session_start: datetime
    last_session_end: Optional[datetime]
    completed_task_count: int
    current_focus: Optional[str]
    known_issues: List[str]
    architecture_decisions: List[Dict[str, str]]
    regression_status: str  # "passing", "failing", "unknown"
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "total_sessions": self.total_sessions,
            "last_session_start": self.last_session_start.isoformat(),
            "last_session_end": self.last_session_end.isoformat() if self.last_session_end else None,
            "completed_task_count": self.completed_task_count,
            "current_focus": self.current_focus,
            "known_issues": self.known_issues,
            "architecture_decisions": self.architecture_decisions,
            "regression_status": self.regression_status,
            "notes": self.notes
        }


class StateProvider(ABC):
    """
    Abstract base class for state providers.

    Implementations must handle:
    - Task CRUD operations
    - Session metadata (META issue)
    - Progress tracking
    - Query filtering
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the provider with configuration.

        Args:
            config: Provider-specific configuration (API keys, team IDs, etc.)

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create a new task/issue.

        Args:
            task_data: Task properties (title, description, priority, etc.)

        Returns:
            Created task ID
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object or None if not found
        """
        pass

    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update task properties.

        Args:
            task_id: Task identifier
            updates: Properties to update

        Returns:
            True if update successful
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task (soft delete preferred).

        Args:
            task_id: Task identifier

        Returns:
            True if deletion successful
        """
        pass

    @abstractmethod
    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[TaskCategory] = None,
        assigned_to: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> List[Task]:
        """
        Query tasks with optional filters.

        Args:
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            assigned_to: Filter by assignee
            labels: Filter by labels (any match)

        Returns:
            List of matching tasks
        """
        pass

    @abstractmethod
    def get_meta(self) -> Optional[SessionMeta]:
        """
        Get session metadata (META issue content).

        Returns:
            SessionMeta object or None if not initialized
        """
        pass

    @abstractmethod
    def update_meta(self, updates: Dict[str, Any]) -> bool:
        """
        Update session metadata.

        Args:
            updates: Properties to update

        Returns:
            True if update successful
        """
        pass

    @abstractmethod
    def start_session(self) -> str:
        """
        Mark the start of a new session.

        Returns:
            Session ID
        """
        pass

    @abstractmethod
    def end_session(self, summary: str) -> bool:
        """
        Mark the end of a session with summary.

        Args:
            summary: Session summary for handoff

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def add_session_comment(self, comment: str) -> bool:
        """
        Add a comment to the META issue for this session.

        Args:
            comment: Comment text (markdown supported)

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get progress summary for display.

        Returns:
            Dictionary with counts by status, completion rate, etc.
        """
        pass


def get_provider(config_path: Optional[str] = None) -> StateProvider:
    """
    Get configured state provider based on project config.

    Args:
        config_path: Path to config file (defaults to .ai-agents/config.yml)

    Returns:
        Configured StateProvider instance
    """
    import yaml

    # Default config path
    if config_path is None:
        config_path = ".ai-agents/config.yml"

    # Load config if file exists
    provider_type = "file"  # Default to file-based
    provider_config = {}

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            state_config = config.get("state_provider", {})
            provider_type = state_config.get("type", "file")
            provider_config = state_config

    # Import and instantiate appropriate provider
    if provider_type == "linear":
        from .linear_provider import LinearStateProvider
        provider = LinearStateProvider()
    elif provider_type == "github":
        from .github_provider import GitHubStateProvider
        provider = GitHubStateProvider()
    elif provider_type == "notion":
        from .notion_provider import NotionStateProvider
        provider = NotionStateProvider()
    else:
        from .file_provider import FileStateProvider
        provider = FileStateProvider()

    # Initialize with config
    provider.initialize(provider_config)

    return provider


# Convenience exports
__all__ = [
    "StateProvider",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskCategory",
    "SessionMeta",
    "get_provider"
]
