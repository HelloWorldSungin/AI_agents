# Git Sync Automation Workflow

## Overview

This workflow describes how to automate AppFlowy syncing with git operations, scheduled tasks, and CI/CD pipelines. The sync scripts support multiple trigger mechanisms to keep your AppFlowy workspace up-to-date with repository changes.

## Sync Triggers

### 1. Manual Sync

Run sync scripts manually when needed:

```bash
# Sync documentation
cd skills/custom/appflowy-integration/scripts/
python3 sync_docs.py

# Sync tasks
python3 sync_tasks.py

# Sync both
python3 sync_docs.py && python3 sync_tasks.py
```

**When to use:**
- Testing sync configuration
- One-time sync after major changes
- Debugging sync issues
- Ad-hoc updates

### 2. Git Hooks

Automatically sync when committing or pushing changes.

#### Post-Commit Hook

Sync after each local commit:

**Setup:**
```bash
# Create post-commit hook
cat > .git/hooks/post-commit <<'EOF'
#!/bin/bash
# AppFlowy Sync on Commit
# Syncs docs and tasks to AppFlowy after each commit

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS_DIR="$REPO_ROOT/skills/custom/appflowy-integration/scripts"

# Load environment variables
if [ -f "/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env" ]; then
    export $(cat "/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env" | grep -v '^#' | xargs)
fi

echo "Syncing to AppFlowy..."

# Sync documentation
cd "$SCRIPTS_DIR"
python3 sync_docs.py || echo "Warning: Documentation sync failed"

# Sync tasks
python3 sync_tasks.py || echo "Warning: Task sync failed"

echo "AppFlowy sync complete"
EOF

# Make executable
chmod +x .git/hooks/post-commit
```

**Test:**
```bash
# Make a test commit
echo "# Test" >> test.md
git add test.md
git commit -m "Test post-commit hook"

# Should see: "Syncing to AppFlowy..." output
```

**Pros:**
- Automatic sync on every commit
- No manual intervention
- Immediate updates

**Cons:**
- Slows down commit process
- Fails if AppFlowy is unreachable
- May sync incomplete work

#### Post-Push Hook

Sync after pushing to remote (server-side):

**Setup (Git Server):**
```bash
# On git server (e.g., GitHub Actions, GitLab CI, self-hosted)
cat > .git/hooks/post-receive <<'EOF'
#!/bin/bash
# AppFlowy Sync on Push
# Syncs docs and tasks to AppFlowy after each push

while read oldrev newrev refname; do
    if [ "$refname" = "refs/heads/master" ]; then
        echo "Master branch updated, syncing to AppFlowy..."

        # Clone or pull repo
        WORK_DIR="/tmp/ai-agents-sync"
        if [ -d "$WORK_DIR" ]; then
            cd "$WORK_DIR"
            git pull
        else
            git clone /path/to/repo.git "$WORK_DIR"
            cd "$WORK_DIR"
        fi

        # Load environment
        export $(cat /path/to/.env | grep -v '^#' | xargs)

        # Sync
        cd skills/custom/appflowy-integration/scripts/
        python3 sync_docs.py
        python3 sync_tasks.py

        echo "AppFlowy sync complete"
    fi
done
EOF

# Make executable
chmod +x .git/hooks/post-receive
```

**Pros:**
- Only syncs when pushing to specific branch
- Doesn't slow down local commits
- Syncs completed work only

**Cons:**
- Requires server-side setup
- Delayed sync (only on push)

#### Pre-Commit Hook (Validation)

Validate data sources before committing:

**Setup:**
```bash
# Create pre-commit hook for validation
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash
# Validate data sources before commit

echo "Validating data sources..."

# Check JSON files are valid
for file in .ai-agents/state/team-communication.json .ai-agents/state/feature-tracking.json; do
    if [ -f "$file" ]; then
        if ! jq empty "$file" 2>/dev/null; then
            echo "Error: $file is not valid JSON"
            exit 1
        fi
    fi
done

# Check ROADMAP.md exists
if [ ! -f ".planning/ROADMAP.md" ]; then
    echo "Warning: .planning/ROADMAP.md not found"
fi

echo "Validation passed"
exit 0
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### 3. Cron Jobs

Schedule automatic syncs at regular intervals.

#### Cron Setup (macOS/Linux)

**Edit crontab:**
```bash
crontab -e
```

**Add scheduled syncs:**
```cron
# Sync every hour during work hours (9am-6pm, Mon-Fri)
0 9-18 * * 1-5 cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && /usr/bin/python3 sync_docs.py && /usr/bin/python3 sync_tasks.py >> /tmp/appflowy-sync.log 2>&1

# Sync every 15 minutes (aggressive)
*/15 * * * * cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && /usr/bin/python3 sync_tasks.py >> /tmp/appflowy-sync.log 2>&1

# Sync once daily at 8am
0 8 * * * cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && /usr/bin/python3 sync_docs.py && /usr/bin/python3 sync_tasks.py >> /tmp/appflowy-sync.log 2>&1

# Sync on weekends (for maintenance tasks)
0 12 * * 0,6 cd /Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts && /usr/bin/python3 sync_docs.py --force >> /tmp/appflowy-sync.log 2>&1
```

**Cron Schedule Examples:**

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 5 minutes | `*/5 * * * *` | Very aggressive, for active development |
| Every 15 minutes | `*/15 * * * *` | Aggressive, for active projects |
| Every hour | `0 * * * *` | Moderate, for regular updates |
| Every 4 hours | `0 */4 * * *` | Light, for stable projects |
| Daily at 8am | `0 8 * * *` | Once daily |
| Work hours only | `0 9-18 * * 1-5` | Business hours, Mon-Fri |

**Create wrapper script for cron:**
```bash
cat > /Users/sunginkim/bin/appflowy-sync.sh <<'EOF'
#!/bin/bash
# AppFlowy Sync Wrapper for Cron
# Loads environment and runs sync scripts

# Set paths
REPO_ROOT="/Users/sunginkim/GIT/AI_agents"
SCRIPTS_DIR="$REPO_ROOT/skills/custom/appflowy-integration/scripts"
ENV_FILE="/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env"

# Load environment
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Change to scripts directory
cd "$SCRIPTS_DIR" || exit 1

# Sync (only changed files)
echo "=== AppFlowy Sync - $(date) ==="
python3 sync_docs.py
python3 sync_tasks.py
echo "=== Sync Complete - $(date) ==="
EOF

# Make executable
chmod +x /Users/sunginkim/bin/appflowy-sync.sh

# Update crontab to use wrapper
crontab -e
# Add: 0 * * * * /Users/sunginkim/bin/appflowy-sync.sh >> /tmp/appflowy-sync.log 2>&1
```

**View cron logs:**
```bash
tail -f /tmp/appflowy-sync.log
```

**Pros:**
- Reliable scheduled syncs
- No manual intervention
- Configurable frequency

**Cons:**
- Syncs even without changes (use incremental mode)
- Requires cron daemon running
- May miss immediate changes

#### Launchd Setup (macOS Alternative)

macOS prefers launchd over cron:

**Create launchd plist:**
```bash
cat > ~/Library/LaunchAgents/com.arknode.appflowy-sync.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arknode.appflowy-sync</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/sunginkim/bin/appflowy-sync.sh</string>
    </array>

    <key>StartInterval</key>
    <integer>3600</integer> <!-- Every hour -->

    <key>StandardOutPath</key>
    <string>/tmp/appflowy-sync.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/appflowy-sync-error.log</string>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# Load launchd job
launchctl load ~/Library/LaunchAgents/com.arknode.appflowy-sync.plist

# Start immediately
launchctl start com.arknode.appflowy-sync

# Check status
launchctl list | grep appflowy
```

**Unload launchd job:**
```bash
launchctl unload ~/Library/LaunchAgents/com.arknode.appflowy-sync.plist
```

### 4. CI/CD Integration

#### GitHub Actions

**Setup:**
```yaml
# .github/workflows/appflowy-sync.yml
name: AppFlowy Sync

on:
  push:
    branches: [master, main]
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install requests python-dotenv

      - name: Sync documentation
        env:
          APPFLOWY_API_URL: ${{ secrets.APPFLOWY_API_URL }}
          APPFLOWY_API_TOKEN: ${{ secrets.APPFLOWY_API_TOKEN }}
          APPFLOWY_WORKSPACE_ID: ${{ secrets.APPFLOWY_WORKSPACE_ID }}
        run: |
          cd skills/custom/appflowy-integration/scripts/
          python sync_docs.py

      - name: Sync tasks
        env:
          APPFLOWY_API_URL: ${{ secrets.APPFLOWY_API_URL }}
          APPFLOWY_API_TOKEN: ${{ secrets.APPFLOWY_API_TOKEN }}
          APPFLOWY_WORKSPACE_ID: ${{ secrets.APPFLOWY_WORKSPACE_ID }}
          APPFLOWY_DATABASE_ID: ${{ secrets.APPFLOWY_DATABASE_ID }}
        run: |
          cd skills/custom/appflowy-integration/scripts/
          python sync_tasks.py
```

**Configure secrets:**
1. Go to GitHub repository Settings → Secrets
2. Add secrets:
   - `APPFLOWY_API_URL`
   - `APPFLOWY_API_TOKEN`
   - `APPFLOWY_WORKSPACE_ID`
   - `APPFLOWY_DATABASE_ID`

#### GitLab CI

**Setup:**
```yaml
# .gitlab-ci.yml
appflowy-sync:
  stage: deploy
  image: python:3.10

  before_script:
    - pip install requests python-dotenv

  script:
    - cd skills/custom/appflowy-integration/scripts/
    - python sync_docs.py
    - python sync_tasks.py

  only:
    - master

  schedule:
    - cron: '0 */4 * * *'
      only:
        - master
```

## Incremental Sync Logic

The sync scripts implement intelligent incremental syncing:

### How It Works

1. **Hash Calculation:** MD5 hash computed for each file/task
2. **Status Tracking:** Hash stored in `.sync-status.json` or `.task-sync-status.json`
3. **Change Detection:** Current hash compared to stored hash
4. **Conditional Sync:** Only sync if hash changed or never synced

### Sync Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Incremental** (default) | Run without flags | Sync only changed items |
| **Force** | `--force` flag | Sync all items regardless of status |
| **Dry Run** | `--dry-run` flag | Preview without syncing |

### Examples

**Incremental sync (fast):**
```bash
python3 sync_docs.py
# Output: Synced: 2, Skipped: 12, Failed: 0
```

**Force sync (slow):**
```bash
python3 sync_docs.py --force
# Output: Synced: 14, Skipped: 0, Failed: 0
```

**Dry run (preview):**
```bash
python3 sync_docs.py --dry-run
# Output: Shows what would be synced without making changes
```

### When to Use Force Sync

- First time setup
- After database schema changes
- After .sync-status.json corruption
- After AppFlowy server migration
- Manual verification needed

## Conflict Handling

### Sync Direction: Repository → AppFlowy

**Important:** Sync is **one-way** from repository to AppFlowy.

- Repository is the **source of truth**
- AppFlowy is the **read-only view** (for viewing/tracking)
- Manual edits in AppFlowy will be **overwritten** on next sync

### Handling Conflicts

**Scenario 1: Edit in AppFlowy**
```
1. User edits task in AppFlowy UI
2. Next sync runs
3. Repository data overwrites AppFlowy changes
Result: AppFlowy edits lost
```

**Solution:** Edit in repository, then sync:
```bash
# Edit team-communication.json
vim .ai-agents/state/team-communication.json

# Sync to AppFlowy
python3 sync_tasks.py
```

**Scenario 2: Concurrent Edits**
```
1. User A edits repository file
2. User B edits same task in AppFlowy
3. User A syncs
Result: User B's changes overwritten
```

**Solution:** Use repository as single source of truth:
- All edits happen in repository files
- AppFlowy is view-only
- Use git for version control

**Scenario 3: Deleted Files**
```
1. File exists in AppFlowy
2. File deleted from repository
3. Sync runs
Result: File remains in AppFlowy (not deleted)
```

**Solution:** Manual cleanup:
- Script does not delete from AppFlowy
- Delete orphaned items manually in UI
- Or implement custom cleanup logic

### Best Practices

1. **Repository is authoritative:** All changes start in repository
2. **AppFlowy is read-only:** View and track progress only
3. **No bi-directional sync:** Keeps logic simple and prevents conflicts
4. **Manual AppFlowy edits discouraged:** Will be overwritten
5. **Use git for collaboration:** Version control for all changes

## Monitoring and Logging

### Log Output

**Basic logging (stdout):**
```bash
python3 sync_docs.py 2>&1 | tee -a sync.log
```

**Rotate logs by date:**
```bash
python3 sync_docs.py 2>&1 | tee -a logs/sync_$(date +%Y%m%d).log
```

**Separate stdout and stderr:**
```bash
python3 sync_docs.py > sync_out.log 2> sync_err.log
```

### Monitoring Sync Status

**Check last sync time:**
```bash
jq '.last_sync' skills/custom/appflowy-integration/.sync-status.json
jq '.last_sync' skills/custom/appflowy-integration/.task-sync-status.json
```

**Check synced files count:**
```bash
jq '.synced_files | length' skills/custom/appflowy-integration/.sync-status.json
```

**Check synced tasks count:**
```bash
jq '.synced_tasks | length' skills/custom/appflowy-integration/.task-sync-status.json
```

**Monitor for failures:**
```bash
# Check exit codes
python3 sync_docs.py
if [ $? -ne 0 ]; then
    echo "Sync failed!" | mail -s "AppFlowy Sync Failed" admin@example.com
fi
```

### Health Check Script

```bash
#!/bin/bash
# appflowy-sync-healthcheck.sh
# Monitors sync health and alerts on issues

SCRIPTS_DIR="/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/scripts"
SYNC_STATUS="$SCRIPTS_DIR/../.sync-status.json"
TASK_STATUS="$SCRIPTS_DIR/../.task-sync-status.json"

# Check last sync time (should be within 24 hours)
last_sync=$(jq -r '.last_sync' "$SYNC_STATUS")
last_sync_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_sync" +%s 2>/dev/null || echo 0)
now_epoch=$(date +%s)
hours_since_sync=$(( ($now_epoch - $last_sync_epoch) / 3600 ))

if [ $hours_since_sync -gt 24 ]; then
    echo "Warning: Last sync was $hours_since_sync hours ago"
    # Send alert
fi

# Check for sync failures
cd "$SCRIPTS_DIR"
python3 sync_docs.py --dry-run > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Documentation sync test failed"
    # Send alert
fi

python3 sync_tasks.py --dry-run > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Task sync test failed"
    # Send alert
fi

echo "Sync health check passed"
```

## Troubleshooting

### Sync Hook Not Running

**Issue:** Git hook doesn't execute

**Solution:**
```bash
# Check hook is executable
ls -l .git/hooks/post-commit
# Should show: -rwxr-xr-x

# Make executable if needed
chmod +x .git/hooks/post-commit

# Test hook directly
.git/hooks/post-commit
```

### Cron Job Not Running

**Issue:** Cron job not executing

**Solution:**
```bash
# Check cron daemon is running
pgrep cron || sudo service cron start

# Check crontab is configured
crontab -l

# Check cron logs
tail -f /var/log/syslog | grep CRON

# Test script manually
/Users/sunginkim/bin/appflowy-sync.sh
```

### Environment Variables Not Loading

**Issue:** Scripts can't find APPFLOWY_API_TOKEN

**Solution:**
```bash
# Check .env file exists
ls -la /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env

# Test loading manually
export $(cat /path/to/.env | grep -v '^#' | xargs)
echo $APPFLOWY_API_TOKEN

# Update wrapper script to debug
echo "TOKEN: $APPFLOWY_API_TOKEN" >> /tmp/debug.log
```

### Sync Taking Too Long

**Issue:** Sync delays commits or takes too long

**Solution:**
```bash
# Use incremental mode (default)
python3 sync_docs.py

# Run sync in background (post-commit hook)
(python3 sync_docs.py &)

# Switch to cron instead of hooks
# Remove post-commit hook, use cron
```

### Failed Syncs

**Issue:** Syncs consistently failing

**Solution:**
```bash
# Check connectivity
curl -v https://appflowy.ark-node.com/api/workspace

# Check token validity
curl -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  https://appflowy.ark-node.com/api/workspace

# Review error logs
python3 sync_docs.py 2>&1 | tee error.log

# Try dry run to diagnose
python3 sync_docs.py --dry-run
```

## Best Practices

1. **Start with dry runs:** Test sync logic before live syncing
2. **Use incremental mode:** Faster and more efficient
3. **Schedule during off-hours:** Avoid syncing during active development
4. **Monitor logs:** Set up log rotation and monitoring
5. **Test hooks locally:** Before relying on automation
6. **Keep .sync-status.json:** Track sync history
7. **Use git for changes:** Repository is source of truth
8. **Avoid manual AppFlowy edits:** Will be overwritten
9. **Set up alerts:** Get notified of sync failures
10. **Document your setup:** Team members need to know workflow

## Examples

### Complete Automation Setup

```bash
#!/bin/bash
# setup-appflowy-sync.sh
# Complete automation setup for AppFlowy sync

REPO_ROOT="/Users/sunginkim/GIT/AI_agents"

# 1. Create wrapper script
cat > /Users/sunginkim/bin/appflowy-sync.sh <<'EOF'
#!/bin/bash
REPO_ROOT="/Users/sunginkim/GIT/AI_agents"
SCRIPTS_DIR="$REPO_ROOT/skills/custom/appflowy-integration/scripts"
ENV_FILE="/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env"

export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
cd "$SCRIPTS_DIR"
python3 sync_docs.py && python3 sync_tasks.py
EOF
chmod +x /Users/sunginkim/bin/appflowy-sync.sh

# 2. Set up post-commit hook
cat > "$REPO_ROOT/.git/hooks/post-commit" <<'EOF'
#!/bin/bash
(/Users/sunginkim/bin/appflowy-sync.sh > /tmp/appflowy-sync.log 2>&1 &)
EOF
chmod +x "$REPO_ROOT/.git/hooks/post-commit"

# 3. Set up cron (hourly)
(crontab -l 2>/dev/null; echo "0 * * * * /Users/sunginkim/bin/appflowy-sync.sh >> /tmp/appflowy-sync-cron.log 2>&1") | crontab -

echo "AppFlowy sync automation setup complete"
```

## Related Documentation

- `sync-documentation.md` - Documentation sync details
- `sync-tasks.md` - Task sync details
- `references/api-reference.md` - API documentation
- `workflows/troubleshooting.md` - General troubleshooting
