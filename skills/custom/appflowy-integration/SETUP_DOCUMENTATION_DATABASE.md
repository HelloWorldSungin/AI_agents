# AppFlowy Documentation Database Setup Instructions

## Overview
This guide will help you create a "Documentation" database in AppFlowy to sync AI_agents repository documentation automatically.

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Create "Documentation" Database in AppFlowy UI          │
│    - Add required fields (Title, Content, Category, etc.)  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Get Database ID from AppFlowy URL                       │
│    - Copy from browser address bar                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Add APPFLOWY_DOCS_DATABASE_ID to .env file              │
│    - Located in appflowy-deployment/.env                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Test Connection (test_connection.py)                    │
│    - Validates environment variables                        │
│    - Checks database access                                 │
│    - Verifies field schema                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Dry-Run Test (sync_docs_database.py --dry-run)         │
│    - Shows what would be synced                            │
│    - No actual changes made                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Run Full Sync (sync_docs_database.py)                  │
│    - Syncs 14 documentation files                          │
│    - Creates database rows                                  │
│    - Tracks sync status                                     │
└─────────────────────────────────────────────────────────────┘
```

## Setup Steps

### 1. Create the Documentation Database

1. **Open AppFlowy** and navigate to your **AI Agents** workspace
2. **Create a new database**:
   - Click the "+" button or "Add a page" in the sidebar
   - Select **"Database"** or **"Board"** (you can change views later)
   - Name it: **"Documentation"**
   - Place it in the **General space** (next to your "Project Management" database)

### 2. Configure Database Fields

The database needs these fields with exact names (case-sensitive):

| Field Name | Field Type | Configuration | Required |
|------------|------------|---------------|----------|
| **Title** | Text | Primary field (default) | YES |
| **Content** | Long Text | - | YES |
| **Category** | Select | Options: Getting Started, Guides, Reference, Examples | YES |
| **FilePath** | Text | - | YES |
| **LastUpdated** | Date | - | YES |
| **Status** | Select | Options: Draft, Published, Archived | Optional |

#### Step-by-step Field Creation:

1. **Title** - Already created as the primary field
   - No changes needed

2. **Content** - Add Long Text field
   - Click "+" to add a field
   - Select **"Long Text"** type
   - Name it: **"Content"**

3. **Category** - Add Select field
   - Click "+" to add a field
   - Select **"Select"** type
   - Name it: **"Category"**
   - Add these options:
     - Getting Started
     - Guides
     - Reference
     - Examples

4. **FilePath** - Add Text field
   - Click "+" to add a field
   - Select **"Text"** type
   - Name it: **"FilePath"**

5. **LastUpdated** - Add Date field
   - Click "+" to add a field
   - Select **"Date"** type
   - Name it: **"LastUpdated"**

6. **Status** - Add Select field (optional)
   - Click "+" to add a field
   - Select **"Select"** type
   - Name it: **"Status"**
   - Add these options:
     - Draft
     - Published
     - Archived

### 3. Get the Database ID

1. **Open the Documentation database** in AppFlowy
2. **Copy the database URL** from your browser or the share dialog
3. **Extract the database ID**:
   - URL format: `https://appflowy.ark-node.com/workspace/{workspace_id}/database/{database_id}`
   - The database ID is the UUID after `/database/`
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

### 4. Update Environment Variables

Add the database ID to your `.env` file:

```bash
# Documentation Database
APPFLOWY_DOCS_DATABASE_ID=your-database-id-here
```

Full path: `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`

Example:
```bash
APPFLOWY_DOCS_DATABASE_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 5. Test the Sync Script

Run in dry-run mode to verify everything is configured correctly:

```bash
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
python sync_docs_database.py --dry-run
```

Expected output:
- Database schema validation should pass
- 14 documents should be detected
- Field mappings should be displayed
- No errors should occur

### 6. Run the First Sync

Once dry-run succeeds, run the actual sync:

```bash
python sync_docs_database.py
```

This will:
- Sync 14 documentation files to the database
- Create a row for each document
- Track sync status for incremental updates

## What Gets Synced

The script will sync these 14 documentation files:

### Getting Started (2 files)
- README.md → README
- docs/reference/CHEAT_SHEET/00-quick-start.md → Quick Start
- starter-templates/README.md → Starter Templates

### Guides (5 files)
- docs/guides/ARCHITECTURE.md → Architecture
- docs/guides/Context_Engineering.md → Context Engineering
- docs/guides/SKILLS_GUIDE.md → Skills Guide
- docs/guides/PRACTICAL_WORKFLOW_GUIDE.md → Practical Workflow
- docs/guides/E2E_TESTING.md → E2E Testing
- docs/guides/LONG_RUNNING_AGENTS.md → Long Running Agents

### Reference (3 files)
- docs/reference/CHEAT_SHEET.md → Cheat Sheet Index
- docs/reference/FAQ.md → FAQ
- docs/reference/CHEAT_SHEET/01-state-files.md → State Files

### Examples (2 files)
- examples/web-app-team/README.md → Web App Team
- examples/mobile-app-team/README.md → Mobile App Team

## Script Features

### Auto-Detection
- **Field IDs are automatically detected** from the database schema
- No need to hardcode field IDs in the script
- Works with any database that has the required fields

### Incremental Sync
- Only syncs files that have changed (using MD5 hash comparison)
- Tracks sync status in `.sync-status-db.json`
- Updates existing rows instead of creating duplicates

### Options
```bash
python sync_docs_database.py --dry-run    # Test without syncing
python sync_docs_database.py --force      # Re-sync all files
python sync_docs_database.py              # Normal incremental sync
```

## Troubleshooting

### Missing Fields Error
If you see "Missing required fields", ensure:
- Field names match exactly (case-sensitive)
- All required fields are created
- Database ID is correct in .env file

### Authentication Error
If you see "Authentication failed":
- Check that APPFLOWY_API_TOKEN is valid (expires after 7 days)
- Re-generate token if expired
- Verify workspace access

### Database Not Found
If you see "Database not found":
- Verify APPFLOWY_DOCS_DATABASE_ID in .env
- Ensure database exists in the AI Agents workspace
- Check database permissions

## Next Steps

After successful sync:
1. **View the synced documents** in AppFlowy
2. **Organize by category** using the Category field
3. **Create views** (Kanban, Calendar, etc.) to organize documentation
4. **Set up regular syncs** using cron or a task scheduler
5. **Share the database** with team members

## Support

For issues or questions:
- Check the script logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure database structure matches the requirements above
