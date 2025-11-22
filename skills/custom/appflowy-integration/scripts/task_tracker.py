#!/usr/bin/env python3
"""
AppFlowy Task Tracker

Helper script for tracking agent tasks in AppFlowy.
Provides simple CLI for creating and updating tasks.

Usage:
    # Create a task
    python task_tracker.py create "Implement feature X" --priority high

    # Update task status
    python task_tracker.py update <task_id> --status completed

    # List recent tasks
    python task_tracker.py list --limit 10
"""

import sys
import argparse
import json
from datetime import datetime, timedelta
from typing import Optional

try:
    from appflowy_client import AppFlowyClient, AppFlowyError
except ImportError:
    print("Error: appflowy_client.py not found. Ensure it's in the same directory.")
    sys.exit(1)


class TaskTracker:
    """Helper for tracking tasks in AppFlowy."""

    def __init__(self, database_name: str = "Tasks"):
        """
        Initialize task tracker.

        Args:
            database_name: Name of the database to use for tasks
        """
        self.client = AppFlowyClient()
        self.database_name = database_name
        self._database_id = None

    @property
    def database_id(self) -> str:
        """Get or find the tasks database ID."""
        if not self._database_id:
            db = self.client.find_database_by_name(self.database_name)
            if not db:
                raise AppFlowyError(
                    f"Database '{self.database_name}' not found. "
                    "Please create it in AppFlowy first."
                )
            self._database_id = db['id']
        return self._database_id

    def create_task(
        self,
        title: str,
        description: str = "",
        status: str = "Todo",
        priority: str = "Medium",
        assignee: str = "AI Agent",
        tags: Optional[list] = None
    ) -> dict:
        """
        Create a new task in AppFlowy.

        Args:
            title: Task title
            description: Task description
            status: Task status (Todo, In Progress, Completed, etc.)
            priority: Task priority (High, Medium, Low)
            assignee: Person assigned to task
            tags: List of tags

        Returns:
            Created task dictionary
        """
        task_data = {
            'title': title,
            'description': description,
            'status': status,
            'priority': priority,
            'assignee': assignee,
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }

        if tags:
            task_data['tags'] = tags

        # Validate against database schema
        validated_data = self.client.validate_task_data(
            self.database_id,
            task_data
        )

        # Create task
        result = self.client.create_row(self.database_id, validated_data)

        print(f"✅ Task created: {title}")
        print(f"   ID: {result.get('id')}")
        print(f"   Status: {status}")
        print(f"   Priority: {priority}")

        return result

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> dict:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            status: New status
            description: New description
            priority: New priority
            assignee: New assignee

        Returns:
            Updated task dictionary
        """
        updates = {}

        if status:
            updates['status'] = status
        if description:
            updates['description'] = description
        if priority:
            updates['priority'] = priority
        if assignee:
            updates['assignee'] = assignee

        if status == 'Completed':
            updates['completed_at'] = datetime.utcnow().isoformat() + 'Z'

        updates['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        # Validate updates
        validated_updates = self.client.validate_task_data(
            self.database_id,
            updates
        )

        # Update task
        result = self.client.update_row(
            self.database_id,
            task_id,
            validated_updates
        )

        print(f"✅ Task updated: {task_id}")
        for key, value in validated_updates.items():
            print(f"   {key}: {value}")

        return result

    def list_recent_tasks(self, hours: int = 24, limit: int = 10) -> list:
        """
        List recently updated tasks.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of tasks to return

        Returns:
            List of task dictionaries
        """
        # Calculate timestamp
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + 'Z'

        # Get updated rows
        updated_rows = self.client.get_updated_rows(self.database_id, since)

        if not updated_rows:
            print(f"No tasks updated in last {hours} hours")
            return []

        # Get details for updated rows
        row_ids = [row['id'] for row in updated_rows[:limit]]
        tasks = self.client.get_row_detail(self.database_id, row_ids)

        return tasks

    def display_tasks(self, tasks: list):
        """Display tasks in a formatted way."""
        if not tasks:
            print("No tasks to display")
            return

        print(f"\n{'='*70}")
        print(f"{'TASKS':<70}")
        print(f"{'='*70}\n")

        for i, task in enumerate(tasks, 1):
            title = task.get('title', 'Untitled')
            status = task.get('status', 'Unknown')
            priority = task.get('priority', 'Medium')
            assignee = task.get('assignee', 'Unassigned')

            # Status emoji
            status_emoji = {
                'Todo': '📋',
                'In Progress': '🔄',
                'Completed': '✅',
                'Blocked': '🚫'
            }.get(status, '📌')

            # Priority indicator
            priority_indicator = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(priority, '⚪')

            print(f"{i}. {status_emoji} {title}")
            print(f"   Status: {status} | Priority: {priority_indicator} {priority}")
            print(f"   Assignee: {assignee}")
            print(f"   ID: {task.get('id')}")

            if task.get('description'):
                desc = task['description']
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                print(f"   Description: {desc}")

            print()


def main():
    """CLI for AppFlowy task tracking."""
    parser = argparse.ArgumentParser(
        description='Track agent tasks in AppFlowy'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create task command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('title', help='Task title')
    create_parser.add_argument('--description', '-d', default='', help='Task description')
    create_parser.add_argument(
        '--status', '-s',
        default='Todo',
        choices=['Todo', 'In Progress', 'Completed', 'Blocked'],
        help='Task status'
    )
    create_parser.add_argument(
        '--priority', '-p',
        default='Medium',
        choices=['High', 'Medium', 'Low'],
        help='Task priority'
    )
    create_parser.add_argument('--assignee', '-a', default='AI Agent', help='Task assignee')
    create_parser.add_argument('--tags', '-t', nargs='+', help='Task tags')

    # Update task command
    update_parser = subparsers.add_parser('update', help='Update an existing task')
    update_parser.add_argument('task_id', help='Task ID to update')
    update_parser.add_argument('--status', '-s', help='New status')
    update_parser.add_argument('--description', '-d', help='New description')
    update_parser.add_argument('--priority', '-p', help='New priority')
    update_parser.add_argument('--assignee', '-a', help='New assignee')

    # List tasks command
    list_parser = subparsers.add_parser('list', help='List recent tasks')
    list_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Look back this many hours (default: 24)'
    )
    list_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of tasks to show (default: 10)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        tracker = TaskTracker()

        if args.command == 'create':
            tracker.create_task(
                title=args.title,
                description=args.description,
                status=args.status,
                priority=args.priority,
                assignee=args.assignee,
                tags=args.tags
            )

        elif args.command == 'update':
            tracker.update_task(
                task_id=args.task_id,
                status=args.status,
                description=args.description,
                priority=args.priority,
                assignee=args.assignee
            )

        elif args.command == 'list':
            tasks = tracker.list_recent_tasks(hours=args.hours, limit=args.limit)
            tracker.display_tasks(tasks)

    except AppFlowyError as e:
        print(f"❌ AppFlowy error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
