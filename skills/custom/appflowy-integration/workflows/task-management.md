# Task Management Workflows

<overview>
Common patterns for creating, updating, querying, and tracking tasks in AppFlowy databases. These workflows enable efficient task management through the AppFlowy REST API.
</overview>

## Table of Contents

1. [Create Tasks](#create-tasks)
2. [Update Tasks](#update-tasks)
3. [Query Tasks](#query-tasks)
4. [Bulk Operations](#bulk-operations)
5. [Agent Task Tracking Pattern](#agent-task-tracking-pattern)
6. [Daily Standup Summary](#daily-standup-summary)
7. [Project Dashboard](#project-dashboard)

---

## Create Tasks

<create_task>
**Basic Task Creation:**

```python
from appflowy_client import AppFlowyClient

client = AppFlowyClient()

# Create a new task
task = client.create_row(
    workspace_id=client.workspace_id,
    database_id="bb7a9c66-8088-4f71-a7b7-551f4c1adc5d",  # To-dos DB
    data={
        'title': 'Implement user authentication',
        'status': 'In Progress',
        'priority': 'High',
        'assignee': 'AI Agent',
        'description': 'Add JWT-based authentication with refresh tokens',
        'due_date': '2025-12-15'
    }
)

print(f"Created task: {task['id']}")
```

**Task Creation with Field Validation:**

```python
def create_task_safe(client, database_id, task_data):
    """Create task with automatic field validation."""
    # Get database fields
    fields = client.get_database_fields(client.workspace_id, database_id)
    field_names = {f['name'] for f in fields}

    # Validate and filter task data
    validated_data = {k: v for k, v in task_data.items() if k in field_names}

    # Warn about missing fields
    missing = set(task_data.keys()) - field_names
    if missing:
        print(f"⚠️  Fields not in database: {missing}")

    # Create task
    return client.create_row(
        workspace_id=client.workspace_id,
        database_id=database_id,
        data=validated_data
    )

# Usage
task = create_task_safe(client, database_id, {
    'title': 'Review pull request #123',
    'status': 'Todo',
    'priority': 'Medium',
    'description': 'Review changes in authentication module'
})
```

**Task Creation Workflow (Full Pattern):**

```python
def create_task_workflow(client, task_info):
    """Complete workflow for creating a tracked task.

    Args:
        task_info: Dictionary with task details
            - title (required)
            - description (optional)
            - status (optional, default: 'Todo')
            - priority (optional, default: 'Medium')
            - assignee (optional)
            - due_date (optional)
            - tags (optional)
    """
    # 1. Get or verify database
    databases = client.list_databases(client.workspace_id)
    tasks_db = next((db for db in databases if db.get('name') == 'To-dos'), None)

    if not tasks_db:
        raise ValueError("To-dos database not found in workspace")

    database_id = tasks_db['id']

    # 2. Get database fields to ensure compatibility
    fields = client.get_database_fields(client.workspace_id, database_id)
    field_names = [f['name'] for f in fields]

    # 3. Prepare task data matching available fields
    task_data = {}
    field_mapping = {
        'title': 'title',
        'description': 'description',
        'status': 'status',
        'priority': 'priority',
        'assignee': 'assignee',
        'due_date': 'due_date',
        'tags': 'tags'
    }

    for task_key, field_name in field_mapping.items():
        if field_name in field_names and task_key in task_info:
            task_data[field_name] = task_info[task_key]

    # 4. Create the task
    result = client.create_row(
        workspace_id=client.workspace_id,
        database_id=database_id,
        data=task_data
    )

    return {
        'task_id': result.get('id'),
        'database_id': database_id,
        'created': True
    }

# Usage
task = create_task_workflow(client, {
    'title': 'Implement AppFlowy integration',
    'description': 'Create skill for AppFlowy API integration',
    'status': 'In Progress',
    'priority': 'High',
    'assignee': 'AI Agent',
    'tags': ['development', 'integration']
})
print(f"Created task: {task['task_id']}")
```
</create_task>

---

## Update Tasks

<update_task>
**Update Task Status:**

```python
def update_task_status(client, database_id, row_id, new_status):
    """Update task status."""
    return client.update_row(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_id=row_id,
        updates={'status': new_status}
    )

# Usage
update_task_status(client, database_id, task_id, 'Completed')
```

**Update Multiple Fields:**

```python
from datetime import datetime

def complete_task(client, database_id, row_id):
    """Mark task as completed with timestamp."""
    return client.update_row(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_id=row_id,
        updates={
            'status': 'Completed',
            'completed_at': datetime.utcnow().isoformat() + 'Z'
        }
    )

# Usage
complete_task(client, database_id, task_id)
```

**Upsert Pattern (Update or Create):**

```python
def upsert_task(client, database_id, task_data, task_title=None):
    """Update existing task or create new one if not found."""
    if task_title:
        # Try to find existing task by title
        rows = client.get_database_rows(client.workspace_id, database_id)
        row_ids = [row['id'] for row in rows]

        if row_ids:
            details = client.get_row_detail(
                workspace_id=client.workspace_id,
                database_id=database_id,
                row_ids=row_ids
            )

            # Find task with matching title
            existing_task = next(
                (t for t in details if t.get('title') == task_title),
                None
            )

            if existing_task:
                # Update existing task
                return client.update_row(
                    workspace_id=client.workspace_id,
                    database_id=database_id,
                    row_id=existing_task['id'],
                    updates=task_data
                )

    # Create new task if not found
    task_data['title'] = task_title or task_data.get('title', 'Untitled Task')
    return client.create_row(
        workspace_id=client.workspace_id,
        database_id=database_id,
        data=task_data
    )
```
</update_task>

---

## Query Tasks

<query_tasks>
**Get All Tasks:**

```python
def get_all_tasks(client, database_id):
    """Retrieve all tasks from database."""
    # Get row IDs
    rows = client.get_database_rows(client.workspace_id, database_id)
    row_ids = [row['id'] for row in rows]

    if not row_ids:
        return []

    # Get full task details
    return client.get_row_detail(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_ids=row_ids
    )

# Usage
tasks = get_all_tasks(client, database_id)
for task in tasks:
    print(f"{task.get('title')} - {task.get('status')}")
```

**Filter Tasks by Status:**

```python
def get_tasks_by_status(client, database_id, status):
    """Get tasks filtered by status."""
    tasks = get_all_tasks(client, database_id)
    return [t for t in tasks if t.get('status', '').lower() == status.lower()]

# Usage
in_progress = get_tasks_by_status(client, database_id, 'In Progress')
print(f"Found {len(in_progress)} tasks in progress")
```

**Get Recently Updated Tasks:**

```python
from datetime import datetime, timedelta

def get_recent_updates(client, database_id, hours=24):
    """Retrieve tasks updated in last N hours."""
    cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + 'Z'

    updated_rows = client.get_updated_rows(
        workspace_id=client.workspace_id,
        database_id=database_id,
        since_timestamp=cutoff_time
    )

    if not updated_rows:
        return []

    row_ids = [row['id'] for row in updated_rows]
    return client.get_row_detail(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_ids=row_ids
    )

# Usage
recent_tasks = get_recent_updates(client, database_id, hours=24)
```

**Search Tasks by Title:**

```python
def search_tasks(client, database_id, search_term):
    """Search tasks by title (case-insensitive)."""
    tasks = get_all_tasks(client, database_id)
    search_lower = search_term.lower()
    return [
        t for t in tasks
        if search_lower in t.get('title', '').lower()
    ]

# Usage
auth_tasks = search_tasks(client, database_id, 'authentication')
```
</query_tasks>

---

## Bulk Operations

<bulk_operations>
**Bulk Status Update:**

```python
def bulk_update_status(client, database_id, task_ids, new_status):
    """Update status for multiple tasks."""
    results = []
    for task_id in task_ids:
        try:
            result = client.update_row(
                workspace_id=client.workspace_id,
                database_id=database_id,
                row_id=task_id,
                updates={'status': new_status}
            )
            results.append({'task_id': task_id, 'success': True})
        except Exception as e:
            results.append({'task_id': task_id, 'success': False, 'error': str(e)})

    return results

# Usage
task_ids = ['task1', 'task2', 'task3']
results = bulk_update_status(client, database_id, task_ids, 'Completed')
print(f"Updated {sum(1 for r in results if r['success'])} tasks")
```

**Bulk Create Tasks:**

```python
def bulk_create_tasks(client, database_id, tasks_list):
    """Create multiple tasks at once."""
    results = []
    for task_data in tasks_list:
        try:
            result = client.create_row(
                workspace_id=client.workspace_id,
                database_id=database_id,
                data=task_data
            )
            results.append({
                'task_id': result['id'],
                'title': task_data.get('title'),
                'success': True
            })
        except Exception as e:
            results.append({
                'title': task_data.get('title'),
                'success': False,
                'error': str(e)
            })

    return results

# Usage
tasks = [
    {'title': 'Task 1', 'status': 'Todo', 'priority': 'High'},
    {'title': 'Task 2', 'status': 'Todo', 'priority': 'Medium'},
    {'title': 'Task 3', 'status': 'In Progress', 'priority': 'Low'}
]
results = bulk_create_tasks(client, database_id, tasks)
```
</bulk_operations>

---

## Agent Task Tracking Pattern

<agent_task_tracking>
**Track Agent Work Automatically:**

```python
#!/usr/bin/env python3
"""
Agent task tracking - tracks agent work in AppFlowy for team visibility.
"""
import os
from datetime import datetime
from appflowy_client import AppFlowyClient

class AgentTaskTracker:
    def __init__(self):
        self.client = AppFlowyClient()
        self.database_id = os.getenv('APPFLOWY_TODOS_DB_ID')
        self.current_task_id = None

    def start_task(self, task_description, priority='Medium'):
        """Start tracking a new task."""
        task_data = {
            'title': task_description,
            'status': 'In Progress',
            'assignee': 'AI Agent',
            'priority': priority,
            'tags': ['automated', 'agent-work'],
            'started_at': datetime.utcnow().isoformat() + 'Z'
        }

        result = self.client.create_row(
            workspace_id=self.client.workspace_id,
            database_id=self.database_id,
            data=task_data
        )

        self.current_task_id = result['id']
        print(f"✅ Started tracking: {task_description}")
        print(f"   Task ID: {self.current_task_id}")
        return self.current_task_id

    def update_progress(self, progress_note):
        """Add progress update to current task."""
        if not self.current_task_id:
            print("⚠️  No active task to update")
            return

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        update_text = f"[{timestamp}] {progress_note}"

        self.client.update_row(
            workspace_id=self.client.workspace_id,
            database_id=self.database_id,
            row_id=self.current_task_id,
            updates={'description': update_text}
        )
        print(f"📝 Progress updated: {progress_note}")

    def complete_task(self, final_note=None):
        """Mark current task as completed."""
        if not self.current_task_id:
            print("⚠️  No active task to complete")
            return

        updates = {
            'status': 'Completed',
            'completed_at': datetime.utcnow().isoformat() + 'Z'
        }

        if final_note:
            updates['description'] = f"Completed: {final_note}"

        self.client.update_row(
            workspace_id=self.client.workspace_id,
            database_id=self.database_id,
            row_id=self.current_task_id,
            updates=updates
        )

        print(f"✅ Task completed: {self.current_task_id}")
        self.current_task_id = None

# Usage Example
tracker = AgentTaskTracker()

# Start a task
task_id = tracker.start_task("Implement AppFlowy integration skill", priority='High')

# Update progress
tracker.update_progress("Created SKILL.md with core patterns")
tracker.update_progress("Implemented Python client library")
tracker.update_progress("Added workflow documentation")

# Complete task
tracker.complete_task("All components implemented and tested")
```

**Automatic Task Tracking Decorator:**

```python
def track_in_appflowy(task_description, priority='Medium'):
    """Decorator to automatically track function execution as AppFlowy task."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = AgentTaskTracker()
            task_id = tracker.start_task(f"{task_description}: {func.__name__}", priority)

            try:
                result = func(*args, **kwargs)
                tracker.complete_task(f"Successfully executed {func.__name__}")
                return result
            except Exception as e:
                tracker.update_progress(f"Error: {str(e)}")
                client = AppFlowyClient()
                client.update_row(
                    workspace_id=client.workspace_id,
                    database_id=os.getenv('APPFLOWY_TODOS_DB_ID'),
                    row_id=task_id,
                    updates={'status': 'Failed'}
                )
                raise

        return wrapper
    return decorator

# Usage
@track_in_appflowy("Deploy infrastructure", priority='High')
def deploy_server(server_config):
    # ... deployment logic ...
    pass
```
</agent_task_tracking>

---

## Daily Standup Summary

<daily_standup>
**Generate Standup Report:**

```python
def generate_standup_summary(client, database_id, hours=24):
    """Generate daily standup summary from AppFlowy tasks.

    Returns summary of tasks by status for standup meetings.
    """
    from datetime import datetime, timedelta

    # Get tasks updated in last N hours
    cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + 'Z'
    updated_rows = client.get_updated_rows(
        workspace_id=client.workspace_id,
        database_id=database_id,
        since_timestamp=cutoff_time
    )

    if not updated_rows:
        return "No task updates in the last 24 hours"

    # Get full details
    row_ids = [row['id'] for row in updated_rows]
    details = client.get_row_detail(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_ids=row_ids
    )

    # Organize by status
    summary = {
        'completed': [],
        'in_progress': [],
        'blocked': [],
        'todo': []
    }

    for task in details:
        status = task.get('status', '').lower()
        title = task.get('title', 'Untitled')
        priority = task.get('priority', 'Medium')
        assignee = task.get('assignee', 'Unassigned')

        task_info = {
            'title': title,
            'priority': priority,
            'assignee': assignee
        }

        if 'complete' in status or 'done' in status:
            summary['completed'].append(task_info)
        elif 'progress' in status or 'doing' in status:
            summary['in_progress'].append(task_info)
        elif 'block' in status:
            summary['blocked'].append(task_info)
        else:
            summary['todo'].append(task_info)

    # Format output
    output = ["=" * 60, "DAILY STANDUP SUMMARY", "=" * 60]
    output.append(f"\nPeriod: Last {hours} hours")
    output.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    if summary['completed']:
        output.append(f"✅ Completed ({len(summary['completed'])}):")
        for task in summary['completed']:
            output.append(f"  • {task['title']} [{task['priority']}] - {task['assignee']}")

    if summary['in_progress']:
        output.append(f"\n🔄 In Progress ({len(summary['in_progress'])}):")
        for task in summary['in_progress']:
            output.append(f"  • {task['title']} [{task['priority']}] - {task['assignee']}")

    if summary['blocked']:
        output.append(f"\n🚫 Blocked ({len(summary['blocked'])}):")
        for task in summary['blocked']:
            output.append(f"  • {task['title']} [{task['priority']}] - {task['assignee']}")

    if summary['todo']:
        output.append(f"\n📋 Todo ({len(summary['todo'])}):")
        for task in summary['todo']:
            output.append(f"  • {task['title']} [{task['priority']}] - {task['assignee']}")

    output.append("\n" + "=" * 60)

    return '\n'.join(output)

# Usage
standup = generate_standup_summary(client, database_id, hours=24)
print(standup)
```

**Send Standup via Slack/Email:**

```python
def send_standup_notification(client, database_id, notification_method='print'):
    """Generate and send standup summary."""
    summary = generate_standup_summary(client, database_id)

    if notification_method == 'slack':
        # Send to Slack (requires slack_sdk)
        import slack_sdk
        slack_client = slack_sdk.WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        slack_client.chat_postMessage(
            channel='#standup',
            text=f"```{summary}```"
        )
    elif notification_method == 'email':
        # Send via email (requires smtplib)
        import smtplib
        from email.mime.text import MIMEText
        # ... email sending logic ...
    else:
        print(summary)
```
</daily_standup>

---

## Project Dashboard

<project_dashboard>
**Generate Comprehensive Dashboard:**

```python
def generate_project_dashboard(client, database_id):
    """Create comprehensive project status dashboard."""
    # Get all project tasks
    rows = client.get_database_rows(client.workspace_id, database_id)
    row_ids = [r['id'] for r in rows]

    if not row_ids:
        return "No tasks found in database"

    tasks = client.get_row_detail(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_ids=row_ids
    )

    # Analyze status distribution
    status_counts = {}
    priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    assignee_workload = {}

    for task in tasks:
        # Count by status
        status = task.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

        # Count by priority
        priority = task.get('priority', 'Medium')
        if priority in priority_counts:
            priority_counts[priority] += 1

        # Track assignee workload
        assignee = task.get('assignee', 'Unassigned')
        assignee_workload[assignee] = assignee_workload.get(assignee, 0) + 1

    # Calculate completion percentage
    completed = status_counts.get('Completed', 0) + status_counts.get('Done', 0)
    total = len(tasks)
    completion_rate = (completed / total * 100) if total > 0 else 0

    # Generate dashboard
    dashboard = [
        "=" * 60,
        "PROJECT DASHBOARD",
        "=" * 60,
        f"\n📊 Total Tasks: {total}",
        f"✅ Completion Rate: {completion_rate:.1f}%",
        "\n📈 Status Distribution:"
    ]

    for status, count in sorted(status_counts.items()):
        percentage = (count / total) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length + '░' * (50 - bar_length)
        dashboard.append(f"  {status:15s}: {count:3d} ({percentage:5.1f}%) {bar}")

    dashboard.append("\n🎯 Priority Breakdown:")
    for priority, count in priority_counts.items():
        dashboard.append(f"  {priority:8s}: {count:3d}")

    dashboard.append("\n👥 Assignee Workload:")
    for assignee, count in sorted(assignee_workload.items(), key=lambda x: x[1], reverse=True):
        dashboard.append(f"  {assignee:20s}: {count:3d} tasks")

    dashboard.append("\n" + "=" * 60)

    return '\n'.join(dashboard)

# Usage
dashboard = generate_project_dashboard(client, database_id)
print(dashboard)
```

**Expected Output:**
```
============================================================
PROJECT DASHBOARD
============================================================

📊 Total Tasks: 42
✅ Completion Rate: 35.7%

📈 Status Distribution:
  Completed      :  15 ( 35.7%) ███████████████████████████████████░░░░░░░░░░░░░░░
  In Progress    :  18 ( 42.9%) █████████████████████████████████████████░░░░░░░░░
  Todo           :   7 ( 16.7%) ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  Blocked        :   2 (  4.8%) ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

🎯 Priority Breakdown:
  High    :   8
  Medium  :  25
  Low     :   9

👥 Assignee Workload:
  AI Agent            :  12 tasks
  John Doe            :  10 tasks
  Jane Smith          :   8 tasks
  Unassigned          :  12 tasks

============================================================
```
</project_dashboard>

---

## Project Status Sync

<project_sync>
**Sync Local Tasks with AppFlowy:**

```python
def sync_project_status(client, database_id, local_tasks):
    """Sync local task status with AppFlowy.

    Args:
        database_id: AppFlowy database ID
        local_tasks: List of local task objects with id and status
    """
    # Get current state from AppFlowy
    appflowy_rows = client.get_database_rows(client.workspace_id, database_id)
    row_ids = [row['id'] for row in appflowy_rows]

    if not row_ids:
        return {'synced': 0, 'task_ids': []}

    details = client.get_row_detail(
        workspace_id=client.workspace_id,
        database_id=database_id,
        row_ids=row_ids
    )

    # Create mapping of existing tasks
    appflowy_tasks = {task['id']: task for task in details}

    # Update tasks that exist in both systems
    updates = []
    for local_task in local_tasks:
        if local_task['id'] in appflowy_tasks:
            appflowy_status = appflowy_tasks[local_task['id']].get('status')
            if appflowy_status != local_task['status']:
                client.update_row(
                    workspace_id=client.workspace_id,
                    database_id=database_id,
                    row_id=local_task['id'],
                    updates={'status': local_task['status']}
                )
                updates.append(local_task['id'])

    return {
        'synced': len(updates),
        'task_ids': updates
    }

# Usage
local_tasks = [
    {'id': 'task1', 'status': 'Completed'},
    {'id': 'task2', 'status': 'In Progress'},
    {'id': 'task3', 'status': 'Blocked'}
]
result = sync_project_status(client, database_id, local_tasks)
print(f"Synced {result['synced']} tasks")
```
</project_sync>

---

## Related Documentation

- **API Reference**: See `references/api-reference.md` for detailed API endpoint documentation
- **Troubleshooting**: See `workflows/troubleshooting.md` for common task management issues
- **Workspace Operations**: See `workflows/workspace-operations.md` for database setup
