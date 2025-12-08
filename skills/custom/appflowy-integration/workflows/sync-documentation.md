# Documentation Sync Workflow

## Overview

The `sync_docs.py` script syncs AI_agents documentation files to your AppFlowy workspace, creating a hierarchical folder structure that mirrors the repository organization. The script supports incremental updates, tracking sync status to avoid redundant syncs.

## Quick Start

```bash
# Navigate to scripts directory
cd skills/custom/appflowy-integration/scripts/

# Preview what would be synced (dry run)
python3 sync_docs.py --dry-run

# Sync changed files only
python3 sync_docs.py

# Force re-sync all files
python3 sync_docs.py --force
```

## Prerequisites

### Environment Variables

The script requires the following environment variables:

```bash
export APPFLOWY_API_URL="https://appflowy.ark-node.com"
export APPFLOWY_API_TOKEN="your_jwt_token_here"
export APPFLOWY_WORKSPACE_ID="22bcbccd-9cf3-41ac-aa0b-28fe144ba71d"
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
python3 sync_docs.py --env-file /path/to/custom/.env
```

## Configuration Options

### Command Line Arguments

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Preview changes without syncing | `python3 sync_docs.py --dry-run` |
| `--force` | Re-sync all files, ignoring status | `python3 sync_docs.py --force` |
| `--env-file PATH` | Custom .env file location | `python3 sync_docs.py --env-file ~/.env` |

### Synced Documents

The script syncs the following 14 documentation files:

**Getting Started:**
- `README.md` → Getting Started/README
- `docs/reference/CHEAT_SHEET/00-quick-start.md` → Getting Started/Quick Start
- `starter-templates/README.md` → Getting Started/Starter Templates

**Guides:**
- `docs/guides/ARCHITECTURE.md` → Guides/Architecture
- `docs/guides/Context_Engineering.md` → Guides/Context Engineering
- `docs/guides/SKILLS_GUIDE.md` → Guides/Skills Guide
- `docs/guides/PRACTICAL_WORKFLOW_GUIDE.md` → Guides/Practical Workflow
- `docs/guides/E2E_TESTING.md` → Guides/E2E Testing
- `docs/guides/LONG_RUNNING_AGENTS.md` → Guides/Long Running Agents

**Reference:**
- `docs/reference/CHEAT_SHEET.md` → Reference/Cheat Sheet Index
- `docs/reference/FAQ.md` → Reference/FAQ
- `docs/reference/CHEAT_SHEET/01-state-files.md` → Reference/State Files

**Examples:**
- `examples/web-app-team/README.md` → Examples/Web App Team
- `examples/mobile-app-team/README.md` → Examples/Mobile App Team

## How It Works

### Incremental Sync Logic

The script uses MD5 hashing to track file changes:

1. **First Run:** All files are synced and status is saved
2. **Subsequent Runs:** Only files with changed content are synced
3. **Force Mode:** All files are re-synced regardless of status

### Sync Status Tracking

Sync status is stored in:
```
skills/custom/appflowy-integration/.sync-status.json
```

This file tracks:
- Last sync timestamp
- MD5 hash of each file
- AppFlowy page ID for each document
- Folder structure IDs

Example `.sync-status.json`:
```json
{
  "last_sync": "2025-12-08T07:42:30Z",
  "synced_files": {
    "README.md": {
      "hash": "a1b2c3d4e5f6",
      "page_id": "page-12345",
      "page_name": "README",
      "folder_name": "Getting Started",
      "last_sync": "2025-12-08T07:42:30Z"
    }
  },
  "folder_ids": {
    "Getting Started": "folder-67890",
    "Guides": "folder-54321"
  }
}
```

## Expected Output

### Dry Run Mode

```
2025-12-08 07:40:00 - INFO - Testing AppFlowy connection...
2025-12-08 07:40:01 - INFO - Connected to AppFlowy - 3 workspace(s) accessible
2025-12-08 07:40:01 - INFO - ============================================================
2025-12-08 07:40:01 - INFO - AppFlowy Documentation Sync
2025-12-08 07:40:01 - INFO - ============================================================
2025-12-08 07:40:01 - INFO - Repository: /Users/sunginkim/GIT/AI_agents
2025-12-08 07:40:01 - INFO - Workspace ID: 22bcbccd-9cf3-41ac-aa0b-28fe144ba71d
2025-12-08 07:40:01 - INFO - Total documents: 14
2025-12-08 07:40:01 - INFO - Mode: DRY RUN
2025-12-08 07:40:01 - INFO - ============================================================
2025-12-08 07:40:01 - INFO - DRY RUN: Would create folder 'Getting Started'
2025-12-08 07:40:01 - INFO - DRY RUN: Would sync 'README' to folder 'Getting Started'
2025-12-08 07:40:01 - INFO -          Content size: 5234 bytes
2025-12-08 07:40:01 - INFO - Syncing README.md -> Getting Started/README (never synced)
...
2025-12-08 07:40:05 - INFO - ============================================================
2025-12-08 07:40:05 - INFO - Sync Summary
2025-12-08 07:40:05 - INFO - ============================================================
2025-12-08 07:40:05 - INFO - Synced:  14
2025-12-08 07:40:05 - INFO - Skipped: 0
2025-12-08 07:40:05 - INFO - Failed:  0
2025-12-08 07:40:05 - INFO - Total:   14
2025-12-08 07:40:05 - INFO - ============================================================
```

### Live Sync Mode

```
2025-12-08 07:42:00 - INFO - Testing AppFlowy connection...
2025-12-08 07:42:01 - INFO - Connected to AppFlowy - 3 workspace(s) accessible
2025-12-08 07:42:01 - INFO - ============================================================
2025-12-08 07:42:01 - INFO - AppFlowy Documentation Sync
2025-12-08 07:42:01 - INFO - ============================================================
2025-12-08 07:42:01 - INFO - Repository: /Users/sunginkim/GIT/AI_agents
2025-12-08 07:42:01 - INFO - Workspace ID: 22bcbccd-9cf3-41ac-aa0b-28fe144ba71d
2025-12-08 07:42:01 - INFO - Total documents: 14
2025-12-08 07:42:01 - INFO - Mode: LIVE SYNC
2025-12-08 07:42:01 - INFO - ============================================================
2025-12-08 07:42:02 - INFO - Created folder 'Getting Started' (ID: folder-67890)
2025-12-08 07:42:03 - INFO - Created page 'README' (ID: page-12345)
2025-12-08 07:42:03 - INFO - Syncing README.md -> Getting Started/README (never synced)
2025-12-08 07:42:04 - INFO - Skipping docs/guides/ARCHITECTURE.md - up to date
2025-12-08 07:42:05 - INFO - Updated page 'Context Engineering'
2025-12-08 07:42:05 - INFO - Syncing docs/guides/Context_Engineering.md -> Guides/Context Engineering (content changed)
...
2025-12-08 07:42:20 - INFO - Sync status saved to .sync-status.json
2025-12-08 07:42:20 - INFO - ============================================================
2025-12-08 07:42:20 - INFO - Sync Summary
2025-12-08 07:42:20 - INFO - ============================================================
2025-12-08 07:42:20 - INFO - Synced:  3
2025-12-08 07:42:20 - INFO - Skipped: 11
2025-12-08 07:42:20 - INFO - Failed:  0
2025-12-08 07:42:20 - INFO - Total:   14
2025-12-08 07:42:20 - INFO - ============================================================
```

## Verification

### 1. Check Sync Status

```bash
# View sync status file
cat skills/custom/appflowy-integration/.sync-status.json | jq .
```

### 2. Verify in AppFlowy UI

1. Open https://appflowy.ark-node.com
2. Navigate to your workspace
3. Check for folders: Getting Started, Guides, Reference, Examples
4. Open any page to verify content

### 3. Test Incremental Sync

```bash
# Make a change to a file
echo "\n## New Section" >> README.md

# Run sync (should only sync README.md)
python3 sync_docs.py

# Output should show:
# Synced: 1
# Skipped: 13
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

### Missing Files

**Error:** `File not found: docs/guides/ARCHITECTURE.md`

**Solution:**
- Verify file exists in repository
- Check file path is correct (case-sensitive)
- Ensure you're running from correct directory

### Permission Denied

**Error:** `Permission denied - check workspace access`

**Solution:**
- Verify workspace ID is correct
- Ensure your user has write access to the workspace
- Check token has required permissions

### Network Connection Issues

**Error:** `Failed to connect to AppFlowy: Connection refused`

**Solution:**
```bash
# Test connectivity
curl -v https://appflowy.ark-node.com/api/workspace

# Check DNS resolution
nslookup appflowy.ark-node.com

# Verify server is running
ssh admin@192.168.68.55
docker ps | grep appflowy
```

### Sync Status Corruption

**Error:** Sync status file corrupted or inconsistent

**Solution:**
```bash
# Delete sync status to start fresh
rm skills/custom/appflowy-integration/.sync-status.json

# Force re-sync all files
python3 sync_docs.py --force
```

### Script Exits with Code 1

**Common Causes:**
1. Authentication failure (401)
2. Missing environment variables
3. File not found in repository
4. Network connectivity issues

**Debug:**
```bash
# Run with verbose output
python3 sync_docs.py --dry-run 2>&1 | tee sync_log.txt

# Check exit code
echo $?
```

## Best Practices

### 1. Always Dry Run First

Before syncing, especially after code changes:
```bash
python3 sync_docs.py --dry-run
```

### 2. Use Version Control for .sync-status.json

Add to `.gitignore` if you don't want to track sync status:
```bash
echo ".sync-status.json" >> .gitignore
```

Or commit it to track what's synced across team members.

### 3. Automate with Cron

See `git-sync.md` for automated sync setup.

### 4. Monitor Sync Logs

Keep logs for troubleshooting:
```bash
python3 sync_docs.py 2>&1 | tee -a logs/sync_$(date +%Y%m%d_%H%M%S).log
```

### 5. Validate Before Syncing

```bash
# Check all files exist
for file in README.md docs/guides/ARCHITECTURE.md ...; do
  if [ ! -f "$file" ]; then
    echo "Missing: $file"
  fi
done
```

## Common Use Cases

### Initial Setup

```bash
# First time setup
cd skills/custom/appflowy-integration/scripts/
python3 sync_docs.py --dry-run   # Preview
python3 sync_docs.py             # Sync
```

### Daily Updates

```bash
# Only sync changed files (fast)
python3 sync_docs.py
```

### After Major Changes

```bash
# Force re-sync everything
python3 sync_docs.py --force
```

### Testing with Custom Credentials

```bash
# Use different workspace
python3 sync_docs.py --env-file ~/.env.test
```

## Integration with Git

See `git-sync.md` for:
- Git post-commit hooks
- Automated sync on push
- CI/CD integration
- Scheduled sync with cron

## Related Scripts

- `sync_tasks.py` - Sync tasks to AppFlowy Kanban
- `sync_docs.py` - This script (documentation sync)

## Support

For issues or questions:
1. Check this documentation
2. Review `references/api-reference.md`
3. Check AppFlowy logs: `docker logs appflowy-cloud`
4. Review sync status: `.sync-status.json`
