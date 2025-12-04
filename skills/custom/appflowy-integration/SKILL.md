---
name: appflowy-integration
description: >
  Integration with AppFlowy project management tool for task tracking, database management,
  and workspace organization. Use when working with AppFlowy, managing project tasks,
  creating databases, organizing workspaces, syncing agent work with project tracking,
  or when the user mentions AppFlowy, project tracking, or task management.
version: 2.0.0
author: AI Agents Team
category: custom
token_estimate: ~1200
---

# AppFlowy Integration Skill

<objective>
Integration with AppFlowy, an open-source collaborative workspace and project management tool. Provides capabilities for managing tasks, databases, workspaces, and project organization through AppFlowy's REST API.
</objective>

<context>
**When to use:**
- Creating or updating tasks in AppFlowy databases
- Managing project workspaces and folders
- Organizing work items in Kanban boards or database views
- Syncing agent work with project tracking
- Automating project management workflows
- Creating documentation in AppFlowy workspaces
- When user mentions AppFlowy, project tracking, or task management

**Prerequisites:**
- AppFlowy deployed (self-hosted or cloud)
- API endpoint URL configured
- Authentication credentials (JWT token)
- Workspace ID known for operations
- Python `requests` library installed

**Do NOT use when:**
- Working with other project management tools (Jira, Asana, Trello)
- Managing local files without AppFlowy integration
- Tasks don't require project management tracking
</context>

<quick_start>
**ArkNode-AI Production Configuration:**
```bash
export APPFLOWY_API_URL="http://appflowy.arknode-ai.home"
export APPFLOWY_WORKSPACE_ID="22bcbccd-9cf3-41ac-aa0b-28fe144ba71d"
export APPFLOWY_TODOS_DB_ID="bb7a9c66-8088-4f71-a7b7-551f4c1adc5d"
```

**Access:**
- Web UI: http://appflowy.arknode-ai.home
- Admin Email: admin@arknode.local
- Admin Password: Stored in `/opt/appflowy-cloud/.env` on CT102 (192.168.68.55)
- WebSocket: ws://appflowy.arknode-ai.home/ws/v2/

**Python Client Quick Start:**
```python
from appflowy_client import AppFlowyClient

# Initialize client (uses environment variables)
client = AppFlowyClient()

# List workspaces
workspaces = client.list_workspaces()

# List databases in workspace
databases = client.list_databases(client.workspace_id)

# Get database fields
fields = client.get_database_fields(client.workspace_id, database_id)

# Create a task
task = client.create_row(
    workspace_id=client.workspace_id,
    database_id=database_id,
    data={
        'title': 'Implement user authentication',
        'status': 'In Progress',
        'priority': 'High',
        'assignee': 'AI Agent',
        'description': 'Add JWT-based authentication'
    }
)
```

For detailed workflows, see:
- `workflows/task-management.md` - Creating and updating tasks
- `workflows/workspace-operations.md` - Workspace and database setup
- `workflows/troubleshooting.md` - Common issues and solutions
- `references/api-reference.md` - Complete API documentation
</quick_start>

<success_criteria>
- AppFlowy client initialized successfully
- Can list workspaces and databases
- Can create and update tasks via API
- Authentication token valid and working
- Tasks visible in AppFlowy UI (if view exists - see limitations)
- No 401/403 authentication errors
- API responses return expected data structures
</success_criteria>

<workflow>
<overview>
AppFlowy integration follows a standard pattern: authenticate → verify workspace → list databases → perform operations. The skill provides specialized workflows for different use cases.
</overview>

<router>
**Choose your workflow:**

1. **Task Management** → `workflows/task-management.md`
   - Create tasks
   - Update task status
   - Query and filter tasks
   - Bulk operations
   - Agent task tracking pattern
   - Daily standup summary

2. **Workspace Operations** → `workflows/workspace-operations.md`
   - Workspace setup
   - Database creation and management
   - Folder structure organization
   - View management
   - Project workspace initialization

3. **Server Management** → `workflows/server-deployment.md`
   - Start/stop AppFlowy backend
   - Monitor server health
   - Backup and restore
   - Container management
   - Auto-start configuration

4. **Troubleshooting** → `workflows/troubleshooting.md`
   - Environment variables not updating
   - WebSocket connection issues
   - View-database association problems
   - API authentication failures
   - Container restart behavior

5. **API Reference** → `references/api-reference.md`
   - Authentication endpoints
   - Workspace API
   - Database API
   - Row operations
   - Field operations
   - Error handling patterns
</router>

<authentication>
**Method 1: JWT Token (Recommended for automation)**
```bash
# Obtain JWT token via API
curl -X POST "http://appflowy.arknode-ai.home/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password",
    "grant_type": "password"
  }'
```

**Method 2: Environment Variables**
```bash
export APPFLOWY_API_URL="http://appflowy.arknode-ai.home"
export APPFLOWY_API_TOKEN="your_jwt_token_here"
export APPFLOWY_WORKSPACE_ID="your_workspace_id"
```

**Python Client Configuration:**
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

See `references/api-reference.md` for complete authentication documentation.
</authentication>

<error_handling>
**Robust Error Handling Pattern:**
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
```

See `workflows/troubleshooting.md` for specific error scenarios and solutions.
</error_handling>
</workflow>

<best_practices>
<practice name="secure_credentials">
**Never hardcode credentials.** Use environment variables or secure credential storage.

```python
from dotenv import load_dotenv
load_dotenv()

# Credentials loaded from .env file
api_token = os.getenv('APPFLOWY_API_TOKEN')
```
</practice>

<practice name="cache_ids">
**Cache workspace and database IDs** to avoid repeated lookups.

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
</practice>

<practice name="validate_fields">
**Validate field compatibility** before inserting data.

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
</practice>

<practice name="degree_of_freedom">
**Medium Freedom:** Follow authentication and API endpoint patterns exactly. Implement error handling and rate limiting. Customize workflow functions based on your project needs.
</practice>
</best_practices>

<security_checklist>
- Never hardcode credentials - use environment variables
- Store API tokens securely (not in git)
- Validate all user input before API calls
- Use HTTPS for production deployments
- Rotate JWT tokens regularly
- Never log API tokens or passwords
- Verify workspace/database IDs before operations
- Implement rate limiting to prevent API abuse
- Use proper error handling to avoid credential leaks
- Set up firewall rules for self-hosted instances
</security_checklist>

<limitations>
<limitation name="view_database_association">
**Tasks Created via API May Not Be Visible Immediately**

**Issue:** Tasks created via REST API may not appear in the AppFlowy UI right away.

**Cause:** AppFlowy requires view objects (Grid, Board, Calendar) to exist as separate collab records in PostgreSQL. The REST API cannot create these view-database associations - only the UI can.

**Symptoms:**
- Task created successfully via API (returns row ID)
- Task exists in database (verified in PostgreSQL)
- Task does NOT appear in UI
- Browser console shows: `[useViewOperations] databaseId not found for view`

**Solution:**
1. Create a database view in AppFlowy UI first (click "+" → "Grid" or "Board")
2. Then use the API to create tasks - they will appear in the view
3. Alternative: Create tasks via browser console (uses WebSocket like UI)

**Browser Console Workaround:**
```javascript
// This uses your existing session (no auth needed)
const WORKSPACE_ID = '22bcbccd-9cf3-41ac-aa0b-28fe144ba71d';
const DATABASE_ID = 'bb7a9c66-8088-4f71-a7b7-551f4c1adc5d';

fetch(`/api/workspace/${WORKSPACE_ID}/database/${DATABASE_ID}/row`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    cells: {
      phVRgL: 'Task Title',     // Description field
      YAgo8T: 'Task details',   // Text field
      SqwRg1: 'CEZD'            // Status: To Do
    }
  })
})
.then(r => r.json())
.then(d => console.log('Created:', d.data));
```

**Reference:** See `workflows/troubleshooting.md` for detailed diagnosis and solutions.
</limitation>

<limitation name="api_versioning">
**API Documentation is Evolving**
- API endpoints may change between versions
- Self-hosted instances may have different API versions
- Some features may require specific AppFlowy versions
- Always check AppFlowy documentation for latest API changes
</limitation>

<limitation name="rate_limiting">
**Rate Limiting**
- Rate limiting depends on deployment configuration
- Self-hosted instances may have different limits than cloud
- Implement client-side rate limiting for safety
</limitation>
</limitations>

<anti_patterns>
<pitfall name="expired_tokens">
❌ **Don't:** Continue using expired JWT tokens, causing 401 errors

✅ **Do:** Implement token refresh logic or re-authenticate automatically
```python
if response.status_code == 401:
    token = refresh_jwt_token()
    retry_request()
```
</pitfall>

<pitfall name="workspace_id_confusion">
❌ **Don't:** Hardcode workspace IDs or use wrong IDs

✅ **Do:** List and verify resources first, use descriptive variable names
```python
workspaces = client.list_workspaces()
arknode_workspace = next(w for w in workspaces if w['name'] == 'ArkNode Infrastructure')
workspace_id = arknode_workspace['id']
```
</pitfall>

<pitfall name="missing_view_objects">
❌ **Don't:** Expect API-created tasks to appear in UI without views

✅ **Do:** Create views in UI first, then use API for task operations

See `workflows/troubleshooting.md` for view-database association issue.
</pitfall>

<pitfall name="restart_vs_recreate">
❌ **Don't:** Use `docker compose restart` to reload .env changes

✅ **Do:** Use `docker compose down && docker compose up -d` to recreate containers
```bash
# WRONG - doesn't reload .env
docker compose restart

# RIGHT - recreates containers with new .env
docker compose down
docker compose up -d
```
</pitfall>

<pitfall name="network_issues">
❌ **Don't:** Assume AppFlowy is accessible without testing

✅ **Do:** Test connectivity before running operations
```bash
# Test connectivity
curl -v http://appflowy.arknode-ai.home/api/workspace

# Test DNS resolution
nslookup appflowy.arknode-ai.home
```
</pitfall>
</anti_patterns>

<examples>
<example name="agent_task_tracking">
**Context:** Agent needs to track its work in AppFlowy for team visibility.

```python
#!/usr/bin/env python3
from appflowy_client import AppFlowyClient

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

    result = client.create_row(
        workspace_id=client.workspace_id,
        database_id=os.getenv('APPFLOWY_TODOS_DB_ID'),
        data=task_info
    )
    print(f"✅ Task tracked: {result['id']}")
    return result['id']

# Usage
task_id = track_agent_task("Implementing AppFlowy integration skill")
```

See `workflows/task-management.md` for complete patterns.
</example>

<example name="daily_standup">
**Context:** Generate daily standup summary from AppFlowy tasks.

```python
def generate_standup_summary(client, database_id):
    """Generate daily standup summary from AppFlowy tasks."""
    from datetime import datetime, timedelta

    # Get tasks updated in last 24 hours
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
    updated_rows = client.get_updated_rows(client.workspace_id, database_id, yesterday)

    # ... organize by status and format output ...

    return formatted_summary

# Usage
standup = generate_standup_summary(client, database_id)
print(standup)
```

See `workflows/task-management.md` for complete implementation.
</example>

<example name="project_dashboard">
**Context:** Generate project status dashboard from AppFlowy data.

```python
def generate_project_dashboard(client, database_id):
    """Create comprehensive project status dashboard."""
    # Get all tasks
    rows = client.get_database_rows(client.workspace_id, database_id)

    # Analyze status, priority, assignee workload
    # ... (see workflows/task-management.md for full code) ...

    return dashboard_output
```

See `workflows/task-management.md` for complete implementation.
</example>
</examples>

<related_skills>
This skill works well with:

- **api-endpoint-creator**: When building custom integrations with AppFlowy
- **database-migration**: When setting up AppFlowy database schemas
- **incident-response**: Track incidents in AppFlowy
- **deployment-workflow**: Track deployment tasks in AppFlowy
- **documentation-writer**: Generate documentation for AppFlowy workflows
</related_skills>

<integration_notes>
**Working with Other Tools:**

**Zapier Integration:** AppFlowy supports Zapier, enabling no-code automation between AppFlowy and 5,000+ apps.

**GitHub Integration:** Combine with GitHub Actions to auto-create AppFlowy tasks from issues or PRs.

**Skill Composition:**
1. Use this skill for project tracking
2. Use code-related skills for implementation
3. Update AppFlowy status as work progresses
</integration_notes>

<reference_guides>
**Documentation:**
- `workflows/task-management.md` - Creating, updating, and tracking tasks
- `workflows/workspace-operations.md` - Workspace and database management
- `workflows/server-deployment.md` - Server setup and operations
- `workflows/troubleshooting.md` - Common issues and solutions
- `references/api-reference.md` - Complete API endpoint documentation
- `references/setup_guide.md` - Deployment and configuration guide

**Scripts:**
- `scripts/appflowy_client.py` - Python client library
- `scripts/task_tracker.py` - Task tracking utilities
- `scripts/workspace_setup.py` - Workspace initialization
- `scripts/manage_server.sh` - Server management script

**External Resources:**
- [AppFlowy GitHub Repository](https://github.com/AppFlowy-IO/AppFlowy)
- [AppFlowy Cloud Documentation](https://github.com/AppFlowy-IO/AppFlowy-Cloud)
- [AppFlowy API Documentation](https://github.com/AppFlowy-IO/documentations/blob/main/documentation/appflowy-cloud/openapi/README.md)
- [AppFlowy Zapier Integration](https://appflowy.com/blog/appflowy-is-now-on-zapier)
</reference_guides>

<version_history>
**Version 2.0.0 (2025-12-04)**
- Migrated to pure XML structure
- Implemented progressive disclosure
- Split content into workflow files
- Added security checklist
- Improved YAML description with broader triggers
- Reduced main skill file from 1,256 to ~450 lines

**Version 1.0.0 (2025-11-22)**
- Initial creation
- Core API integration patterns
- Self-hosted deployment guides
- Task tracking workflows
- Project dashboard examples
</version_history>
