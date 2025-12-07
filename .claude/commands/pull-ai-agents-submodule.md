---
description: Pull and sync latest AI_agents updates from submodule to parent project
argument-hint: [project-path (optional, defaults to current directory)]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Pull AI_agents Submodule Updates

This command updates your project with the latest AI_agents system improvements from the submodule.

**Usage:**
```bash
# Update current directory project
/pull-ai-agents-submodule

# Update specific sub-project in mono-repo
/pull-ai-agents-submodule ./projects/trading-signal-ai

# Update project with absolute path
/pull-ai-agents-submodule /Users/you/projects/my-app
```

**Prerequisites:**
- AI_agents repository installed as submodule at `{project-path}/.ai-agents/library/`
- Project has `.claude/commands/`, `.claude/agents/`, and `prompts/` directories

## Step 0: Parse Arguments and Set Project Path

```bash
# Parse project path argument (optional)
# Default to current directory if not provided
project_path="${1:-.}"

# Resolve to absolute path
project_path=$(cd "$project_path" && pwd)

echo "Target project: $project_path"
echo ""

# Verify project path exists
if [ ! -d "$project_path" ]; then
  echo "❌ Error: Project path does not exist: $project_path"
  exit 1
fi
```

## Step 1: Validate Submodule Setup

Check that the submodule exists in the target project:

```bash
# Verify submodule exists in target project
if [ ! -d "$project_path/.ai-agents/library" ]; then
  echo "❌ Error: AI_agents submodule not found at $project_path/.ai-agents/library/"
  echo ""
  echo "To set up the submodule:"
  echo "  cd $project_path"
  echo "  git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library"
  echo "  git submodule update --init --recursive"
  exit 1
fi

echo "✓ Submodule found at $project_path/.ai-agents/library/"

# Check if it's actually a git submodule
if [ ! -f "$project_path/.ai-agents/library/.git" ] && [ ! -d "$project_path/.ai-agents/library/.git" ]; then
  echo "⚠️  Warning: .ai-agents/library/ exists but is not a git submodule"
fi

# Get current submodule commit
cd "$project_path/.ai-agents/library"
current_commit=$(git rev-parse HEAD)
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current: $current_branch @ ${current_commit:0:7}"
cd - > /dev/null
```

## Step 2: Fetch and Show Available Updates

Fetch latest changes from remote and show what's new:

```bash
cd "$project_path/.ai-agents/library"

# Fetch latest from remote
echo ""
echo "Fetching latest updates from origin/master..."
git fetch origin master

# Get remote commit
remote_commit=$(git rev-parse origin/master)

# Check if updates are available
if [ "$current_commit" = "$remote_commit" ]; then
  echo ""
  echo "✓ Already up to date with origin/master"
  cd - > /dev/null
  exit 0
fi

# Show commits between current and remote
echo ""
echo "📋 New commits available:"
echo ""
git log --oneline --graph --decorate HEAD..origin/master

# Show file changes summary
echo ""
echo "📊 Files changed:"
git diff --stat HEAD..origin/master

cd - > /dev/null
```

## Step 3: Analyze Changes

Categorize what changed in the submodule:

```bash
cd "$project_path/.ai-agents/library"

# Detect changes by category
echo ""
echo "🔍 Analyzing changes..."
echo ""

# Commands changed
commands_changed=$(git diff --name-only HEAD..origin/master | grep '^\.claude/commands/' | wc -l | tr -d ' ')
if [ "$commands_changed" -gt 0 ]; then
  echo "  Commands: $commands_changed files"
  git diff --name-only HEAD..origin/master | grep '^\.claude/commands/' | sed 's/^/    - /'
fi

# Agents changed
agents_changed=$(git diff --name-only HEAD..origin/master | grep '^\.claude/agents/' | wc -l | tr -d ' ')
if [ "$agents_changed" -gt 0 ]; then
  echo "  Agents: $agents_changed files"
  git diff --name-only HEAD..origin/master | grep '^\.claude/agents/' | sed 's/^/    - /'
fi

# Prompts changed
prompts_changed=$(git diff --name-only HEAD..origin/master | grep '^prompts/' | wc -l | tr -d ' ')
if [ "$prompts_changed" -gt 0 ]; then
  echo "  Prompts: $prompts_changed files"
  git diff --name-only HEAD..origin/master | grep '^prompts/' | sed 's/^/    - /'
fi

# Scripts changed
scripts_changed=$(git diff --name-only HEAD..origin/master | grep '^scripts/' | wc -l | tr -d ' ')
if [ "$scripts_changed" -gt 0 ]; then
  echo "  Scripts: $scripts_changed files"
  git diff --name-only HEAD..origin/master | grep '^scripts/' | sed 's/^/    - /'
fi

# Docs changed
docs_changed=$(git diff --name-only HEAD..origin/master | grep '^docs/' | wc -l | tr -d ' ')
if [ "$docs_changed" -gt 0 ]; then
  echo "  Documentation: $docs_changed files"
fi

cd - > /dev/null
```

## Step 4: User Confirmation

Ask user if they want to proceed with the update:

```markdown
## Update Summary

**Available Updates:**
- Commands: {commands_changed} files
- Agents: {agents_changed} files
- Prompts: {prompts_changed} files
- Scripts: {scripts_changed} files
- Documentation: {docs_changed} files

**What will happen:**

1. **Submodule Update:** Pull latest master branch
2. **Analysis:** Review each changed file in detail
3. **Sync Commands:** Copy new/updated commands to `.claude/commands/`
4. **Sync Agents:** Copy new/updated agents to `.claude/agents/`
5. **Sync Prompts:** Copy new/updated prompts to `prompts/`
6. **Report:** Show what was updated and any conflicts

**Safety:**
- Your local customizations will be preserved
- Conflicts will be reported (not auto-overwritten)
- Backup recommendation: Commit your current work first

---

**Proceed with update?**

Options:
- **Yes** - Pull updates and sync to parent project
- **Show details** - Read detailed change analysis first
- **Cancel** - Keep current version
```

Wait for user response. If user says "Show details", proceed to detailed analysis. If "Yes", proceed to Step 5. If "Cancel", exit.

## Step 5: Pull Submodule Updates

Pull the latest changes:

```bash
cd "$project_path/.ai-agents/library"

echo ""
echo "📥 Pulling latest updates..."
git pull origin master

new_commit=$(git rev-parse HEAD)
echo "✓ Updated to ${new_commit:0:7}"

cd - > /dev/null
```

## Step 6: Detailed Change Analysis

For each changed file, provide detailed analysis:

**Read each changed file and analyze:**

```bash
# Get list of changed files
cd "$project_path/.ai-agents/library"
changed_files=$(git diff --name-only HEAD~1..HEAD)
cd - > /dev/null
```

For each file in `changed_files` (relative to `$project_path`):

### Commands (`.claude/commands/*.md`)

```markdown
**File:** {filename}
**Category:** Command
**Status:** {New | Updated | Deleted}

**What changed:**
{Read the file, compare with previous version if it exists in parent project}

**Impact on your project:**
- This command {does what}
- {If new:} Adds new capability: {description}
- {If updated:} Changes behavior: {description}
- {If deleted:} This command is deprecated

**Recommendation:**
- {Sync | Skip | Review manually}
```

### Agents (`.claude/agents/*.md`)

```markdown
**File:** {filename}
**Category:** Agent
**Status:** {New | Updated | Deleted}

**Agent type:** {Manager | Worker | Specialist}

**What changed:**
{Analyze agent prompt changes}
- Role definition: {changes}
- Workflow updates: {changes}
- New capabilities: {list}

**Impact on your project:**
- {How this agent is used}
- {What workflows it affects}

**Recommendation:**
- {Sync | Skip | Review manually}
```

### Prompts (`prompts/*.md`)

```markdown
**File:** {filename}
**Category:** Prompt Template
**Status:** {New | Updated | Deleted}

**Purpose:** {What this prompt does}

**What changed:**
{Analyze prompt changes}
- Instructions updated: {summary}
- New sections: {list}
- Removed sections: {list}

**Impact on your project:**
- {Workflows that use this prompt}
- {Breaking changes if any}

**Recommendation:**
- {Sync | Skip | Review manually}
```

### Scripts (`scripts/*.py`, `scripts/*.sh`)

```markdown
**File:** {filename}
**Category:** Script
**Status:** {New | Updated | Deleted}

**Purpose:** {What this script does}

**What changed:**
{Analyze script changes}
- New features: {list}
- Bug fixes: {list}
- Breaking changes: {list}

**Dependencies:**
{Check if script has new dependencies}

**Impact on your project:**
- {How/when this script is used}
- {Required setup if any}

**Recommendation:**
- {Sync | Skip | Review manually}
```

## Step 7: Sync Files to Parent Project

For each file recommended to sync:

### Commands Sync

```bash
# Create commands directory if needed
mkdir -p "$project_path/.claude/commands"

# For each changed command file
for cmd_file in {changed_command_files}; do
  source="$project_path/.ai-agents/library/.claude/commands/$cmd_file"
  dest="$project_path/.claude/commands/$cmd_file"

  # Check if file exists locally
  if [ -f "$dest" ]; then
    # Compare files
    if diff -q "$source" "$dest" > /dev/null; then
      echo "  ✓ $cmd_file - already up to date"
    else
      # Files differ - check if local has custom modifications
      echo "  ⚠️  $cmd_file - local version differs"
      echo "     Show diff? (y/n)"
      # If yes, show diff and ask to overwrite/keep/merge
    fi
  else
    # New file - copy it
    cp "$source" "$dest"
    echo "  ✓ $cmd_file - copied (new)"
  fi
done
```

### Agents Sync

```bash
# Create agents directory if needed
mkdir -p "$project_path/.claude/agents"

# For each changed agent file
for agent_file in {changed_agent_files}; do
  source="$project_path/.ai-agents/library/.claude/agents/$agent_file"
  dest="$project_path/.claude/agents/$agent_file"

  # Check if this is a project-specific agent (e.g., appflowy-manager.md)
  # Skip syncing project-specific agents
  if [[ "$agent_file" == *"manager.md" ]] && [ -f "$dest" ]; then
    echo "  ⏭️  $agent_file - skipped (project-specific agent)"
    continue
  fi

  # Sync generic/template agents
  if [ -f "$dest" ]; then
    if ! diff -q "$source" "$dest" > /dev/null; then
      echo "  ⚠️  $agent_file - local version differs"
      # Show diff and ask
    fi
  else
    cp "$source" "$dest"
    echo "  ✓ $agent_file - copied (new)"
  fi
done
```

### Prompts Sync

```bash
# Create prompts directory if needed
mkdir -p "$project_path/prompts"

# Sync prompts with same logic
# Handle prompts/roles/, prompts/*.md
```

### Scripts Sync

```bash
# Create scripts directory if needed
mkdir -p "$project_path/scripts"

# For scripts, be more careful
# Ask user confirmation for each script since they may have local modifications
```

## Step 8: Update State File Schemas

Check if state file schemas changed:

```bash
# Read state file documentation from submodule
Read $project_path/.ai-agents/library/docs/reference/CHEAT_SHEET/01-state-files.md

# Compare with local state files at project path
# If schemas changed, show migration guide
```

If state file schemas updated:

```markdown
## State File Schema Updates Detected

**Files affected:**
- team-communication.json: {changes}
- session-progress.json: {changes}
- feature-tracking.json: {changes}

**Migration needed:**
{Step-by-step instructions to update local state files}

**Automatic migration available:** {Yes/No}

Shall I update your state files? (Backup will be created)
```

## Step 9: Generate Update Report

Create comprehensive report:

```markdown
# AI_agents Submodule Update Report

**Project:** {project_path}
**Date:** {ISO-8601 timestamp}
**Updated from:** {old_commit} → {new_commit}

## Files Synced

### Commands ({count})
- ✓ {filename} - {new/updated/deleted}
- ✓ {filename} - {new/updated/deleted}

### Agents ({count})
- ✓ {filename} - {new/updated/deleted}
- ⏭️ {filename} - skipped (project-specific)

### Prompts ({count})
- ✓ {filename} - {new/updated/deleted}

### Scripts ({count})
- ✓ {filename} - {new/updated/deleted}

## Conflicts Detected ({count})

{If any conflicts:}
- ⚠️ {filename}
  - Location: {path}
  - Issue: {local modifications conflict with update}
  - Action needed: {manual review/merge}

## Breaking Changes

{If any breaking changes detected:}
- {description of breaking change}
- Migration steps: {steps}

## New Features Added

{Summary of new capabilities from commits}

## Recommendations

### Next Steps
1. {Recommended actions}
2. {Testing suggestions}
3. {Documentation to review}

### Rollback (if needed)
If you need to revert this update:
\`\`\`bash
cd .ai-agents/library
git checkout {old_commit}
cd ../..
# Then re-run this command to sync files back
\`\`\`

---

**Update complete!** ✓

Your project is now synced with AI_agents master @ {new_commit:0:7}
```

## Step 10: Save Report and Commit

Save the update report and commit changes:

```bash
# Save report in project directory
mkdir -p "$project_path/.ai-agents/update-reports"
echo "{report_content}" > "$project_path/.ai-agents/update-reports/update-$(date +%Y%m%d-%H%M%S).md"

# Show git status for project
cd "$project_path"
git status
cd - > /dev/null

# Suggest commit message
echo ""
echo "Suggested commit message:"
echo ""
echo "chore: sync AI_agents submodule updates"
echo ""
echo "Updated AI_agents library from ${old_commit:0:7} to ${new_commit:0:7}"
echo ""
echo "Changes synced:"
echo "- Commands: $commands_changed files"
echo "- Agents: $agents_changed files"
echo "- Prompts: $prompts_changed files"
echo "- Scripts: $scripts_changed files"
echo ""
echo "See .ai-agents/update-reports/update-{timestamp}.md for details"
```

Ask user if they want to commit now or review first.

---

# Usage Examples

## Basic Update (Current Directory)

```bash
/pull-ai-agents-submodule
```

Updates the project in the current directory.

## Update Specific Sub-Project

```bash
# Relative path
/pull-ai-agents-submodule ./projects/trading-signal-ai

# Absolute path
/pull-ai-agents-submodule /Users/you/work/my-mono-repo/apps/backend
```

## Mono-Repo Workflow

When working in a mono-repo with multiple projects:

```
my-mono-repo/
├── projects/
│   ├── trading-signal-ai/
│   │   ├── .ai-agents/library/  ← Submodule
│   │   ├── .claude/commands/
│   │   └── prompts/
│   ├── portfolio-tracker/
│   │   ├── .ai-agents/library/  ← Submodule
│   │   ├── .claude/commands/
│   │   └── prompts/
│   └── market-analyzer/
│       ├── .ai-agents/library/  ← Submodule
│       ├── .claude/commands/
│       └── prompts/
```

Launch Claude Code in sub-project:
```bash
cd /path/to/my-mono-repo/projects/trading-signal-ai
# In Claude Code:
/pull-ai-agents-submodule
```

Or from mono-repo root:
```bash
cd /path/to/my-mono-repo
# In Claude Code:
/pull-ai-agents-submodule ./projects/trading-signal-ai
```

## After Running Command

You should review:
1. Update report in `.ai-agents/update-reports/`
2. Any conflicts flagged during sync
3. Breaking changes section
4. New features documentation

Then test your project to ensure everything works with the updates.

---

# Safety Features

✅ **Non-destructive:** Shows changes before applying
✅ **Conflict detection:** Warns about local modifications
✅ **Selective sync:** Skip project-specific files
✅ **Detailed analysis:** Understand each change
✅ **Rollback support:** Can revert to previous version
✅ **Update reports:** Full audit trail

---

# Troubleshooting

## "Submodule not found"

Initialize the submodule in the target project:
```bash
cd /path/to/project  # or ./projects/trading-signal-ai
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library
git submodule update --init --recursive
```

## "Merge conflicts"

The command will flag conflicts but not auto-merge. Review manually:
```bash
# Compare versions (adjust paths for your project)
diff ./projects/trading-signal-ai/.claude/commands/example.md \
     ./projects/trading-signal-ai/.ai-agents/library/.claude/commands/example.md

# Choose which version to keep or merge manually
```

## "Wrong project updated"

Make sure to specify the correct path:
```bash
# Bad - updates wrong project
cd /mono-repo
/pull-ai-agents-submodule  # Updates /mono-repo, not the sub-project!

# Good - specify sub-project
cd /mono-repo
/pull-ai-agents-submodule ./projects/trading-signal-ai

# Also Good - run from sub-project
cd /mono-repo/projects/trading-signal-ai
/pull-ai-agents-submodule
```

## "Want to skip certain files"

Edit the sync logic in Step 7 to add files to skip list.

---

**Implementation Note:** This command automates the sync process while maintaining safety and giving users full visibility into what's changing in their AI agent system.
