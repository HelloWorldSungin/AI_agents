# Task Sync Workflow

## Overview

The `sync_tasks.py` script syncs AI_agents tasks from multiple data sources to your AppFlowy Kanban board. It intelligently extracts tasks from JSON state files, ROADMAP.md, and session handoffs, mapping them to appropriate Kanban columns with priority, category, and status tracking.

## Quick Start

```bash
# Navigate to scripts directory
cd skills/custom/appflowy-integration/scripts/

# Preview what would be synced (dry run)
python3 sync_tasks.py --dry-run

# Sync changed tasks only
python3 sync_tasks.py

# Force re-sync all tasks
python3 sync_tasks.py --force
```

## Prerequisites

### Environment Variables

The script requires the following environment variables:

```bash
export APPFLOWY_API_URL="https://appflowy.ark-node.com"
export APPFLOWY_API_TOKEN="your_jwt_token_here"
export APPFLOWY_WORKSPACE_ID="22bcbccd-9cf3-41ac-aa0b-28fe144ba71d"
export APPFLOWY_DATABASE_ID="bb7a9c66-8088-4f71-a7b7-551f4c1adc5d"
```

### Python Dependencies

```bash
# Required
pip3 install requests

# Optional (for better .env file handling)
pip3 install python-dotenv
```

### .env File

By default, the script loads credentials from:
```
/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env
```

You can specify a custom .env file location:
```bash
python3 sync_tasks.py --env-file /path/to/custom/.env
```

## Configuration Options

### Command Line Arguments

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Preview changes without syncing | `python3 sync_tasks.py --dry-run` |
| `--force` | Re-sync all tasks, ignoring status | `python3 sync_tasks.py --force` |
| `--env-file PATH` | Custom .env file location | `python3 sync_tasks.py --env-file ~/.env` |

## Data Sources

The script collects tasks from multiple sources:

### 1. team-communication.json (Required)

**Location:** `.ai-agents/state/team-communication.json`

**Extracts:**
- Active tasks → Status from task data
- Completed tasks (last 5) → Status: Done
- Blocked tasks → Status: Blocked

**Example:**
```json
{
  "manager_instructions": {
    "active_tasks": [
      {
        "id": "TASK-1.1",
        "name": "Create sync script",
        "status": "in_progress",
        "priority": "high",
        "agent": "Python Developer"
      }
    ],
    "completed_tasks": [...],
    "blocked_tasks": [...]
  }
}
```

### 2. ROADMAP.md (Required)

**Location:** `.planning/ROADMAP.md`

**Extracts:**
- Phase headers: `### Phase XX: Title` → Status: Backlog

**Example:**
```markdown
### Phase 01: Documentation Consolidation
### Phase 02: Skills Deduplication
```

Results in:
- Task: "Phase 01: Documentation Consolidation" → Status: Backlog
- Task: "Phase 02: Skills Deduplication" → Status: Backlog

### 3. feature-tracking.json (Optional)

**Location:** `.ai-agents/state/feature-tracking.json`

**Extracts:**
- Features with status and priority

**Example:**
```json
{
  "features": [
    {
      "name": "User authentication",
      "status": "in_progress",
      "priority": "high",
      "description": "JWT-based auth"
    }
  ]
}
```

### 4. whats-next.md (Optional)

**Location:** `whats-next.md`

**Extracts:**
- Items from "Next Steps" or "Pending Items" sections
- Bullet points and numbered lists → Status: Todo, Priority: High

**Example:**
```markdown
## Next Steps
- Complete task sync script
- Add automation workflows
- Update documentation
```

## Kanban Column Mapping

The script maps task statuses to AppFlowy Kanban columns:

| Source Status | AppFlowy Column | Description |
|--------------|-----------------|-------------|
| `pending` | Backlog | Not yet started |
| `todo` | Todo | Ready to start |
| `in_progress` | In Progress | Currently working |
| `review` | Review | Ready for review |
| `completed` / `done` | Done | Finished |
| `blocked` | Blocked | Waiting for dependency |
| `not started` | Backlog | Not yet started |

### Example Status Mapping

```python
STATUS_MAP = {
    'pending': 'Backlog',
    'in_progress': 'In Progress',
    'blocked': 'Blocked',
    'completed': 'Done',
    'todo': 'Todo',
    'review': 'Review',
    'not started': 'Backlog',
    'done': 'Done',
}
```

## Priority Mapping

| Source Priority | AppFlowy Priority |
|----------------|-------------------|
| `critical` | Critical |
| `high` | High |
| `medium` | Medium (default) |
| `low` | Low |

## Category Mapping

Tasks are automatically categorized based on their source:

| Source | Category |
|--------|----------|
| team-communication.json | Feature |
| feature-tracking.json | Feature |
| ROADMAP.md | Infrastructure |
| whats-next.md | Documentation |

You can customize categories by modifying the extraction functions in `sync_tasks.py`.

## AppFlowy Database Schema

The script expects the following fields in your AppFlowy database:

| Field Name | Type | Values | Required |
|-----------|------|--------|----------|
| Title | Text | Task title | Yes |
| Status | Select | Backlog, Todo, In Progress, Review, Done, Blocked | Yes |
| Priority | Select | Critical, High, Medium, Low | Yes |
| Category | Select | Feature, Bug, Documentation, Infrastructure, Research | Yes |
| Source | Text | File path or reference | Yes |
| Notes | Text | Additional details | No |

### Setting Up the Database

1. Create a database in AppFlowy UI
2. Add the fields listed above
3. Configure select field options (Status, Priority, Category)
4. Copy the database ID to APPFLOWY_DATABASE_ID

## How It Works

### Task Collection Flow

```
1. Load sync status from .task-sync-status.json
2. Extract tasks from team-communication.json
3. Extract tasks from ROADMAP.md
4. Extract tasks from feature-tracking.json (if exists)
5. Extract tasks from whats-next.md (if exists)
6. Deduplicate tasks by title
7. Check each task for changes (hash comparison)
8. Sync only changed tasks (or all if --force)
9. Save sync status
```

### Incremental Sync Logic

The script uses hash-based change detection:

1. **First Run:** All tasks are synced and status is saved
2. **Subsequent Runs:** Only tasks with changed data are synced
3. **Force Mode:** All tasks are re-synced regardless of status

### Sync Status Tracking

Sync status is stored in:
```
skills/custom/appflowy-integration/.task-sync-status.json
```

This file tracks:
- Last sync timestamp
- Task hash for each task (source:title)
- AppFlowy row ID for each task

Example `.task-sync-status.json`:
```json
{
  "last_sync": "2025-12-08T07:46:45Z",
  "synced_tasks": {
    "team-communication.json:Create sync script": "row-12345",
    "ROADMAP.md:Phase 01: Documentation Consolidation": "row-67890"
  },
  "task_hashes": {
    "team-communication.json:Create sync script": "a1b2c3d4e5f6",
    "ROADMAP.md:Phase 01: Documentation Consolidation": "f6e5d4c3b2a1"
  }
}
```

### Task Deduplication

Tasks with identical titles are deduplicated (case-insensitive):
- "Create sync script" and "create sync script" → Same task
- First occurrence wins

## Expected Output

### Dry Run Mode

```
2025-12-08 07:45:00 - INFO - Testing AppFlowy connection...
2025-12-08 07:45:01 - INFO - Connected to AppFlowy - 3 workspace(s) accessible
2025-12-08 07:45:01 - INFO - ============================================================
2025-12-08 07:45:01 - INFO - AppFlowy Task Sync
2025-12-08 07:45:01 - INFO - ============================================================
2025-12-08 07:45:01 - INFO - Repository: /Users/sunginkim/GIT/AI_agents
2025-12-08 07:45:01 - INFO - Workspace ID: 22bcbccd-9cf3-41ac-aa0b-28fe144ba71d
2025-12-08 07:45:01 - INFO - Database ID: bb7a9c66-8088-4f71-a7b7-551f4c1adc5d
2025-12-08 07:45:01 - INFO - Mode: DRY RUN
2025-12-08 07:45:01 - INFO - ============================================================
2025-12-08 07:45:02 - INFO - Extracted 2 tasks from team-communication.json
2025-12-08 07:45:02 - INFO - feature-tracking.json not found (optional)
2025-12-08 07:45:02 - INFO - Extracted 6 tasks from ROADMAP.md
2025-12-08 07:45:02 - INFO - whats-next.md not found (optional)
2025-12-08 07:45:02 - INFO - Collected 8 unique tasks from 8 total
2025-12-08 07:45:02 - INFO - Total tasks to process: 8
2025-12-08 07:45:02 - INFO - ============================================================
2025-12-08 07:45:02 - INFO - DRY RUN: Would sync task 'Create sync script'
2025-12-08 07:45:02 - INFO -          Status: In Progress, Priority: High
2025-12-08 07:45:02 - INFO - Syncing 'Create sync script' (never synced)
...
2025-12-08 07:45:05 - INFO - ============================================================
2025-12-08 07:45:05 - INFO - Sync Summary
2025-12-08 07:45:05 - INFO - ============================================================
2025-12-08 07:45:05 - INFO - Synced:  8
2025-12-08 07:45:05 - INFO - Skipped: 0
2025-12-08 07:45:05 - INFO - Failed:  0
2025-12-08 07:45:05 - INFO - Total:   8
2025-12-08 07:45:05 - INFO - ============================================================
```

### Live Sync Mode

```
2025-12-08 07:46:00 - INFO - Testing AppFlowy connection...
2025-12-08 07:46:01 - INFO - Connected to AppFlowy - 3 workspace(s) accessible
2025-12-08 07:46:01 - INFO - ============================================================
2025-12-08 07:46:01 - INFO - AppFlowy Task Sync
2025-12-08 07:46:01 - INFO - ============================================================
2025-12-08 07:46:01 - INFO - Repository: /Users/sunginkim/GIT/AI_agents
2025-12-08 07:46:01 - INFO - Workspace ID: 22bcbccd-9cf3-41ac-aa0b-28fe144ba71d
2025-12-08 07:46:01 - INFO - Database ID: bb7a9c66-8088-4f71-a7b7-551f4c1adc5d
2025-12-08 07:46:01 - INFO - Mode: LIVE SYNC
2025-12-08 07:46:01 - INFO - ============================================================
2025-12-08 07:46:02 - INFO - Extracted 2 tasks from team-communication.json
2025-12-08 07:46:02 - INFO - Extracted 6 tasks from ROADMAP.md
2025-12-08 07:46:02 - INFO - Collected 8 unique tasks from 8 total
2025-12-08 07:46:02 - INFO - Total tasks to process: 8
2025-12-08 07:46:02 - INFO - ============================================================
2025-12-08 07:46:03 - INFO - Created task 'Create sync script' (ID: row-12345)
2025-12-08 07:46:03 - INFO - Syncing 'Create sync script' (never synced)
2025-12-08 07:46:04 - INFO - Skipping 'Phase 01: Documentation Consolidation' - up to date
2025-12-08 07:46:05 - INFO - Updated task 'Phase 02: Skills Deduplication'
2025-12-08 07:46:05 - INFO - Syncing 'Phase 02: Skills Deduplication' (task data changed)
...
2025-12-08 07:46:20 - INFO - Sync status saved to .task-sync-status.json
2025-12-08 07:46:20 - INFO - ============================================================
2025-12-08 07:46:20 - INFO - Sync Summary
2025-12-08 07:46:20 - INFO - ============================================================
2025-12-08 07:46:20 - INFO - Synced:  3
2025-12-08 07:46:20 - INFO - Skipped: 5
2025-12-08 07:46:20 - INFO - Failed:  0
2025-12-08 07:46:20 - INFO - Total:   8
2025-12-08 07:46:20 - INFO - ============================================================
```

## Verification

### 1. Check Sync Status

```bash
# View sync status file
cat skills/custom/appflowy-integration/.task-sync-status.json | jq .
```

### 2. Verify in AppFlowy UI

1. Open https://appflowy.ark-node.com
2. Navigate to your workspace
3. Open the "To-dos" database (or your tasks database)
4. Verify tasks appear in correct Kanban columns
5. Check priority, category, and source fields

### 3. Test Incremental Sync

```bash
# Make a change to team-communication.json
# (e.g., update a task status)

# Run sync (should only sync changed tasks)
python3 sync_tasks.py

# Output should show:
# Synced: 1
# Skipped: 7
```

## Troubleshooting

### Authentication Errors

**Error:** `Authentication failed - check API token`

**Solution:**
```bash
# Obtain fresh JWT token
curl -X POST "https://appflowy.ark-node.com/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@arknode.local",
    "password": "your_password",
    "grant_type": "password"
  }'

# Update .env file with new token
export APPFLOWY_API_TOKEN="new_token_here"
```

### Database Not Found

**Error:** `Resource not found: /api/workspace/.../database/...`

**Solution:**
- Verify database ID is correct
- Check database exists in workspace
- Ensure your user has access to the database

```bash
# List all databases in workspace
curl -X GET "https://appflowy.ark-node.com/api/workspace/$APPFLOWY_WORKSPACE_ID/database" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

### Field Schema Mismatch

**Error:** Tasks created but missing fields or incorrect values

**Solution:**
- Verify database has all required fields (Title, Status, Priority, Category, Source, Notes)
- Check Select field options match expected values
- Review field names (case-sensitive)

### Missing Data Source Files

**Error:** `File not found: .ai-agents/state/team-communication.json`

**Solution:**
- Verify file exists: `ls -la .ai-agents/state/team-communication.json`
- Check you're running from repository root
- Note: feature-tracking.json and whats-next.md are optional

### Tasks Not Appearing in UI

**Issue:** Tasks created via API but not visible in AppFlowy UI

**Solution:**
This is a known limitation - see SKILL.md limitations section.

1. Create a database view in AppFlowy UI first (click "+" → "Board" for Kanban)
2. Then tasks created via API will appear in the view
3. Alternative: Create tasks via browser console (uses WebSocket like UI)

### Sync Status Corruption

**Error:** Sync status file corrupted or inconsistent

**Solution:**
```bash
# Delete sync status to start fresh
rm skills/custom/appflowy-integration/.task-sync-status.json

# Force re-sync all tasks
python3 sync_tasks.py --force
```

### Duplicate Tasks

**Issue:** Tasks appear multiple times in AppFlowy

**Cause:** Same task extracted from multiple sources with different titles

**Solution:**
1. Check task deduplication logic in script
2. Ensure task titles are consistent across sources
3. Review `.task-sync-status.json` for duplicate entries
4. Delete duplicates in AppFlowy UI and run `--force` sync

### Script Exits with Code 1

**Common Causes:**
1. Authentication failure (401)
2. Missing environment variables
3. Database not found (404)
4. Network connectivity issues
5. Missing required data source file

**Debug:**
```bash
# Run with verbose output
python3 sync_tasks.py --dry-run 2>&1 | tee sync_log.txt

# Check exit code
echo $?
```

## Best Practices

### 1. Always Dry Run First

Before syncing, especially after code changes:
```bash
python3 sync_tasks.py --dry-run
```

### 2. Use Version Control for .task-sync-status.json

Add to `.gitignore` if you don't want to track sync status:
```bash
echo ".task-sync-status.json" >> .gitignore
```

Or commit it to track what's synced across team members.

### 3. Automate with Cron

See `git-sync.md` for automated sync setup.

### 4. Monitor Sync Logs

Keep logs for troubleshooting:
```bash
python3 sync_tasks.py 2>&1 | tee -a logs/task_sync_$(date +%Y%m%d_%H%M%S).log
```

### 5. Validate Data Sources

```bash
# Check data sources exist and are valid JSON
jq . .ai-agents/state/team-communication.json
jq . .ai-agents/state/feature-tracking.json  # optional
```

### 6. Customize Task Extraction

Modify extraction functions to match your workflow:
- Add custom status mappings
- Filter specific task types
- Adjust priority logic
- Change category assignments

## Common Use Cases

### Initial Setup

```bash
# First time setup
cd skills/custom/appflowy-integration/scripts/
python3 sync_tasks.py --dry-run   # Preview
python3 sync_tasks.py             # Sync
```

### Daily Task Sync

```bash
# Only sync changed tasks (fast)
python3 sync_tasks.py
```

### After Task Updates

```bash
# Sync after updating team-communication.json
python3 sync_tasks.py
```

### Sync All Tasks

```bash
# Force re-sync everything (slow)
python3 sync_tasks.py --force
```

### Testing with Custom Credentials

```bash
# Use different workspace/database
python3 sync_tasks.py --env-file ~/.env.test
```

## Integration with Git

See `git-sync.md` for:
- Git post-commit hooks for automatic sync
- Automated sync on push
- CI/CD integration
- Scheduled sync with cron

## Related Scripts

- `sync_docs.py` - Sync documentation to AppFlowy
- `sync_tasks.py` - This script (task sync)

## Customization Examples

### Add Custom Data Source

Edit `sync_tasks.py` to add a new data source:

```python
def _extract_tasks_from_custom_source(self) -> List[Dict[str, Any]]:
    """Extract tasks from custom source."""
    tasks = []
    file_path = self.REPO_ROOT / 'path/to/custom.json'

    if not file_path.exists():
        logger.info("custom.json not found (optional)")
        return tasks

    # ... extraction logic ...

    return tasks

# Add to collect_tasks method
def collect_tasks(self):
    all_tasks.extend(self._extract_tasks_from_custom_source())
```

### Customize Status Mapping

Edit `STATUS_MAP` in `sync_tasks.py`:

```python
STATUS_MAP = {
    'pending': 'Backlog',
    'in_progress': 'In Progress',
    'blocked': 'Blocked',
    'completed': 'Done',
    # Add custom mappings
    'waiting': 'Blocked',
    'deployed': 'Done',
}
```

### Add Custom Fields

Modify `_sync_task` method to include additional fields:

```python
task_data = {
    'Title': task['title'],
    'Status': task['status'],
    'Priority': task['priority'],
    'Category': task['category'],
    'Source': task['source'],
    'Notes': task.get('notes', ''),
    # Add custom fields
    'Assignee': task.get('assignee', 'Unassigned'),
    'Due Date': task.get('due_date', ''),
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review `references/api-reference.md`
3. Check AppFlowy logs: `docker logs appflowy-cloud`
4. Review sync status: `.task-sync-status.json`
5. Test data sources: `jq . .ai-agents/state/team-communication.json`
