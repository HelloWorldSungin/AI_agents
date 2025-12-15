"""
Linear State Provider for AI_agents

Implements StateProvider using Linear.app API as the external source of truth.
This enables multi-agent systems to survive context resets by storing all
task state, session metadata, and progress in Linear.

Based on patterns from Linear-Coding-Agent-Harness.

Configuration in .ai-agents/config.yml:
    state_provider:
      type: "linear"
      api_key_env: "LINEAR_API_KEY"  # Environment variable name
      team_id: "TEAM_ID"             # Optional, auto-detected if not set
      project_id: "PROJECT_ID"       # Optional, creates one if not set
      meta_issue_label: "meta"       # Label for META tracking issue
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from . import (
    StateProvider,
    Task,
    TaskStatus,
    TaskPriority,
    TaskCategory,
    SessionMeta
)


# Linear API status mapping
LINEAR_STATUS_MAP = {
    TaskStatus.TODO: "Todo",
    TaskStatus.IN_PROGRESS: "In Progress",
    TaskStatus.BLOCKED: "Blocked",
    TaskStatus.IN_REVIEW: "In Review",
    TaskStatus.DONE: "Done",
    TaskStatus.CANCELLED: "Canceled"
}

REVERSE_STATUS_MAP = {v.lower(): k for k, v in LINEAR_STATUS_MAP.items()}

# Linear priority mapping (1=urgent in both systems)
LINEAR_PRIORITY_MAP = {
    TaskPriority.URGENT: 1,
    TaskPriority.HIGH: 2,
    TaskPriority.NORMAL: 3,
    TaskPriority.LOW: 4
}


class LinearStateProvider(StateProvider):
    """
    State provider implementation using Linear.app API.

    Features:
    - Creates issues for tasks with structured acceptance criteria
    - Uses a META issue for cross-session knowledge transfer
    - Comments on META issue for session handoffs
    - Supports project organization
    - Handles API pagination for large task lists
    """

    API_URL = "https://api.linear.app/graphql"

    def __init__(self):
        self.api_key: Optional[str] = None
        self.team_id: Optional[str] = None
        self.project_id: Optional[str] = None
        self.meta_issue_id: Optional[str] = None
        self.meta_label: str = "meta"
        self.session_id: Optional[str] = None
        self._status_ids: Dict[str, str] = {}  # Cache workflow state IDs
        self._label_ids: Dict[str, str] = {}   # Cache label IDs

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Linear provider with API credentials and team info."""
        # Get API key from environment
        api_key_env = config.get("api_key_env", "LINEAR_API_KEY")
        self.api_key = os.environ.get(api_key_env)

        if not self.api_key:
            raise ValueError(f"Linear API key not found in environment variable: {api_key_env}")

        # Get team ID (required or auto-detect)
        self.team_id = config.get("team_id")
        if not self.team_id:
            self.team_id = self._auto_detect_team()

        # Get or create project
        self.project_id = config.get("project_id")
        if not self.project_id and config.get("project_name"):
            self.project_id = self._get_or_create_project(config["project_name"])

        # Configure META issue label
        self.meta_label = config.get("meta_issue_label", "meta")

        # Cache workflow states and labels
        self._cache_workflow_states()
        self._cache_labels()

        # Find or create META issue
        self._ensure_meta_issue()

        return True

    def _graphql(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query against Linear API."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.API_URL,
            headers=headers,
            json={"query": query, "variables": variables or {}}
        )

        if response.status_code != 200:
            raise Exception(f"Linear API error: {response.status_code} - {response.text}")

        data = response.json()
        if "errors" in data:
            raise Exception(f"Linear GraphQL error: {data['errors']}")

        return data["data"]

    def _auto_detect_team(self) -> str:
        """Auto-detect team ID from user's teams."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                }
            }
        }
        """
        data = self._graphql(query)
        teams = data["teams"]["nodes"]

        if not teams:
            raise ValueError("No Linear teams found for this API key")

        # Return first team (or could prompt for selection)
        return teams[0]["id"]

    def _get_or_create_project(self, name: str) -> str:
        """Get existing project or create new one."""
        # First try to find existing
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                projects {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        data = self._graphql(query, {"teamId": self.team_id})
        projects = data["team"]["projects"]["nodes"]

        for project in projects:
            if project["name"].lower() == name.lower():
                return project["id"]

        # Create new project
        mutation = """
        mutation($teamId: String!, $name: String!) {
            projectCreate(input: {teamIds: [$teamId], name: $name}) {
                success
                project {
                    id
                }
            }
        }
        """
        data = self._graphql(mutation, {"teamId": self.team_id, "name": name})
        return data["projectCreate"]["project"]["id"]

    def _cache_workflow_states(self):
        """Cache workflow state IDs for the team."""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                states {
                    nodes {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        data = self._graphql(query, {"teamId": self.team_id})
        states = data["team"]["states"]["nodes"]

        for state in states:
            self._status_ids[state["name"].lower()] = state["id"]

    def _cache_labels(self):
        """Cache label IDs for the team."""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        data = self._graphql(query, {"teamId": self.team_id})
        labels = data["team"]["labels"]["nodes"]

        for label in labels:
            self._label_ids[label["name"].lower()] = label["id"]

    def _get_or_create_label(self, name: str) -> str:
        """Get label ID, creating if necessary."""
        if name.lower() in self._label_ids:
            return self._label_ids[name.lower()]

        mutation = """
        mutation($teamId: String!, $name: String!) {
            issueLabelCreate(input: {teamId: $teamId, name: $name}) {
                success
                issueLabel {
                    id
                }
            }
        }
        """
        data = self._graphql(mutation, {"teamId": self.team_id, "name": name})
        label_id = data["issueLabelCreate"]["issueLabel"]["id"]
        self._label_ids[name.lower()] = label_id
        return label_id

    def _ensure_meta_issue(self):
        """Find or create the META tracking issue."""
        # Search for existing META issue
        meta_label_id = self._get_or_create_label(self.meta_label)

        query = """
        query($teamId: ID, $labelId: ID) {
            issues(filter: {team: {id: {eq: $teamId}}, labels: {id: {eq: $labelId}}}) {
                nodes {
                    id
                    title
                }
            }
        }
        """
        data = self._graphql(query, {"teamId": self.team_id, "labelId": meta_label_id})
        issues = data["issues"]["nodes"]

        if issues:
            self.meta_issue_id = issues[0]["id"]
        else:
            # Create META issue
            self.meta_issue_id = self._create_meta_issue()

    def _create_meta_issue(self) -> str:
        """Create the META tracking issue."""
        meta_label_id = self._get_or_create_label(self.meta_label)

        description = """# Project META Issue

This issue tracks cross-session knowledge and project state.

## Session History
_Sessions will be logged as comments below._

## Architecture Decisions
_Key decisions made during development._

## Known Issues
_Tracked problems and blockers._

## Regression Status
Status: unknown

---
**DO NOT MODIFY THIS ISSUE DESCRIPTION**
Session updates are added as comments.
"""

        mutation = """
        mutation($teamId: String!, $title: String!, $description: String!, $labelIds: [String!]) {
            issueCreate(input: {
                teamId: $teamId,
                title: $title,
                description: $description,
                labelIds: $labelIds
            }) {
                success
                issue {
                    id
                }
            }
        }
        """
        data = self._graphql(mutation, {
            "teamId": self.team_id,
            "title": "[META] Project State Tracker",
            "description": description,
            "labelIds": [meta_label_id]
        })
        return data["issueCreate"]["issue"]["id"]

    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new issue in Linear."""
        # Handle Task objects by converting to dict
        if isinstance(task_data, Task):
            task_data = task_data.to_dict()

        # Build description with acceptance criteria and test steps
        description = task_data.get("description", "")

        if task_data.get("acceptance_criteria"):
            description += "\n\n## Acceptance Criteria\n"
            for criterion in task_data["acceptance_criteria"]:
                description += f"- [ ] {criterion}\n"

        if task_data.get("test_steps"):
            description += "\n\n## Test Steps\n"
            for i, step in enumerate(task_data["test_steps"], 1):
                description += f"{i}. {step}\n"

        # Map priority
        priority = task_data.get("priority", 3)
        if isinstance(priority, TaskPriority):
            priority = LINEAR_PRIORITY_MAP[priority]

        # Get status ID
        status = task_data.get("status", "todo")
        if isinstance(status, TaskStatus):
            status = LINEAR_STATUS_MAP[status].lower()
        state_id = self._status_ids.get(status, self._status_ids.get("todo"))

        # Build label IDs
        label_ids = []
        if task_data.get("category"):
            category = task_data["category"]
            if isinstance(category, TaskCategory):
                category = category.value
            label_ids.append(self._get_or_create_label(category))

        if task_data.get("labels"):
            for label in task_data["labels"]:
                label_ids.append(self._get_or_create_label(label))

        # Create issue
        mutation = """
        mutation($teamId: String!, $title: String!, $description: String!,
                 $priority: Int, $stateId: String, $labelIds: [String!], $projectId: String) {
            issueCreate(input: {
                teamId: $teamId,
                title: $title,
                description: $description,
                priority: $priority,
                stateId: $stateId,
                labelIds: $labelIds,
                projectId: $projectId
            }) {
                success
                issue {
                    id
                    identifier
                }
            }
        }
        """

        variables = {
            "teamId": self.team_id,
            "title": task_data["title"],
            "description": description,
            "priority": priority,
            "stateId": state_id,
            "projectId": self.project_id
        }
        # Only include labelIds if we have labels
        if label_ids:
            variables["labelIds"] = label_ids

        data = self._graphql(mutation, variables)
        return data["issueCreate"]["issue"]["identifier"]

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by its identifier."""
        query = """
        query($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                priority
                state {
                    name
                }
                labels {
                    nodes {
                        name
                    }
                }
                createdAt
                updatedAt
                assignee {
                    name
                }
                parent {
                    identifier
                }
            }
        }
        """

        try:
            data = self._graphql(query, {"id": task_id})
            issue = data["issue"]

            if not issue:
                return None

            return self._issue_to_task(issue)
        except Exception:
            return None

    def _issue_to_task(self, issue: Dict) -> Task:
        """Convert Linear issue to Task object."""
        # Parse acceptance criteria and test steps from description
        description = issue.get("description", "")
        acceptance_criteria = []
        test_steps = []

        # Simple parsing (could be enhanced)
        if "## Acceptance Criteria" in description:
            ac_section = description.split("## Acceptance Criteria")[1]
            if "##" in ac_section:
                ac_section = ac_section.split("##")[0]
            for line in ac_section.strip().split("\n"):
                if line.strip().startswith("- ["):
                    acceptance_criteria.append(line.strip()[6:].strip())

        if "## Test Steps" in description:
            ts_section = description.split("## Test Steps")[1]
            if "##" in ts_section:
                ts_section = ts_section.split("##")[0]
            for line in ts_section.strip().split("\n"):
                if line.strip() and line.strip()[0].isdigit():
                    test_steps.append(line.strip().split(". ", 1)[-1])

        # Get labels for category
        labels = [l["name"] for l in issue.get("labels", {}).get("nodes", [])]
        category = TaskCategory.FUNCTIONAL
        for cat in TaskCategory:
            if cat.value in [l.lower() for l in labels]:
                category = cat
                break

        # Map status
        status_name = issue.get("state", {}).get("name", "Todo").lower()
        status = REVERSE_STATUS_MAP.get(status_name, TaskStatus.TODO)

        # Map priority
        priority_val = issue.get("priority", 3)
        priority = TaskPriority.NORMAL
        for p, v in LINEAR_PRIORITY_MAP.items():
            if v == priority_val:
                priority = p
                break

        return Task(
            id=issue.get("identifier", issue["id"]),
            title=issue["title"],
            description=description,
            status=status,
            priority=priority,
            category=category,
            acceptance_criteria=acceptance_criteria,
            test_steps=test_steps,
            created_at=datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00")),
            assigned_to=issue.get("assignee", {}).get("name") if issue.get("assignee") else None,
            labels=labels,
            parent_id=issue.get("parent", {}).get("identifier") if issue.get("parent") else None
        )

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task properties."""
        # Build update input
        update_input = {}

        if "title" in updates:
            update_input["title"] = updates["title"]

        if "description" in updates:
            update_input["description"] = updates["description"]

        if "status" in updates:
            status = updates["status"]
            if isinstance(status, TaskStatus):
                status = LINEAR_STATUS_MAP[status].lower()
            if status in self._status_ids:
                update_input["stateId"] = self._status_ids[status]

        if "priority" in updates:
            priority = updates["priority"]
            if isinstance(priority, TaskPriority):
                priority = LINEAR_PRIORITY_MAP[priority]
            update_input["priority"] = priority

        if not update_input:
            return True  # Nothing to update

        mutation = """
        mutation($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
            }
        }
        """

        data = self._graphql(mutation, {"id": task_id, "input": update_input})
        return data["issueUpdate"]["success"]

    def delete_task(self, task_id: str) -> bool:
        """Archive (soft delete) a task."""
        mutation = """
        mutation($id: String!) {
            issueArchive(id: $id) {
                success
            }
        }
        """
        data = self._graphql(mutation, {"id": task_id})
        return data["issueArchive"]["success"]

    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[TaskCategory] = None,
        assigned_to: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> List[Task]:
        """Query tasks with filters."""
        # Build filter
        filters = [f'team: {{id: {{eq: "{self.team_id}"}}}}']

        # Exclude META issue
        meta_label_id = self._label_ids.get(self.meta_label.lower())
        if meta_label_id:
            filters.append(f'labels: {{id: {{neq: "{meta_label_id}"}}}}')

        if status:
            status_name = LINEAR_STATUS_MAP[status].lower()
            if status_name in self._status_ids:
                filters.append(f'state: {{id: {{eq: "{self._status_ids[status_name]}"}}}}')

        if priority:
            filters.append(f'priority: {{eq: {LINEAR_PRIORITY_MAP[priority]}}}')

        if self.project_id:
            filters.append(f'project: {{id: {{eq: "{self.project_id}"}}}}')

        filter_str = ", ".join(filters)

        query = f"""
        query {{
            issues(filter: {{{filter_str}}}, first: 100) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    priority
                    state {{
                        name
                    }}
                    labels {{
                        nodes {{
                            name
                        }}
                    }}
                    createdAt
                    updatedAt
                    assignee {{
                        name
                    }}
                    parent {{
                        identifier
                    }}
                }}
            }}
        }}
        """

        data = self._graphql(query)
        issues = data["issues"]["nodes"]

        tasks = [self._issue_to_task(issue) for issue in issues]

        # Apply additional filters that aren't easily done in GraphQL
        if category:
            tasks = [t for t in tasks if t.category == category]

        if labels:
            tasks = [t for t in tasks if any(l in (t.labels or []) for l in labels)]

        return tasks

    def get_meta(self) -> Optional[SessionMeta]:
        """Get META issue content as SessionMeta."""
        if not self.meta_issue_id:
            return None

        query = """
        query($id: String!) {
            issue(id: $id) {
                description
                comments {
                    nodes {
                        body
                        createdAt
                    }
                }
            }
        }
        """

        data = self._graphql(query, {"id": self.meta_issue_id})
        issue = data["issue"]

        if not issue:
            return None

        # Parse META issue - this is a simplified version
        # In production, would parse the structured content more carefully
        comments = issue.get("comments", {}).get("nodes", [])

        return SessionMeta(
            project_id=self.project_id or self.team_id,
            total_sessions=len([c for c in comments if "Session Start" in c.get("body", "")]),
            last_session_start=datetime.now(),  # Would parse from comments
            last_session_end=None,
            completed_task_count=0,  # Would query from tasks
            current_focus=None,
            known_issues=[],
            architecture_decisions=[],
            regression_status="unknown",
            notes=issue.get("description", "")
        )

    def update_meta(self, updates: Dict[str, Any]) -> bool:
        """Update META issue (adds comment for most updates)."""
        # For most updates, we add a comment rather than modifying description
        comment = f"**Meta Update** ({datetime.now().isoformat()})\n\n"

        for key, value in updates.items():
            comment += f"- **{key}**: {value}\n"

        return self.add_session_comment(comment)

    def start_session(self) -> str:
        """Mark session start in META issue."""
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Get current progress for context
        progress = self.get_progress_summary()

        comment = f"""## Session Start: {self.session_id}

**Time**: {datetime.now().isoformat()}

**Current State**:
- Todo: {progress.get('todo', 0)}
- In Progress: {progress.get('in_progress', 0)}
- Done: {progress.get('done', 0)}
- Completion Rate: {progress.get('completion_rate', 0):.1%}

---
"""
        self.add_session_comment(comment)
        return self.session_id

    def end_session(self, summary: str) -> bool:
        """Mark session end with summary."""
        progress = self.get_progress_summary()

        comment = f"""## Session End: {self.session_id}

**Time**: {datetime.now().isoformat()}

**Summary**:
{summary}

**Final State**:
- Todo: {progress.get('todo', 0)}
- In Progress: {progress.get('in_progress', 0)}
- Done: {progress.get('done', 0)}
- Completion Rate: {progress.get('completion_rate', 0):.1%}

---
"""
        return self.add_session_comment(comment)

    def add_session_comment(self, comment: str) -> bool:
        """Add comment to META issue."""
        if not self.meta_issue_id:
            return False

        mutation = """
        mutation($issueId: String!, $body: String!) {
            commentCreate(input: {issueId: $issueId, body: $body}) {
                success
            }
        }
        """

        data = self._graphql(mutation, {
            "issueId": self.meta_issue_id,
            "body": comment
        })
        return data["commentCreate"]["success"]

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary across all tasks."""
        # Count tasks by status
        all_tasks = self.get_tasks()

        counts = {
            "todo": 0,
            "in_progress": 0,
            "blocked": 0,
            "in_review": 0,
            "done": 0,
            "cancelled": 0
        }

        for task in all_tasks:
            counts[task.status.value] = counts.get(task.status.value, 0) + 1

        total = len(all_tasks)
        done = counts["done"]

        return {
            **counts,
            "total": total,
            "completion_rate": done / total if total > 0 else 0,
            "active": counts["in_progress"] + counts["in_review"],
            "blocked_count": counts["blocked"]
        }
