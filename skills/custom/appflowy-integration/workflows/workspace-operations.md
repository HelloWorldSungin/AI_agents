# Workspace Operations Workflows

<overview>
Patterns for managing AppFlowy workspaces, databases, folders, and views. These workflows enable workspace setup, database management, and organizational structure configuration.
</overview>

## Table of Contents

1. [Workspace Management](#workspace-management)
2. [Database Operations](#database-operations)
3. [Folder Structure](#folder-structure)
4. [View Management](#view-management)
5. [Project Workspace Setup](#project-workspace-setup)

---

## Workspace Management

<workspace_management>
**List All Workspaces:**

```python
from appflowy_client import AppFlowyClient

client = AppFlowyClient()

def list_workspaces(client):
    """Retrieve all available workspaces."""
    workspaces = client._make_request('GET', '/api/workspace')
    return workspaces

# Usage
workspaces = list_workspaces(client)
for workspace in workspaces:
    print(f"Workspace: {workspace.get('name')} (ID: {workspace.get('id')})")
```

**Get Workspace Details:**

```python
def get_workspace_info(client, workspace_id):
    """Get detailed information about a workspace."""
    endpoint = f'/api/workspace/{workspace_id}'
    return client._make_request('GET', endpoint)

# Usage
workspace_info = get_workspace_info(client, client.workspace_id)
print(f"Workspace: {workspace_info.get('name')}")
```

**Get Workspace Folder Structure:**

```python
def get_workspace_folders(client, workspace_id):
    """Get folder structure for a workspace."""
    endpoint = f'/api/workspace/{workspace_id}/folder'
    return client._make_request('GET', endpoint)

# Usage
folders = get_workspace_folders(client, client.workspace_id)
print(f"Folders: {folders}")
```

**Find Workspace by Name:**

```python
def find_workspace_by_name(client, workspace_name):
    """Find workspace by name (case-insensitive)."""
    workspaces = list_workspaces(client)
    search_lower = workspace_name.lower()

    for workspace in workspaces:
        if workspace.get('name', '').lower() == search_lower:
            return workspace

    return None

# Usage
arknode_workspace = find_workspace_by_name(client, 'ArkNode Infrastructure')
if arknode_workspace:
    print(f"Found workspace: {arknode_workspace['id']}")
else:
    print("Workspace not found")
```
</workspace_management>

---

## Database Operations

<database_operations>
**List Databases in Workspace:**

```python
def list_databases(client, workspace_id):
    """Retrieve all databases in a workspace."""
    endpoint = f'/api/workspace/{workspace_id}/database'
    databases = client._make_request('GET', endpoint)
    return databases

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
    fields = client._make_request('GET', endpoint)
    return fields

# Usage
fields = get_database_fields(client, client.workspace_id, database_id)
for field in fields:
    print(f"Field: {field.get('name')} - Type: {field.get('type')}")
```

**Find Database by Name:**

```python
def find_database_by_name(client, workspace_id, database_name):
    """Find database by name in workspace."""
    databases = list_databases(client, workspace_id)
    search_lower = database_name.lower()

    for db in databases:
        if db.get('name', '').lower() == search_lower:
            return db

    return None

# Usage
todos_db = find_database_by_name(client, client.workspace_id, 'To-dos')
if todos_db:
    print(f"Found database: {todos_db['id']}")
```

**Verify Database Schema:**

```python
def verify_database_schema(client, workspace_id, database_id, required_fields):
    """Verify database has required fields.

    Args:
        required_fields: List of field names that should exist
    """
    fields = get_database_fields(client, workspace_id, database_id)
    field_names = {f['name'] for f in fields}

    missing_fields = set(required_fields) - field_names
    extra_fields = field_names - set(required_fields)

    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': list(missing_fields),
        'extra_fields': list(extra_fields),
        'field_names': list(field_names)
    }

# Usage
required = ['title', 'status', 'priority', 'assignee', 'due_date']
schema_check = verify_database_schema(
    client,
    client.workspace_id,
    database_id,
    required
)

if schema_check['valid']:
    print("✅ Database schema is valid")
else:
    print(f"⚠️  Missing fields: {schema_check['missing_fields']}")
```

**Get Database Statistics:**

```python
def get_database_stats(client, workspace_id, database_id):
    """Get statistics about database contents."""
    # Get all rows
    rows = client.get_database_rows(workspace_id, database_id)
    row_ids = [row['id'] for row in rows]

    if not row_ids:
        return {
            'total_rows': 0,
            'fields': [],
            'field_count': 0
        }

    # Get fields
    fields = get_database_fields(client, workspace_id, database_id)

    # Get row details for analysis
    details = client.get_row_detail(workspace_id, database_id, row_ids)

    return {
        'total_rows': len(details),
        'fields': [f['name'] for f in fields],
        'field_count': len(fields),
        'row_ids': row_ids
    }

# Usage
stats = get_database_stats(client, client.workspace_id, database_id)
print(f"Database has {stats['total_rows']} rows and {stats['field_count']} fields")
```
</database_operations>

---

## Folder Structure

<folder_structure>
**Get Folder Hierarchy:**

```python
def get_folder_hierarchy(client, workspace_id):
    """Get complete folder hierarchy for workspace."""
    folders = get_workspace_folders(client, workspace_id)

    def build_tree(items, parent_id=None):
        """Recursively build folder tree."""
        tree = []
        for item in items:
            if item.get('parent_id') == parent_id:
                children = build_tree(items, item.get('id'))
                tree.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': item.get('type'),
                    'children': children
                })
        return tree

    return build_tree(folders)

# Usage
hierarchy = get_folder_hierarchy(client, client.workspace_id)
```

**Print Folder Tree:**

```python
def print_folder_tree(client, workspace_id, indent=0):
    """Print folder structure as tree."""
    folders = get_workspace_folders(client, workspace_id)

    def print_item(item, level):
        prefix = "  " * level
        icon = "📁" if item.get('type') == 'folder' else "📄"
        print(f"{prefix}{icon} {item.get('name')}")

        # Print children recursively
        children = [f for f in folders if f.get('parent_id') == item.get('id')]
        for child in children:
            print_item(child, level + 1)

    # Print root items
    root_items = [f for f in folders if f.get('parent_id') is None]
    for item in root_items:
        print_item(item, indent)

# Usage
print("Workspace Structure:")
print_folder_tree(client, client.workspace_id)
```

**Find Folder by Path:**

```python
def find_folder_by_path(client, workspace_id, path):
    """Find folder by path (e.g., 'Projects/Infrastructure/Monitoring').

    Args:
        path: Folder path separated by '/'
    """
    folders = get_workspace_folders(client, workspace_id)
    parts = path.split('/')

    current_parent = None
    for part in parts:
        found = None
        for folder in folders:
            if (folder.get('name') == part and
                folder.get('parent_id') == current_parent):
                found = folder
                break

        if not found:
            return None

        current_parent = found.get('id')

    return found

# Usage
folder = find_folder_by_path(client, client.workspace_id, 'Projects/AI')
```
</folder_structure>

---

## View Management

<view_management>
**Important:** View management is currently limited via REST API. Views (Grid, Board, Calendar) must be created through the AppFlowy UI. The API can query views but cannot create view-database associations.

**List Views in Database:**

```python
def list_database_views(client, workspace_id, database_id):
    """List views associated with a database.

    Note: This requires the database to have views created via UI.
    """
    endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/views'
    try:
        views = client._make_request('GET', endpoint)
        return views
    except Exception as e:
        print(f"⚠️  Could not list views: {e}")
        return []

# Usage
views = list_database_views(client, client.workspace_id, database_id)
for view in views:
    print(f"View: {view.get('name')} - Type: {view.get('type')}")
```

**Create View via UI Automation (Advanced):**

```python
def create_view_instructions(database_name):
    """Generate instructions for creating views in UI.

    Since REST API cannot create views, provide user instructions.
    """
    instructions = f"""
To create a view for '{database_name}' database:

1. Open AppFlowy web UI: http://appflowy.arknode-ai.home
2. Navigate to workspace: 'ArkNode Infrastructure'
3. Find database: '{database_name}'
4. Click the "+" button in the database header
5. Select view type:
   - Grid: Spreadsheet-like view
   - Board: Kanban board view
   - Calendar: Calendar view (requires date field)
   - Gallery: Card-based view

6. Name your view and configure options
7. Click "Create"

Once the view is created, API-created tasks will appear in it.
"""
    return instructions

# Usage
print(create_view_instructions('To-dos'))
```

**Check if Database Has Views:**

```python
def has_views(client, workspace_id, database_id):
    """Check if database has any views created."""
    views = list_database_views(client, workspace_id, database_id)
    return len(views) > 0

# Usage
if not has_views(client, client.workspace_id, database_id):
    print("⚠️  Database has no views. Create one in the UI first.")
    print(create_view_instructions('To-dos'))
```
</view_management>

---

## Project Workspace Setup

<project_workspace_setup>
**Complete Project Workspace Initialization:**

```python
def create_project_workspace(client, project_name, team_members=None):
    """
    Create a new workspace for a project with initial setup.

    This pattern is useful when starting a new project and you want
    to automatically set up the AppFlowy workspace structure.

    Args:
        client: AppFlowy client instance
        project_name: Name of the new project
        team_members: List of team member emails to add (optional)
    """
    from datetime import datetime

    print(f"🚀 Setting up workspace for: {project_name}")

    # Note: Workspace creation API may require admin permissions
    # For now, this assumes workspace exists and we find it by name

    # 1. Find or verify workspace exists
    workspaces = list_workspaces(client)
    workspace = next(
        (w for w in workspaces if w.get('name') == project_name),
        None
    )

    if not workspace:
        print(f"⚠️  Workspace '{project_name}' not found.")
        print("Please create it manually in AppFlowy UI, then run setup again.")
        print("\nSteps:")
        print("1. Open AppFlowy: http://appflowy.arknode-ai.home")
        print("2. Click '+' to create new workspace")
        print(f"3. Name it: '{project_name}'")
        print("4. Run this script again")
        return None

    workspace_id = workspace['id']
    print(f"✅ Using workspace: {project_name} (ID: {workspace_id})")

    # 2. Check if Tasks database exists
    databases = list_databases(client, workspace_id)
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
        print("\nSteps:")
        print(f"1. Open workspace: {project_name}")
        print("2. Click '+' → 'Database'")
        print("3. Name it: 'Tasks'")
        print("4. Add the fields listed above")
        print("5. Create a Grid or Board view")
        print("6. Run this script again")
        return None
    else:
        print(f"✅ Tasks database found (ID: {tasks_db['id']})")

    # 3. Verify database schema
    required_fields = ['title', 'status', 'priority', 'assignee']
    schema_check = verify_database_schema(
        client,
        workspace_id,
        tasks_db['id'],
        required_fields
    )

    if not schema_check['valid']:
        print(f"⚠️  Database missing required fields: {schema_check['missing_fields']}")
        return None
    else:
        print("✅ Database schema verified")

    # 4. Check if views exist
    if not has_views(client, workspace_id, tasks_db['id']):
        print("⚠️  No views found. Creating views in UI is recommended.")
        print(create_view_instructions('Tasks'))

    # 5. Create initial project setup task
    setup_task = {
        'title': f'Project Setup: {project_name}',
        'description': f'Initialize project workspace and documentation. Created: {datetime.utcnow().isoformat()}',
        'status': 'In Progress',
        'priority': 'High',
        'assignee': 'Project Lead'
    }

    try:
        task = client.create_row(
            workspace_id=workspace_id,
            database_id=tasks_db['id'],
            data=setup_task
        )
        print(f"✅ Created initial setup task (ID: {task.get('id')})")
    except Exception as e:
        print(f"⚠️  Could not create setup task: {e}")

    # 6. Return workspace configuration
    config = {
        'workspace_id': workspace_id,
        'workspace_name': project_name,
        'tasks_database_id': tasks_db['id'],
        'setup_complete': True,
        'message': f'Workspace ready for {project_name}'
    }

    # 7. Print configuration for environment variables
    print("\n" + "=" * 60)
    print("📋 Workspace Configuration Complete")
    print("=" * 60)
    print("\nSave these environment variables:")
    print(f"export APPFLOWY_WORKSPACE_ID='{config['workspace_id']}'")
    print(f"export APPFLOWY_TASKS_DB_ID='{config['tasks_database_id']}'")
    print("\nWorkspace is ready for use!")

    return config

# Usage
config = create_project_workspace(
    client,
    "New AI Project",
    team_members=["dev1@team.com", "dev2@team.com"]
)

if config:
    print(f"\n✅ Setup complete for: {config['workspace_name']}")
```

**Automated Workspace Health Check:**

```python
def check_workspace_health(client, workspace_id):
    """Run health check on workspace configuration."""
    print("🏥 Running Workspace Health Check...")
    print("=" * 60)

    health = {
        'workspace_accessible': False,
        'databases_found': False,
        'database_count': 0,
        'has_tasks_database': False,
        'tasks_db_has_views': False,
        'issues': []
    }

    try:
        # Check workspace access
        workspace_info = get_workspace_info(client, workspace_id)
        health['workspace_accessible'] = True
        print(f"✅ Workspace accessible: {workspace_info.get('name')}")

        # Check databases
        databases = list_databases(client, workspace_id)
        health['databases_found'] = len(databases) > 0
        health['database_count'] = len(databases)
        print(f"✅ Found {len(databases)} databases")

        # Check for Tasks database
        tasks_db = next((db for db in databases if db.get('name') == 'Tasks'), None)
        if tasks_db:
            health['has_tasks_database'] = True
            print(f"✅ Tasks database exists (ID: {tasks_db['id']})")

            # Check views
            if has_views(client, workspace_id, tasks_db['id']):
                health['tasks_db_has_views'] = True
                print("✅ Tasks database has views")
            else:
                health['issues'].append("Tasks database has no views")
                print("⚠️  Tasks database has no views")
        else:
            health['issues'].append("Tasks database not found")
            print("⚠️  Tasks database not found")

    except Exception as e:
        health['issues'].append(f"Error during health check: {str(e)}")
        print(f"❌ Health check error: {e}")

    print("=" * 60)
    if len(health['issues']) == 0:
        print("✅ All health checks passed!")
    else:
        print(f"⚠️  Found {len(health['issues'])} issue(s):")
        for issue in health['issues']:
            print(f"   - {issue}")

    return health

# Usage
health = check_workspace_health(client, client.workspace_id)
```

**Clone Workspace Structure:**

```python
def clone_workspace_structure(client, source_workspace_id, target_workspace_name):
    """Clone database structure from one workspace to another.

    Note: This only provides instructions since database creation
    via API may not be fully supported.
    """
    # Get source workspace databases
    databases = list_databases(client, source_workspace_id)

    print(f"🔄 Cloning structure from workspace to '{target_workspace_name}'")
    print("=" * 60)

    for db in databases:
        db_name = db.get('name')
        print(f"\n📋 Database: {db_name}")

        # Get fields
        fields = get_database_fields(client, source_workspace_id, db.get('id'))

        print("   Fields to create:")
        for field in fields:
            field_type = field.get('type')
            field_name = field.get('name')
            print(f"   - {field_name} ({field_type})")

    print("\n" + "=" * 60)
    print("⚠️  Manual steps required:")
    print("1. Create workspace via UI if it doesn't exist")
    print("2. For each database listed above:")
    print("   - Create new database with same name")
    print("   - Add fields with matching types")
    print("   - Create appropriate views (Grid/Board/Calendar)")

# Usage
clone_workspace_structure(
    client,
    client.workspace_id,
    "New Project Workspace"
)
```
</project_workspace_setup>

---

## Related Documentation

- **Task Management**: See `workflows/task-management.md` for task operations
- **API Reference**: See `references/api-reference.md` for API details
- **Troubleshooting**: See `workflows/troubleshooting.md` for common issues
- **Setup Guide**: See `references/setup_guide.md` for deployment instructions
