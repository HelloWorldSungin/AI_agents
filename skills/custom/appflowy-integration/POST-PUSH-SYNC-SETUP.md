# Git Post-Push Sync Setup for AppFlowy

## Overview

This setup provides automatic AppFlowy synchronization after pushing to remote. It keeps local commits fast and only syncs "finalized" work that has been pushed.

## Architecture

Since Git doesn't have a native `post-push` hook, we use a **git alias** approach:
- Git alias `pushsync` combines `git push` + sync script
- Wrapper script runs both sync operations (tasks and docs)
- Clear colored output shows sync progress and results

## Files Created

### 1. Post-Push Sync Script
**Location:** `/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts/post-push-sync.sh`

**Features:**
- Loads AppFlowy credentials from `.env` file
- Runs `sync_tasks.py` to sync tasks to Kanban board
- Runs `sync_docs.py` to sync documentation to workspace
- Handles errors gracefully with clear status reporting
- Colored output for easy reading
- Returns appropriate exit codes

**Configuration:**
- Repository: `/Users/sunginkim/GIT/AI_agents`
- Credentials: `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`
- Workspace ID: `c9674d81-6037-4dc3-9aa6-e2d833162b0f`
- Database ID: `6f9c57aa-dda0-4aac-ba27-54544d85270e`

### 2. Git Alias Configuration
**Alias:** `pushsync`

**Command:**
```bash
git pushsync [git push arguments]
```

**What it does:**
1. Runs `git push "$@"` with all your arguments
2. If push succeeds, runs the AppFlowy sync script
3. Reports sync results with colored output

## Usage

### Basic Push and Sync
```bash
# Instead of: git push
# Use: git pushsync
git pushsync
```

### Push to Specific Remote/Branch
```bash
# Push to specific branch and sync
git pushsync origin feature-branch

# Force push and sync (be careful!)
git pushsync --force
```

### Regular Push (Without Sync)
```bash
# If you want to push without syncing, use regular push
git push
```

## Testing

### Test the Sync Script Directly
```bash
cd /Users/sunginkim/GIT/AI_agents
./skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

Expected output:
```
════════════════════════════════════════════════════════════
         AppFlowy Post-Push Sync
════════════════════════════════════════════════════════════

📋 Loading environment from .env...
✅ Environment loaded

════════════════════════════════════════════════════════════
📋 Syncing Tasks to AppFlowy...
════════════════════════════════════════════════════════════

[Task sync output...]
✅ Tasks synced successfully

════════════════════════════════════════════════════════════
📄 Syncing Documentation to AppFlowy...
════════════════════════════════════════════════════════════

[Documentation sync output...]
✅ Documentation synced successfully

════════════════════════════════════════════════════════════
         Sync Summary
════════════════════════════════════════════════════════════

  📋 Tasks:         ✅ Success
  📄 Documentation: ✅ Success

════════════════════════════════════════════════════════════

🎉 All syncs completed successfully!
```

### Test the Git Alias
```bash
# Create a test commit
echo "test" > test.txt
git add test.txt
git commit -m "test: git pushsync alias"

# Test pushsync (will push and then sync)
git pushsync

# Clean up test
git reset --hard HEAD~1
git push --force  # Only if you pushed the test commit
```

## Verification

### Check Git Alias Configuration
```bash
git config --get alias.pushsync
```

Expected output:
```
!git push "$@" && /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

### Check Script Permissions
```bash
ls -la /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

Expected output should include execute permissions (`-rwx`):
```
-rwxr-xr-x  1 sunginkim  staff  [size]  [date]  post-push-sync.sh
```

### Check Environment File
```bash
ls -la /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env
```

Should exist and contain:
- `APPFLOWY_API_URL`
- `APPFLOWY_API_TOKEN`

## Troubleshooting

### Sync Fails with "Environment not found"
**Problem:** `.env` file not found or unreadable

**Solution:**
```bash
# Check if .env exists
ls -la /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env

# If missing, create it with required variables
cat > /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env << 'EOF'
APPFLOWY_API_URL=https://your-api-url
APPFLOWY_API_TOKEN=your-token-here
EOF
```

### Sync Scripts Not Found
**Problem:** Python scripts missing from scripts directory

**Solution:**
```bash
# Verify scripts exist
ls -la /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts/sync_*.py

# If missing, you may need to restore them from git history
git checkout HEAD -- skills/custom/appflowy-integration/scripts/
```

### Push Succeeds but Sync Fails
**Problem:** Sync errors don't prevent the push from completing (which is intentional)

**Impact:** Your code is pushed, but AppFlowy isn't updated

**Solution:**
1. Check the error message in the colored output
2. Fix the issue (usually credentials or network)
3. Run sync manually:
   ```bash
   ./skills/custom/appflowy-integration/scripts/post-push-sync.sh
   ```

### Authentication Errors
**Problem:** `401 Unauthorized` or `403 Forbidden` errors

**Solution:**
```bash
# 1. Verify token is valid
cat /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env | grep TOKEN

# 2. Test connection manually
cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
python3 sync_tasks.py --dry-run

# 3. If token expired, get a new one from AppFlowy and update .env
```

### Script Runs but Nothing Syncs
**Problem:** "Skipped: 14" messages (everything up to date)

**This is normal!** The scripts use incremental sync:
- Only changed files/tasks are synced
- Saves time and API calls
- To force a full sync:
  ```bash
  cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts
  python3 sync_tasks.py --force
  python3 sync_docs.py --force
  ```

## Alternative Approaches

### Option 1: Shell Alias (Global)
If you want this behavior for all repositories:

**For Zsh (macOS default):**
```bash
# Add to ~/.zshrc
echo 'alias gpushsync="git push && cd /Users/sunginkim/GIT/AI_agents && ./skills/custom/appflowy-integration/scripts/post-push-sync.sh"' >> ~/.zshrc
source ~/.zshrc

# Usage
gpushsync
```

**For Bash:**
```bash
# Add to ~/.bashrc or ~/.bash_profile
echo 'alias gpushsync="git push && cd /Users/sunginkim/GIT/AI_agents && ./skills/custom/appflowy-integration/scripts/post-push-sync.sh"' >> ~/.bashrc
source ~/.bashrc

# Usage
gpushsync
```

### Option 2: Manual Sync After Push
```bash
# Regular workflow
git push

# Manually sync when you want
cd /Users/sunginkim/GIT/AI_agents
./skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

### Option 3: Pre-Commit Hook (Not Recommended)
You could use a `pre-commit` hook, but this would:
- Slow down every commit (even local ones)
- Run sync before code is pushed
- Not suitable for this use case

## Maintenance

### Update Workspace/Database IDs
If you need to change the target workspace or database:

1. Edit the script:
   ```bash
   vim /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts/post-push-sync.sh
   ```

2. Update these lines:
   ```bash
   export APPFLOWY_WORKSPACE_ID="your-new-workspace-id"
   export APPFLOWY_DATABASE_ID="your-new-database-id"
   ```

### Update Script Path
If you move the repository:

1. Update git alias:
   ```bash
   git config alias.pushsync '!git push "$@" && /new/path/to/post-push-sync.sh'
   ```

2. Update script variables:
   ```bash
   vim /new/path/to/post-push-sync.sh
   # Update REPO_ROOT and ENV_FILE variables
   ```

### Disable Sync
To temporarily disable automatic sync:

**Method 1: Use regular push**
```bash
git push  # Instead of git pushsync
```

**Method 2: Remove alias**
```bash
git config --unset alias.pushsync
```

**Method 3: Comment out git alias**
```bash
# Add a comment to disable
git config alias.pushsync '!echo "Sync disabled" && git push "$@"'
```

## Integration with Team Workflows

### For Team Repositories
If working with a team, you may want to:

1. **Document the alias** in your team's README
2. **Make it optional** - team members can choose to use `pushsync` or regular `push`
3. **Share the setup script** - create an install script for team members
4. **Use environment variables** - each team member can have their own credentials

### Example Team Setup Script
```bash
#!/bin/bash
# setup-appflowy-sync.sh

# Install git alias
git config alias.pushsync '!git push "$@" && ./skills/custom/appflowy-integration/scripts/post-push-sync.sh'

# Create .env template if not exists
if [ ! -f ~/.appflowy-credentials ]; then
    cat > ~/.appflowy-credentials << 'EOF'
APPFLOWY_API_URL=https://your-team-url
APPFLOWY_API_TOKEN=your-personal-token
EOF
    echo "Created ~/.appflowy-credentials - please update with your credentials"
fi

echo "Setup complete! Use 'git pushsync' to push and sync."
```

## Performance Considerations

### Sync Time
- Task sync: ~1-3 seconds (incremental)
- Documentation sync: ~2-5 seconds (incremental)
- **Total: ~3-8 seconds** added to each push

### Optimization Tips
1. **Incremental sync** (default) - only syncs changes
2. **Skip if no changes** - use regular `git push` for quick pushes
3. **Batch commits** - push multiple commits at once
4. **Background sync** (advanced) - modify script to run in background

## Security Notes

### Credentials Protection
- `.env` file contains sensitive tokens
- **Never commit** `.env` files to git
- Store `.env` outside of repository if possible
- Use environment variables or secret management tools in production

### Token Expiration
- AppFlowy tokens may expire
- Update `.env` file when tokens change
- Test sync regularly to catch authentication issues

## Success Indicators

### Everything Working Correctly
- ✅ `git pushsync` completes without errors
- ✅ Both tasks and docs show "Success" in summary
- ✅ Changes appear in AppFlowy workspace within seconds
- ✅ "Skipped" messages for unchanged content (expected)
- ✅ "Synced" messages for changed content

### Something Needs Attention
- ⚠️ Partial success (one sync works, other fails)
- ⚠️ Network timeouts (may need retry)
- ⚠️ Warning messages (non-critical issues)

### Critical Issues
- ❌ Both syncs fail
- ❌ Authentication errors
- ❌ Script not found errors
- ❌ Permission denied errors

## Next Steps

1. **Test with a real commit:**
   ```bash
   # Make a change
   echo "# Test sync" >> test-sync.md
   git add test-sync.md
   git commit -m "test: verify pushsync works"
   git pushsync

   # Clean up
   rm test-sync.md
   git add test-sync.md
   git commit -m "test: cleanup"
   git pushsync
   ```

2. **Monitor AppFlowy workspace** to verify changes appear

3. **Share with team** if working in a team environment

4. **Set up monitoring** (optional) - log sync results for tracking

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review sync logs in terminal output
3. Test individual components (script, git alias, sync scripts)
4. Verify credentials and network connectivity

---

**Document Version:** 1.0
**Last Updated:** 2025-12-08
**Status:** Production Ready
