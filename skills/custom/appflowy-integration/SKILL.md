---
name: appflowy-integration
description: Integration with AppFlowy project management tool for task tracking, database management, and workspace organization. Use when managing project tasks, creating databases, or organizing work in AppFlowy.
version: 1.0.0
author: AI Agents Team
category: custom
token_estimate: ~3800
---

# AppFlowy Integration Skill

## Purpose

This skill enables agents to interact with AppFlowy, an open-source collaborative workspace and project management tool. It provides capabilities for managing tasks, databases, workspaces, and project organization through AppFlowy's REST API.

## When to Use This Skill

Use this skill when:

- Creating or updating tasks in AppFlowy databases
- Managing project workspaces and folders
- Organizing work items in AppFlowy Kanban boards or database views
- Syncing agent work with AppFlowy project tracking
- Automating project management workflows
- Creating documentation in AppFlowy workspaces

Do NOT use this skill when:

- Working with other project management tools (Jira, Asana, etc.)
- Managing local files without AppFlowy integration
- Tasks don't require project management tracking

## Prerequisites

Before using this skill, ensure:

- AppFlowy is deployed (self-hosted or cloud)
- API endpoint URL is configured
- Authentication credentials (JWT token or OAuth) are available
- Workspace ID is known for operations
- Python `requests` library is installed for API calls

## Instructions

### Step 1: Configure AppFlowy Connection

Set up connection to your AppFlowy instance:

**Environment Configuration:**
```bash
# Set environment variables
export APPFLOWY_API_URL="https://your-appflowy-instance.com"
export APPFLOWY_API_TOKEN="your_jwt_token_here"
export APPFLOWY_WORKSPACE_ID="your_workspace_id"
```

**For Self-Hosted Deployments:**
- Synology NAS: Access via `http://nas-ip:port` or configured domain
- AI Home Server: Access via local network or reverse proxy
- Ensure firewall rules allow API access

**Authentication Methods:**

1. **JWT Token Authentication (Recommended for automation):**
```bash
# Obtain JWT token via API
curl -X POST "https://your-appflowy-instance.com/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password",
    "grant_type": "password"
  }'
```

2. **OAuth 2.0 (For interactive sessions):**
```bash
# Redirect to OAuth endpoint
GET /web-api/oauth-redirect/token
```

**Python Configuration:**
```python
import os
import requests

class AppFlowyClient:
    def __init__(self):
        self.api_url = os.getenv('APPFLOWY_API_URL')
        self.token = os.getenv('APPFLOWY_API_TOKEN')
        self.workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated API request."""
        url = f"{self.api_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
```

### Step 2: Workspace and Database Operations

Interact with workspaces and databases:

**List All Workspaces:**
```python
def list_workspaces(client):
    """Retrieve all available workspaces."""
    return client._make_request('GET', '/api/workspace')

# Usage
workspaces = list_workspaces(client)
print(f"Found {len(workspaces)} workspaces")
```

**Get Workspace Folder Structure:**
```python
def get_workspace_folders(client, workspace_id):
    """Get folder structure for a workspace."""
    endpoint = f'/api/workspace/{workspace_id}/folder'
    return client._make_request('GET', endpoint)

# Usage
folders = get_workspace_folders(client, client.workspace_id)
```

**List Databases in Workspace:**
```python
def list_databases(client, workspace_id):
    """Retrieve all databases in a workspace."""
    endpoint = f'/api/workspace/{workspace_id}/database'
    return client._make_request('GET', endpoint)

# Usage
databases = list_databases(client, client.workspace_id)
for db in databases:
    print(f"Database: {db.get('name')} (ID: {db.get('id')})")
```

**Get Database Fields:**
```python
def get_database_fields(client, workspace_id, database_id):
    """Fetch field definitions for a database."""
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/fields'
    return client._make_request('GET', endpoint)

# Usage
fields = get_database_fields(client, client.workspace_id, database_id)
for field in fields:
    print(f"Field: {field.get('name')} - Type: {field.get('type')}")
```

### Step 3: Managing Database Rows (Tasks/Items)

Create, read, and update rows in AppFlowy databases:

**Get All Rows:**
```python
def get_database_rows(client, workspace_id, database_id):
    """Retrieve row IDs from a database."""
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
    return client._make_request('GET', endpoint)

# Usage
rows = get_database_rows(client, client.workspace_id, database_id)
```

**Get Row Details:**
```python
def get_row_detail(client, workspace_id, database_id, row_ids):
    """Get comprehensive information for specific rows.

    Args:
        row_ids: List of row IDs to fetch
    """
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row/detail'
    params = {'row_ids': ','.join(row_ids)}
    return client._make_request('GET', endpoint, params=params)

# Usage
row_details = get_row_detail(client, client.workspace_id, database_id, ['row1', 'row2'])
```

**Create New Row (Task):**
```python
def create_row(client, workspace_id, database_id, data):
    """Add a new row to database.

    Args:
        data: Dictionary with field values
        Example: {
            "title": "Implement user authentication",
            "status": "In Progress",
            "priority": "High",
            "assignee": "Agent",
            "due_date": "2025-12-01"
        }
    """
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
    return client._make_request('POST', endpoint, json=data)

# Usage - Create a task
task_data = {
    "title": "Review pull request #123",
    "status": "Todo",
    "priority": "Medium",
    "description": "Review changes in authentication module"
}
new_task = create_row(client, client.workspace_id, database_id, task_data)
print(f"Created task with ID: {new_task.get('id')}")
```

**Update Row (Upsert):**
```python
def update_row(client, workspace_id, database_id, row_id, updates):
    """Update existing row or create if doesn't exist.

    Args:
        row_id: ID of row to update
        updates: Dictionary of field updates
    """
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
    data = {
        'row_id': row_id,
        **updates
    }
    return client._make_request('PUT', endpoint, json=data)

# Usage - Update task status
update_row(client, client.workspace_id, database_id, task_id, {
    'status': 'Completed',
    'completed_at': '2025-11-22T10:30:00Z'
})
```

**Get Recently Updated Rows:**
```python
def get_updated_rows(client, workspace_id, database_id, since_timestamp=None):
    """Retrieve recently modified rows.

    Args:
        since_timestamp: ISO timestamp to get changes since
    """
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row/updated'
    params = {'since': since_timestamp} if since_timestamp else {}
    return client._make_request('GET', endpoint, params=params)

# Usage - Get rows updated in last hour
from datetime import datetime, timedelta
one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
recent_updates = get_updated_rows(client, client.workspace_id, database_id, one_hour_ago)
```

### Step 4: Common Workflow Patterns

**Pattern 1: Task Creation Workflow**
```python
def create_task_workflow(client, task_info):
    """Complete workflow for creating a tracked task.

    Args:
        task_info: Dictionary with task details
    """
    # 1. Get or create appropriate database
    databases = list_databases(client, client.workspace_id)
    tasks_db = next((db for db in databases if db.get('name') == 'Tasks'), None)

    if not tasks_db:
        raise ValueError("Tasks database not found in workspace")

    database_id = tasks_db['id']

    # 2. Get database fields to ensure compatibility
    fields = get_database_fields(client, client.workspace_id, database_id)
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
    result = create_row(client, client.workspace_id, database_id, task_data)

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
```

**Pattern 2: Project Status Sync**
```python
def sync_project_status(client, database_id, local_tasks):
    """Sync local task status with AppFlowy.

    Args:
        database_id: AppFlowy database ID
        local_tasks: List of local task objects with id and status
    """
    # Get current state from AppFlowy
    appflowy_rows = get_database_rows(client, client.workspace_id, database_id)
    row_ids = [row['id'] for row in appflowy_rows]

    if row_ids:
        details = get_row_detail(client, client.workspace_id, database_id, row_ids)

        # Create mapping of existing tasks
        appflowy_tasks = {task['id']: task for task in details}

        # Update tasks that exist in both systems
        updates = []
        for local_task in local_tasks:
            if local_task['id'] in appflowy_tasks:
                appflowy_status = appflowy_tasks[local_task['id']].get('status')
                if appflowy_status != local_task['status']:
                    update_row(client, client.workspace_id, database_id,
                             local_task['id'], {'status': local_task['status']})
                    updates.append(local_task['id'])

        return {
            'synced': len(updates),
            'task_ids': updates
        }
```

**Pattern 3: Daily Standup Summary**
```python
def generate_standup_summary(client, database_id):
    """Generate daily standup summary from AppFlowy tasks.

    Returns summary of tasks by status for standup meetings.
    """
    from datetime import datetime, timedelta

    # Get tasks updated in last 24 hours
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
    updated_rows = get_updated_rows(client, client.workspace_id, database_id, yesterday)

    if not updated_rows:
        return "No task updates in the last 24 hours"

    # Get full details
    row_ids = [row['id'] for row in updated_rows]
    details = get_row_detail(client, client.workspace_id, database_id, row_ids)

    # Organize by status
    summary = {
        'completed': [],
        'in_progress': [],
        'blocked': []
    }

    for task in details:
        status = task.get('status', '').lower()
        title = task.get('title', 'Untitled')

        if 'complete' in status or 'done' in status:
            summary['completed'].append(title)
        elif 'progress' in status or 'doing' in status:
            summary['in_progress'].append(title)
        elif 'block' in status:
            summary['blocked'].append(title)

    # Format output
    output = ["Daily Standup Summary", "=" * 40]

    if summary['completed']:
        output.append(f"\n✅ Completed ({len(summary['completed'])}):")
        output.extend(f"  - {task}" for task in summary['completed'])

    if summary['in_progress']:
        output.append(f"\n🔄 In Progress ({len(summary['in_progress'])}):")
        output.extend(f"  - {task}" for task in summary['in_progress'])

    if summary['blocked']:
        output.append(f"\n🚫 Blocked ({len(summary['blocked'])}):")
        output.extend(f"  - {task}" for task in summary['blocked'])

    return '\n'.join(output)

# Usage
standup = generate_standup_summary(client, database_id)
print(standup)
```

**Pattern 4: New Project Workspace Setup**
```python
def create_project_workspace(client, project_name, team_members=None):
    """
    Create a new workspace for a project with initial setup.

    This pattern is useful when starting a new project and you want
    to automatically set up the AppFlowy workspace structure.

    Args:
        client: AppFlowy client instance
        project_name: Name of the new project
        team_members: List of team member emails to add
    """
    from datetime import datetime

    # Note: Workspace creation API may require admin permissions
    # Check AppFlowy API documentation for latest endpoint

    # 1. Create workspace (if API supports it)
    # For now, this assumes workspace exists and we find it by name
    workspaces = client.list_workspaces()
    workspace = next(
        (w for w in workspaces if w.get('name') == project_name),
        None
    )

    if not workspace:
        print(f"⚠️  Workspace '{project_name}' not found.")
        print("Please create it manually in AppFlowy UI, then run setup again.")
        return None

    workspace_id = workspace['id']
    print(f"✅ Using workspace: {project_name} (ID: {workspace_id})")

    # 2. Check if Tasks database exists, create note if it doesn't
    databases = client.list_databases(workspace_id)
    tasks_db = next((db for db in databases if db.get('name') == 'Tasks'), None)

    if not tasks_db:
        print("⚠️  'Tasks' database not found in workspace.")
        print("Please create a 'Tasks' database in AppFlowy UI with fields:")
        print("  - title (text)")
        print("  - status (select: Todo, In Progress, Completed, Blocked)")
        print("  - priority (select: High, Medium, Low)")
        print("  - assignee (text)")
        print("  - due_date (date)")
        print("  - description (text)")
        return None
    else:
        print(f"✅ Tasks database found (ID: {tasks_db['id']})")

    # 3. Create initial project setup task
    setup_task = {
        'title': f'Project Setup: {project_name}',
        'description': f'Initialize project workspace and documentation. Created: {datetime.utcnow().isoformat()}',
        'status': 'In Progress',
        'priority': 'High',
        'assignee': 'Project Lead'
    }

    try:
        task = client.create_row(tasks_db['id'], setup_task, workspace_id)
        print(f"✅ Created initial setup task (ID: {task.get('id')})")
    except Exception as e:
        print(f"⚠️  Could not create setup task: {e}")

    # 4. Return workspace configuration
    return {
        'workspace_id': workspace_id,
        'workspace_name': project_name,
        'tasks_database_id': tasks_db['id'],
        'setup_complete': True,
        'message': f'Workspace ready for {project_name}'
    }

# Usage
config = create_project_workspace(client, "New AI Project", ["dev1@team.com", "dev2@team.com"])
if config:
    print(f"\n📋 Save these values:")
    print(f"export APPFLOWY_WORKSPACE_ID='{config['workspace_id']}'")
    print(f"export APPFLOWY_TASKS_DB_ID='{config['tasks_database_id']}'")
```

### Step 5: Managing AppFlowy Backend Server

Start, stop, and monitor your self-hosted AppFlowy instance:

**Start Backend Server:**

```bash
# Using Docker Compose
cd /path/to/appflowy-deploy
docker-compose up -d

# Check status
docker-compose ps

# View startup logs
docker-compose logs -f appflowy

# Wait for healthy status
docker-compose ps | grep appflowy | grep healthy
```

**Stop Backend Server:**

```bash
# Graceful shutdown
docker-compose down

# Stop but keep data
docker-compose stop

# Stop and remove volumes (⚠️ deletes all data!)
docker-compose down -v
```

**Monitor Server:**

```bash
# View real-time logs
docker-compose logs -f

# Check resource usage
docker stats appflowy appflowy-db

# Check API health
curl http://localhost:8080/health

# Test workspace endpoint
curl -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  http://localhost:8080/api/workspace
```

**Server Management Script:**

```bash
#!/bin/bash
# save as: scripts/manage_server.sh

COMPOSE_FILE="/path/to/docker-compose.yml"

case "$1" in
  start)
    echo "🚀 Starting AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" up -d
    echo "⏳ Waiting for server to be healthy..."
    sleep 10
    docker-compose -f "$COMPOSE_FILE" ps
    ;;

  stop)
    echo "🛑 Stopping AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" down
    ;;

  restart)
    echo "🔄 Restarting AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" restart
    ;;

  status)
    echo "📊 AppFlowy server status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo -e "\n💾 Resource usage:"
    docker stats --no-stream appflowy appflowy-db
    ;;

  logs)
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
    ;;

  health)
    echo "🏥 Health check:"
    curl -s http://localhost:8080/health | jq . || echo "API not responding"
    ;;

  backup)
    BACKUP_DIR="/path/to/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    echo "💾 Backing up database..."
    docker-compose -f "$COMPOSE_FILE" exec -T postgres \
      pg_dump -U appflowy_user appflowy | \
      gzip > "${BACKUP_DIR}/appflowy_${DATE}.sql.gz"
    echo "✅ Backup saved: ${BACKUP_DIR}/appflowy_${DATE}.sql.gz"
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|status|logs|health|backup}"
    exit 1
    ;;
esac
```

**Automatic Startup on Boot:**

```bash
# Create systemd service (Linux)
sudo nano /etc/systemd/system/appflowy.service
```

```ini
[Unit]
Description=AppFlowy Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/appflowy-deploy
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl enable appflowy.service
sudo systemctl start appflowy.service

# Check status
sudo systemctl status appflowy.service
```

**Synology NAS Auto-Start:**

1. Open Container Manager
2. Select AppFlowy containers
3. Settings → Enable "Auto-restart"
4. Or use Task Scheduler:
   - Create triggered task
   - Trigger: Boot-up
   - Command: `docker-compose -f /volume1/docker/appflowy/docker-compose.yml up -d`

**Troubleshooting Server Issues:**

```bash
# Check if port is already in use
netstat -tuln | grep 8080
lsof -i :8080

# Check Docker service
sudo systemctl status docker

# Verify container health
docker inspect appflowy | grep -A 10 Health

# Reset everything (⚠️ destroys data)
docker-compose down -v
docker-compose up -d
```

### Step 6: Error Handling and Best Practices

**Robust Error Handling:**
```python
import logging
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

def safe_api_call(func):
    """Decorator for safe API calls with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed - check API token")
                raise Exception("AppFlowy authentication failed")
            elif e.response.status_code == 403:
                logger.error("Permission denied - check workspace access")
                raise Exception("Permission denied for AppFlowy resource")
            elif e.response.status_code == 404:
                logger.error(f"Resource not found: {e.request.url}")
                raise Exception("AppFlowy resource not found")
            else:
                logger.error(f"API error: {e}")
                raise
        except RequestException as e:
            logger.error(f"Network error connecting to AppFlowy: {e}")
            raise Exception("Failed to connect to AppFlowy instance")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    return wrapper

# Apply to API methods
@safe_api_call
def create_row_safe(client, workspace_id, database_id, data):
    return create_row(client, workspace_id, database_id, data)
```

**Rate Limiting:**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    """Rate limit API calls to avoid overwhelming server."""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_minute=30)
def create_row_rate_limited(client, workspace_id, database_id, data):
    return create_row(client, workspace_id, database_id, data)
```

## Best Practices

### 1. Secure Credential Management

**Never hardcode credentials**. Use environment variables or secure credential storage.

**Example using python-dotenv:**
```python
from dotenv import load_dotenv
load_dotenv()

# Credentials loaded from .env file
api_token = os.getenv('APPFLOWY_API_TOKEN')
```

### 2. Cache Workspace and Database IDs

Avoid repeated lookups of workspace and database IDs:

```python
class AppFlowyManager:
    def __init__(self):
        self.client = AppFlowyClient()
        self._workspace_cache = None
        self._database_cache = {}

    def get_workspace_id(self):
        if not self._workspace_cache:
            workspaces = list_workspaces(self.client)
            self._workspace_cache = workspaces[0]['id']
        return self._workspace_cache

    def get_database_id(self, database_name):
        if database_name not in self._database_cache:
            databases = list_databases(self.client, self.get_workspace_id())
            db = next((d for d in databases if d['name'] == database_name), None)
            if db:
                self._database_cache[database_name] = db['id']
        return self._database_cache.get(database_name)
```

### 3. Validate Field Compatibility

Always check database fields before inserting data:

```python
def validate_task_data(client, workspace_id, database_id, task_data):
    """Ensure task data matches database schema."""
    fields = get_database_fields(client, workspace_id, database_id)
    field_names = {f['name'] for f in fields}

    # Remove fields that don't exist in database
    validated = {k: v for k, v in task_data.items() if k in field_names}

    # Warn about missing fields
    missing = set(task_data.keys()) - field_names
    if missing:
        logger.warning(f"Fields not in database: {missing}")

    return validated
```

### 4. Degree of Freedom

**Medium Freedom**: Follow authentication and API endpoint patterns exactly. Implement error handling and rate limiting. Customize workflow functions based on your project needs.

### 5. Token Efficiency

This skill uses approximately **3,800 tokens** when fully loaded.

**Optimization Strategy:**
- Core instructions: Always loaded (~2,500 tokens)
- Examples and patterns: Load for reference (~1,000 tokens)
- Helper scripts: Load on-demand (see scripts/ directory)

## Common Pitfalls

### Pitfall 1: Expired Authentication Tokens

**What Happens:** API calls fail with 401 Unauthorized after token expires.

**How to Avoid:**
- Implement token refresh logic
- Monitor token expiration
- Re-authenticate automatically

**Solution:**
```python
def refresh_token_if_needed(client):
    """Check and refresh token if expiring soon."""
    # Implement token expiration check and refresh
    pass
```

### Pitfall 2: Workspace/Database ID Confusion

**What Happens:** Operations fail because wrong workspace or database ID is used.

**How to Avoid:**
- List and verify resources before operations
- Use descriptive variable names
- Cache IDs after first retrieval

### Pitfall 3: Network Issues with Self-Hosted Instances

**What Happens:** Cannot reach AppFlowy instance on local network.

**How to Avoid:**
- Verify network connectivity
- Check firewall rules
- Use proper URL format (http:// vs https://)
- Test with curl before implementing

**Diagnostic:**
```bash
# Test connectivity
curl -v http://your-nas-ip:port/api/workspace

# Check if service is running
ping your-nas-ip
```

## Self-Hosted Deployment Guide

### Synology NAS (DS 923+) Deployment

**Option 1: Docker Container**
```bash
# SSH into Synology NAS
ssh admin@nas-ip

# Pull AppFlowy image (check AppFlowy docs for latest image)
docker pull appflowy/appflowy-cloud:latest

# Run container
docker run -d \
  --name appflowy \
  -p 8080:80 \
  -v /volume1/appflowy/data:/data \
  appflowy/appflowy-cloud:latest

# Verify running
docker ps | grep appflowy
```

**Option 2: Using Container Manager UI**
1. Open Synology Container Manager
2. Search for "appflowy" in Registry
3. Download latest image
4. Create container with port mapping (8080:80)
5. Set volume for data persistence
6. Start container

**Access:**
- Internal: `http://nas-ip:8080`
- External: Set up reverse proxy in Synology for HTTPS

### AI Home Server Deployment

**Using Docker Compose:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  appflowy:
    image: appflowy/appflowy-cloud:latest
    container_name: appflowy
    ports:
      - "8080:80"
    volumes:
      - ./appflowy-data:/data
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appflowy
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: appflowy-db
    environment:
      - POSTGRES_DB=appflowy
      - POSTGRES_USER=appflowy_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
```

**Deploy:**
```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f appflowy

# Access at http://localhost:8080
```

## Examples

### Example 1: Agent Task Tracking

**Context:** Agent needs to track its work in AppFlowy for team visibility.

**Implementation:**
```python
#!/usr/bin/env python3
"""
Agent task tracking example - tracks agent work in AppFlowy
"""
import os
from appflowy_client import AppFlowyClient, create_task_workflow

def track_agent_task(task_description, status="In Progress"):
    """Create or update task for agent work."""
    client = AppFlowyClient()

    task_info = {
        'title': task_description,
        'status': status,
        'assignee': 'AI Agent',
        'priority': 'Medium',
        'tags': ['automated', 'agent-work']
    }

    result = create_task_workflow(client, task_info)
    print(f"✅ Task tracked in AppFlowy: {result['task_id']}")
    return result['task_id']

# Usage in agent workflow
task_id = track_agent_task("Implementing AppFlowy integration skill")

# Later, update status
from appflowy_client import update_row, AppFlowyClient
client = AppFlowyClient()
update_row(client, client.workspace_id, database_id, task_id, {
    'status': 'Completed',
    'description': 'Successfully implemented AppFlowy skill with full API coverage'
})
```

### Example 2: Automated Project Dashboard

**Context:** Generate project status dashboard from AppFlowy data.

**Implementation:**
```python
def generate_project_dashboard(client, project_database_id):
    """Create comprehensive project status dashboard."""
    # Get all project tasks
    rows = get_database_rows(client, client.workspace_id, project_database_id)
    row_ids = [r['id'] for r in rows]
    tasks = get_row_detail(client, client.workspace_id, project_database_id, row_ids)

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

    # Generate dashboard
    dashboard = [
        "=" * 60,
        "PROJECT DASHBOARD",
        "=" * 60,
        f"\n📊 Total Tasks: {len(tasks)}",
        "\n📈 Status Distribution:"
    ]

    for status, count in sorted(status_counts.items()):
        percentage = (count / len(tasks)) * 100
        dashboard.append(f"  {status}: {count} ({percentage:.1f}%)")

    dashboard.append("\n🎯 Priority Breakdown:")
    for priority, count in priority_counts.items():
        dashboard.append(f"  {priority}: {count}")

    dashboard.append("\n👥 Assignee Workload:")
    for assignee, count in sorted(assignee_workload.items(), key=lambda x: x[1], reverse=True):
        dashboard.append(f"  {assignee}: {count} tasks")

    return '\n'.join(dashboard)

# Usage
dashboard = generate_project_dashboard(client, project_db_id)
print(dashboard)
```

**Expected Output:**
```
============================================================
PROJECT DASHBOARD
============================================================

📊 Total Tasks: 42

📈 Status Distribution:
  Completed: 15 (35.7%)
  In Progress: 18 (42.9%)
  Todo: 7 (16.7%)
  Blocked: 2 (4.8%)

🎯 Priority Breakdown:
  High: 8
  Medium: 25
  Low: 9

👥 Assignee Workload:
  AI Agent: 12 tasks
  John Doe: 10 tasks
  Jane Smith: 8 tasks
  Unassigned: 12 tasks
```

## Related Skills

This skill works well with:

- **api-endpoint-creator**: When building custom integrations with AppFlowy
- **database-migration**: When setting up AppFlowy database schemas
- **incident-response**: Track incidents in AppFlowy
- **deployment-workflow**: Track deployment tasks in AppFlowy

## Integration Notes

### Working with Other Tools

**Zapier Integration:**
AppFlowy supports Zapier, enabling no-code automation between AppFlowy and 5,000+ apps.

**GitHub Integration:**
Combine with GitHub Actions to auto-create AppFlowy tasks from issues or PRs.

### Skill Composition

When using with other skills:
1. Use this skill for project tracking
2. Use code-related skills for implementation
3. Update AppFlowy status as work progresses

## Notes

### Limitations

- API documentation is evolving; some endpoints may change
- Self-hosted instances may have different API versions
- Rate limiting depends on deployment configuration

### Future Enhancements

- Webhooks for real-time synchronization
- Bulk operations for multiple tasks
- Advanced querying and filtering
- Custom field type support

### Assumptions

- AppFlowy instance is accessible via network
- JWT authentication is configured
- Database schemas follow standard AppFlowy conventions

## Version History

### Version 1.0.0 (2025-11-22)
- Initial creation
- Core API integration patterns
- Self-hosted deployment guides
- Task tracking workflows
- Project dashboard examples

## Additional Resources

External documentation and references:

- [AppFlowy GitHub Repository](https://github.com/AppFlowy-IO/AppFlowy)
- [AppFlowy Cloud Documentation](https://github.com/AppFlowy-IO/AppFlowy-Cloud)
- [AppFlowy API Documentation](https://github.com/AppFlowy-IO/documentations/blob/main/documentation/appflowy-cloud/openapi/README.md)
- [AppFlowy Zapier Integration](https://appflowy.com/blog/appflowy-is-now-on-zapier)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
