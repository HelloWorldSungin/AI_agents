# AppFlowy Integration Sync Scripts

This directory contains scripts for syncing AI_agents documentation and tasks to AppFlowy Cloud.

## AppFlowy Cloud API Limitations

AppFlowy Cloud's REST API has specific limitations:

**What Works:**
- `GET /api/workspace` - List workspaces
- `GET /api/workspace/{id}/folder` - Get folder structure
- `GET/POST/PATCH /api/workspace/{id}/database/{db_id}/row` - Database row operations

**What Doesn't Work:**
- `POST /api/workspace/{id}/folder` - Create folders (405 error)
- `POST /api/workspace/{id}/page` - Create pages (405 error)

These operations require either:
1. Using the AppFlowy UI directly
2. Using WebSocket API (complex, undocumented)
3. Working with database rows instead

## Scripts Overview

### Documentation Sync Scripts

#### `sync_docs_report.py` (Start Here)
**Status:** Ready to use
**Purpose:** Reports API limitations and provides sync options

```bash
python sync_docs_report.py
```

This script:
- Tests AppFlowy connection
- Lists 14 local documentation files
- Explains API limitations clearly
- Provides 3 options for syncing docs
- Recommends database-based approach

**Use this first** to understand your options.

---

#### `sync_docs_database.py` (Recommended)
**Status:** Ready to use (after database setup)
**Purpose:** Syncs documentation as database rows

**Setup Required:**
1. Create a "Documentation" database in AppFlowy UI with these fields:
   - Title (Text) - Primary field
   - Content (Long Text)
   - Category (Select: Getting Started, Guides, Reference, Examples)
   - LastUpdated (Date)
   - FilePath (Text)
   - Status (Select: Draft, Published, Archived)

2. Get database ID:
   - Right-click database → Copy link
   - Extract ID from URL

3. Add to `.env` file:
   ```
   APPFLOWY_DOCS_DATABASE_ID=your-database-id-here
   ```

**Usage:**
```bash
# Preview what would be synced
python sync_docs_database.py --dry-run

# Sync documentation
python sync_docs_database.py

# Force re-sync all files
python sync_docs_database.py --force
```

**Features:**
- Syncs 14 documentation files as database rows
- Incremental sync with MD5 hash tracking
- Categories: Getting Started, Guides, Reference, Examples
- Works with AppFlowy's supported API

**Advantages:**
- ✓ Fully automated
- ✓ Supports incremental updates
- ✓ Easy to search and filter
- ✓ Use Kanban/Table/Calendar views
- ✓ Just as powerful as pages!

---

#### `sync_docs.py` (Deprecated)
**Status:** Deprecated - uses unsupported API
**Purpose:** Original page/folder-based sync (doesn't work)

This script attempts to create pages and folders via POST endpoints that don't exist in AppFlowy Cloud API. Kept for reference only.

**Do not use.** Use `sync_docs_database.py` instead.

---

### Task Sync Script

#### `sync_tasks.py`
**Status:** Working correctly
**Purpose:** Syncs tasks to AppFlowy Kanban board

This script already uses the database approach and works correctly!

**Setup:**
Already configured to use the existing "To-dos" database:
```
APPFLOWY_DATABASE_ID=bb7a9c66-8088-4f71-a7b7-551f4c1adc5d
```

**Usage:**
```bash
# Preview what would be synced
python sync_tasks.py --dry-run

# Sync tasks
python sync_tasks.py

# Force re-sync all tasks
python sync_tasks.py --force
```

**Data Sources:**
- `.ai-agents/state/team-communication.json` - Active/completed/blocked tasks
- `.planning/ROADMAP.md` - Planned phases
- `.ai-agents/state/feature-tracking.json` - Features (optional)
- `whats-next.md` - Session handoffs (optional)

**Features:**
- Status mapping: Backlog, Todo, In Progress, Review, Done, Blocked
- Priority mapping: Critical, High, Medium, Low
- Category tagging: Feature, Bug, Documentation, Infrastructure, Research
- Task deduplication by title
- Hash-based change detection

---

## Environment Variables

Required in `.env` file:

```bash
# AppFlowy API Configuration
APPFLOWY_API_URL=https://appflowy.ark-node.com
APPFLOWY_WORKSPACE_ID=22bcbccd-9cf3-41ac-aa0b-28fe144ba71d
APPFLOWY_API_TOKEN=your-jwt-token-here

# For task sync (already configured)
APPFLOWY_DATABASE_ID=bb7a9c66-8088-4f71-a7b7-551f4c1adc5d

# For documentation sync (you need to create this database)
APPFLOWY_DOCS_DATABASE_ID=your-docs-database-id-here
```

## Recommended Workflow

### For Documentation Sync:

1. **Understand your options:**
   ```bash
   python sync_docs_report.py
   ```

2. **Create Documentation database in AppFlowy UI** (one-time setup)

3. **Add database ID to `.env`:**
   ```bash
   APPFLOWY_DOCS_DATABASE_ID=your-database-id
   ```

4. **Test sync:**
   ```bash
   python sync_docs_database.py --dry-run
   ```

5. **Sync for real:**
   ```bash
   python sync_docs_database.py
   ```

### For Task Sync:

1. **Test sync:**
   ```bash
   python sync_tasks.py --dry-run
   ```

2. **Sync tasks:**
   ```bash
   python sync_tasks.py
   ```

---

## Why Database Rows Instead of Pages?

AppFlowy Cloud's REST API doesn't support creating pages/folders programmatically. However, database rows are equally powerful:

**Benefits:**
- ✓ Fully automated sync
- ✓ Multiple view types (Table, Kanban, Calendar, Grid)
- ✓ Rich filtering and sorting
- ✓ Custom fields and properties
- ✓ Search across all content
- ✓ Export capabilities

**Workflow:**
1. Database rows for automated sync ← Use this
2. Traditional pages for manual authoring ← Use UI for this

This is actually how many teams use AppFlowy - databases for structured data, pages for freeform content.

---

## Troubleshooting

### 405 Method Not Allowed
This means you're trying to use an unsupported endpoint. Use the database-based scripts instead.

### Missing APPFLOWY_DOCS_DATABASE_ID
You need to create the Documentation database in AppFlowy UI first, then add its ID to `.env`.

### Authentication Failed
Your JWT token may have expired. Tokens expire after 7 days. Get a new one:
```bash
curl -X POST https://appflowy.ark-node.com/gotrue/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@arknode.local","password":"your-password"}'
```

### No Tasks/Docs Synced
Check that:
1. Environment variables are set correctly
2. Database ID is correct
3. Files exist in the repository
4. You have write access to the workspace

---

## Script Comparison

| Script | Status | API Approach | Use Case |
|--------|--------|--------------|----------|
| `sync_docs_report.py` | ✓ Ready | Read-only | Understand options |
| `sync_docs_database.py` | ✓ Ready | Database rows | Sync documentation |
| `sync_docs.py` | ✗ Deprecated | Pages/folders | Don't use |
| `sync_tasks.py` | ✓ Working | Database rows | Sync tasks |

---

## Next Steps

1. Run `sync_docs_report.py` to understand your options
2. Create Documentation database in AppFlowy UI
3. Configure `APPFLOWY_DOCS_DATABASE_ID` in `.env`
4. Sync docs: `python sync_docs_database.py`
5. Sync tasks: `python sync_tasks.py`
6. Set up automation (cron, git hooks, CI/CD)

See the workflow documentation in `../workflows/` for automation options.
