# Quick Start: AppFlowy Documentation Sync

## What This Does
Automatically syncs 14 AI_agents documentation files to your AppFlowy workspace as database rows, making it easy to browse, search, and organize documentation in AppFlowy.

## Setup (5 minutes)

### Step 1: Create Documentation Database in AppFlowy

1. Open AppFlowy and go to **AI Agents** workspace
2. Click **"+"** or **"Add a page"** in the sidebar
3. Select **Database** or **Board**
4. Name it: **"Documentation"**
5. Place it next to your "Project Management" database

### Step 2: Add Required Fields

Create these fields in the database (click "+" to add fields):

| Field Name | Type | Configuration |
|------------|------|---------------|
| Title | Text | (Already exists as primary field) |
| Content | Long Text | - |
| Category | Select | Options: Getting Started, Guides, Reference, Examples |
| FilePath | Text | - |
| LastUpdated | Date | - |
| Status | Select | Options: Draft, Published, Archived (optional) |

### Step 3: Get Database ID

1. Open the Documentation database
2. Copy the URL from your browser
3. Extract the database ID (the UUID after `/database/`)
   - URL format: `https://appflowy.ark-node.com/workspace/{workspace_id}/database/{DATABASE_ID}`
   - Example ID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

### Step 4: Update .env File

Edit: `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`

Add this line:
```bash
APPFLOWY_DOCS_DATABASE_ID=your-database-id-here
```

Replace `your-database-id-here` with the actual database ID from Step 3.

### Step 5: Test Connection

```bash
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
python3 test_connection.py
```

Expected output:
```
✓ Environment variables loaded
✓ Connected - 5 workspace(s) accessible
✓ Database found
✓ All required fields present
✓ Setup Complete!
```

### Step 6: Sync Documentation

**First, test with dry-run:**
```bash
python3 sync_docs_database.py --dry-run
```

**If successful, sync for real:**
```bash
python3 sync_docs_database.py
```

## What Gets Synced

14 documentation files organized into 4 categories:

### Getting Started (3 files)
- README
- Quick Start
- Starter Templates

### Guides (6 files)
- Architecture
- Context Engineering
- Skills Guide
- Practical Workflow
- E2E Testing
- Long Running Agents

### Reference (3 files)
- Cheat Sheet Index
- FAQ
- State Files

### Examples (2 files)
- Web App Team
- Mobile App Team

## Commands

### Test connection and database setup
```bash
python3 test_connection.py
```

### Dry-run (test without syncing)
```bash
python3 sync_docs_database.py --dry-run
```

### Normal sync (incremental - only changed files)
```bash
python3 sync_docs_database.py
```

### Force re-sync all files
```bash
python3 sync_docs_database.py --force
```

## How It Works

1. **Auto-detects field IDs** from your database schema (no hardcoding!)
2. **Tracks file changes** using MD5 hashes
3. **Incremental sync** - only syncs files that changed
4. **Updates existing rows** instead of creating duplicates
5. **Stores sync status** in `.sync-status-db.json`

## Troubleshooting

### Error: Missing required environment variables
**Fix:** Add `APPFLOWY_DOCS_DATABASE_ID` to your .env file

### Error: Database not found
**Fix:**
- Verify database ID in .env file
- Ensure database exists in AI Agents workspace
- Check you have access permissions

### Error: Missing required fields
**Fix:**
- Open Documentation database in AppFlowy
- Create missing fields (see Step 2)
- Ensure field names match exactly (case-sensitive)

### Error: Authentication failed
**Fix:**
- Token may have expired (7 days validity)
- Re-generate token using login script
- Update `APPFLOWY_API_TOKEN` in .env

## After First Sync

In AppFlowy, you can now:
- **Browse documentation** in a structured database
- **Filter by category** (Getting Started, Guides, Reference, Examples)
- **Search across all docs** using AppFlowy's search
- **Create different views** (Board, Calendar, Gallery, etc.)
- **Add custom fields** (Tags, Priority, etc.)
- **Share with team members**

## Regular Updates

Run the sync script whenever documentation changes:
```bash
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
python3 sync_docs_database.py
```

It will automatically detect and sync only the changed files.

## Advanced: Automated Sync

Set up a cron job to sync automatically:
```bash
# Edit crontab
crontab -e

# Add this line to sync every hour:
0 * * * * cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && python3 sync_docs_database.py
```

## Need Help?

- Read full documentation: [SETUP_DOCUMENTATION_DATABASE.md](SETUP_DOCUMENTATION_DATABASE.md)
- Check script logs for detailed error messages
- Verify environment variables are set correctly
- Test connection with `test_connection.py`
