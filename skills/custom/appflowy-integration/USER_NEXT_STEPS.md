# Next Steps: Setting Up AppFlowy Documentation Sync

## Overview

Your documentation sync system is ready! The script can automatically sync 14 AI_agents documentation files to your AppFlowy workspace using a database approach.

## What's Been Done

- **sync_docs_database.py** updated with field ID auto-detection
- **test_connection.py** created to validate setup
- Complete setup documentation created
- All 14 documentation files verified and ready to sync

## What You Need to Do (7 minutes)

### Step 1: Create Documentation Database (5 min)

1. **Open AppFlowy** at https://appflowy.ark-node.com
2. **Navigate to "AI Agents" workspace**
3. **Create new database**:
   - Click "+" or "Add a page" in sidebar
   - Select "Database" or "Board"
   - Name: "Documentation"
   - Place next to "Project Management"

4. **Add fields** (click "+" to add each field):

   | Field Name | Type | Configuration |
   |------------|------|---------------|
   | **Title** | Text | Already exists (primary) |
   | **Content** | Long Text | Just create it |
   | **Category** | Select | Add options: Getting Started, Guides, Reference, Examples |
   | **FilePath** | Text | Just create it |
   | **LastUpdated** | Date | Just create it |
   | **Status** | Select | Add options: Draft, Published, Archived (optional) |

   **IMPORTANT:** Field names must match exactly (case-sensitive)!

5. **Get Database ID**:
   - Look at the URL in your browser
   - Format: `https://appflowy.ark-node.com/workspace/{workspace-id}/database/{DATABASE-ID}`
   - Copy the DATABASE-ID (the UUID after `/database/`)
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

### Step 2: Update .env File (1 min)

1. **Open:** `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`

2. **Add this line** at the end:
   ```bash
   APPFLOWY_DOCS_DATABASE_ID=your-database-id-here
   ```

3. **Replace** `your-database-id-here` with the actual database ID from Step 1

4. **Save the file**

### Step 3: Test Connection (30 sec)

```bash
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
python3 test_connection.py
```

**Expected output:**
```
✓ Environment variables loaded
✓ Connected - 5 workspace(s) accessible
✓ Database found
Fields found:
  - Title: {field-id}
  - Content: {field-id}
  - Category: {field-id}
  - FilePath: {field-id}
  - LastUpdated: {field-id}
✓ All required fields present
✓ Setup Complete!
```

**If you see errors:**
- Missing fields: Create them in AppFlowy (see Step 1)
- Database not found: Check database ID in .env
- Auth error: Token may have expired

### Step 4: Sync Documentation (30 sec)

**First, test with dry-run:**
```bash
python3 sync_docs_database.py --dry-run
```

**If dry-run succeeds (no errors), sync for real:**
```bash
python3 sync_docs_database.py
```

**Expected output:**
```
============================================================
AppFlowy Documentation Sync (Database Mode)
============================================================
Repository: /Users/sunginkim/GIT/AI_agents
Workspace ID: c9674d81-6037-4dc3-9aa6-e2d833162b0f
Database ID: {your-database-id}
Total documents: 14
Mode: LIVE SYNC
============================================================
Database fields detected:
  - Title: {field-id}
  - Content: {field-id}
  - Category: {field-id}
  - FilePath: {field-id}
  - LastUpdated: {field-id}
Database schema validation: PASSED
============================================================
Sync README.md -> Getting Started/README (never synced)
Created 'README' (ID: ...)
... (13 more files)
============================================================
Sync Summary
============================================================
Synced:  14
Skipped: 0
Failed:  0
Total:   14
============================================================
```

## You're Done!

Go to AppFlowy and you'll see:
- 14 rows in your Documentation database
- Each row has:
  - Title (document name)
  - Content (full markdown)
  - Category (Getting Started, Guides, Reference, Examples)
  - FilePath (source location)
  - LastUpdated (timestamp)

## What Gets Synced

### Getting Started (3 docs)
- README
- Quick Start
- Starter Templates

### Guides (6 docs)
- Architecture
- Context Engineering
- Skills Guide
- Practical Workflow
- E2E Testing
- Long Running Agents

### Reference (3 docs)
- Cheat Sheet Index
- FAQ
- State Files

### Examples (2 docs)
- Web App Team
- Mobile App Team

## Using the Documentation Database

Now you can:
- **Search** across all documentation
- **Filter by Category** to find specific types of docs
- **Create views**:
  - Kanban board (by Category)
  - Calendar (by LastUpdated)
  - Gallery view
- **Share** with team members
- **Add custom fields** (Tags, Priority, etc.)

## Running Sync Again

The script uses incremental sync - it only syncs files that changed.

```bash
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts

# Normal sync (only changed files)
python3 sync_docs_database.py

# Force re-sync all files
python3 sync_docs_database.py --force
```

**Output on subsequent runs:**
```
Sync Summary
============================================================
Synced:  2   (only files that changed)
Skipped: 12  (unchanged files)
Failed:  0
Total:   14
============================================================
```

## Automation (Optional)

Set up automatic sync every hour:

```bash
# Edit crontab
crontab -e

# Add this line:
0 * * * * cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && python3 sync_docs_database.py >> /tmp/appflowy-sync.log 2>&1
```

## Troubleshooting

### Error: Missing APPFLOWY_DOCS_DATABASE_ID
**Fix:** Add the database ID to your .env file (Step 2)

### Error: Missing required fields: Content, Category...
**Fix:** Create the missing fields in AppFlowy (Step 1, item 4)

### Error: Database not found
**Fix:**
- Verify the database ID in .env is correct
- Make sure you created the database in the AI Agents workspace
- Check that you have access permissions

### Error: Authentication failed
**Fix:**
- Your token may have expired (7 days validity)
- Check the token expiration date in .env file
- If expired, regenerate the token

### Error: Field 'Category' not found in database schema
**Fix:**
- Field names must match exactly (case-sensitive)
- Open AppFlowy and check field names
- Rename fields if needed to match: Title, Content, Category, FilePath, LastUpdated

## Need More Help?

- **Quick Start Guide:** [QUICK_START_DOCS_SYNC.md](QUICK_START_DOCS_SYNC.md)
- **Detailed Setup:** [SETUP_DOCUMENTATION_DATABASE.md](SETUP_DOCUMENTATION_DATABASE.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Main README:** [README.md](README.md)

## Summary

The system is ready - just:
1. Create the database in AppFlowy (5 min)
2. Add database ID to .env (1 min)
3. Run test_connection.py (30 sec)
4. Run sync_docs_database.py (30 sec)

Total time: **~7 minutes**

After that, your documentation will be synced and searchable in AppFlowy!
