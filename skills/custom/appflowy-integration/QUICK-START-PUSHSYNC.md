# Quick Start: Git PushSync

## What is PushSync?

**PushSync** automatically syncs your AI_agents repository to AppFlowy after pushing to remote. This keeps local commits fast and only syncs "finalized" work.

## How to Use

### Basic Usage
```bash
# Instead of: git push
# Use: git pushsync

git pushsync
```

That's it! The command will:
1. Push your commits to the remote repository
2. Automatically sync tasks to AppFlowy Kanban board
3. Automatically sync documentation to AppFlowy workspace
4. Show you a clear summary of what was synced

### Example Workflow
```bash
# 1. Make your changes
echo "new feature" >> feature.py

# 2. Commit locally
git add feature.py
git commit -m "feat: add new feature"

# 3. Push and sync to AppFlowy
git pushsync

# 4. See the results
# ════════════════════════════════════════════════════════════
#          AppFlowy Post-Push Sync
# ════════════════════════════════════════════════════════════
#
# 📋 Loading environment from .env...
# ✅ Environment loaded
#
# ════════════════════════════════════════════════════════════
# 📋 Syncing Tasks to AppFlowy...
# ════════════════════════════════════════════════════════════
# ✅ Tasks synced successfully
#
# ════════════════════════════════════════════════════════════
# 📄 Syncing Documentation to AppFlowy...
# ════════════════════════════════════════════════════════════
# ✅ Documentation synced successfully
#
# ════════════════════════════════════════════════════════════
#          Sync Summary
# ════════════════════════════════════════════════════════════
#
#   📋 Tasks:         ✅ Success
#   📄 Documentation: ✅ Success
#
# 🎉 All syncs completed successfully!
```

## When to Use Each Command

### Use `git pushsync` when:
- ✅ Pushing finalized work to remote
- ✅ Want to update AppFlowy immediately
- ✅ Completing a feature or milestone
- ✅ Sharing work with team

### Use regular `git push` when:
- ⚡ Need a quick push without sync
- ⚡ Making frequent WIP commits
- ⚡ Syncing to AppFlowy not needed yet
- ⚡ Offline or sync issues

## Advanced Usage

### Push to Specific Branch
```bash
# Push to feature branch and sync
git pushsync origin feature-branch
```

### Push with Options
```bash
# All git push options work
git pushsync --force-with-lease
git pushsync --set-upstream origin new-branch
git pushsync --tags
```

### Manual Sync (Without Push)
```bash
# If you already pushed, sync manually
cd /Users/sunginkim/GIT/AI_agents
./skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

## What Gets Synced?

### Tasks (to Kanban Board)
- Active tasks from `.ai-agents/state/team-communication.json`
- Planned phases from `.planning/ROADMAP.md`
- Session handoffs from `whats-next.md`

### Documentation (to Workspace)
- README files
- Architecture guides
- Reference documentation
- Examples and tutorials

## Troubleshooting

### "Command not found: git pushsync"
**Fix:** The alias is configured per-repository. Make sure you're in the AI_agents repository:
```bash
cd /Users/sunginkim/GIT/AI_agents
git pushsync
```

### Sync Fails but Push Succeeds
**This is intentional!** Your code is safely pushed. Fix the sync issue and run manually:
```bash
./skills/custom/appflowy-integration/scripts/post-push-sync.sh
```

### Everything Shows "Skipped"
**This is normal!** It means nothing changed since last sync. Only modified files/tasks are synced.

To force a full sync:
```bash
cd skills/custom/appflowy-integration/scripts
python3 sync_tasks.py --force
python3 sync_docs.py --force
```

## Quick Tests

### Test 1: Verify Alias Exists
```bash
git config --get alias.pushsync
# Should output: !git push "$@" && /path/to/post-push-sync.sh
```

### Test 2: Test Sync Script
```bash
./skills/custom/appflowy-integration/scripts/post-push-sync.sh
# Should show colored output and sync results
```

### Test 3: Test Full Workflow
```bash
# Create test file
echo "test" > test-pushsync.txt
git add test-pushsync.txt
git commit -m "test: pushsync"

# Push and sync
git pushsync

# Clean up
rm test-pushsync.txt
git add test-pushsync.txt
git commit -m "test: cleanup"
git pushsync
```

## Performance

- **Task Sync:** ~1-3 seconds
- **Doc Sync:** ~2-5 seconds
- **Total Overhead:** ~3-8 seconds per push

This is the cost of keeping AppFlowy in sync. If you need faster pushes, use regular `git push`.

## Configuration

The sync is configured for:
- **Repository:** `/Users/sunginkim/GIT/AI_agents`
- **Workspace ID:** `c9674d81-6037-4dc3-9aa6-e2d833162b0f`
- **Database ID:** `6f9c57aa-dda0-4aac-ba27-54544d85270e`
- **Credentials:** `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`

## More Information

For detailed documentation, see:
- **[POST-PUSH-SYNC-SETUP.md](POST-PUSH-SYNC-SETUP.md)** - Complete setup guide
- **Sync Scripts:**
  - `scripts/sync_tasks.py` - Task sync implementation
  - `scripts/sync_docs.py` - Documentation sync implementation
- **Wrapper Script:** `scripts/post-push-sync.sh` - Main sync orchestrator

---

**Quick Reference:**
- Use: `git pushsync` (instead of `git push`)
- Manual: `./skills/custom/appflowy-integration/scripts/post-push-sync.sh`
- Test: `git config --get alias.pushsync`
