---
description: Pull and sync latest AI_agents updates from submodule to parent project(s)
argument-hint: [project-path] [--recursive | -r]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Pull AI_agents Submodule Updates

This command updates your project(s) with the latest AI_agents system improvements from the submodule.

**Usage:**
```bash
# Update current directory project
/pull-ai-agents-submodule

# Update specific sub-project in mono-repo
/pull-ai-agents-submodule ./projects/trading-signal-ai

# Update project with absolute path
/pull-ai-agents-submodule /Users/you/projects/my-app

# RECURSIVE: Update all projects under a directory
/pull-ai-agents-submodule --recursive
/pull-ai-agents-submodule ./projects --recursive
/pull-ai-agents-submodule -r  # short form
```

**Prerequisites:**
- AI_agents repository installed as submodule at `{project-path}/.ai-agents/library/`
- Project has `.claude/commands/`, `.claude/agents/`, and `prompts/` directories

## Step 0: Parse Arguments and Detect Mode

```bash
# Parse arguments
recursive_mode=false
project_path="."

# Check for recursive flag
for arg in "$@"; do
  if [[ "$arg" == "--recursive" ]] || [[ "$arg" == "-r" ]]; then
    recursive_mode=true
  elif [[ "$arg" != -* ]]; then
    project_path="$arg"
  fi
done

# Resolve to absolute path
project_path=$(cd "$project_path" && pwd)

# Verify project path exists
if [ ! -d "$project_path" ]; then
  echo "❌ Error: Project path does not exist: $project_path"
  exit 1
fi

# Determine mode
if [ "$recursive_mode" = true ]; then
  echo "🔍 Recursive mode: Scanning for all projects under $project_path"
  echo ""
else
  echo "📁 Single mode: Target project: $project_path"
  echo ""
fi
```

## Step 0.1: Recursive Mode - Scan for Projects

**Only if `recursive_mode=true`:**

```bash
if [ "$recursive_mode" = true ]; then
  # Find all directories containing .ai-agents/
  echo "Scanning for projects with .ai-agents/ directories..."

  # Use find to locate all .ai-agents directories (excluding nested ones)
  found_projects=()
  while IFS= read -r ai_agents_path; do
    # Get parent directory of .ai-agents
    project_dir=$(dirname "$ai_agents_path")

    # Skip if this is the AI_agents repo itself (has .ai-agents at root with specific structure)
    if [ -d "$ai_agents_path/state" ] && [ -d "$ai_agents_path/handoffs" ]; then
      # This looks like the AI_agents repo structure, check for submodule
      if [ -d "$ai_agents_path/library" ]; then
        found_projects+=("$project_dir")
      elif [ -d "$project_dir/.claude/commands" ]; then
        # Has .claude/commands but no library - still a valid project to update
        found_projects+=("$project_dir")
      fi
    else
      # Simple .ai-agents directory - include if it has .claude/commands
      if [ -d "$project_dir/.claude/commands" ]; then
        found_projects+=("$project_dir")
      fi
    fi
  done < <(find "$project_path" -type d -name ".ai-agents" -not -path "*/.ai-agents/*" 2>/dev/null)

  # Remove duplicates
  found_projects=($(printf '%s\n' "${found_projects[@]}" | sort -u))

  # Count projects found
  project_count=${#found_projects[@]}

  if [ $project_count -eq 0 ]; then
    echo "❌ No projects found with .ai-agents/ directories under $project_path"
    echo ""
    echo "Looking for directories with .ai-agents/ and .claude/commands/"
    exit 1
  fi

  # Show found projects
  echo ""
  echo "Found $project_count project(s) with .ai-agents/ directories:"
  echo ""
  for i in "${!found_projects[@]}"; do
    proj="${found_projects[$i]}"
    rel_path=$(realpath --relative-to="$project_path" "$proj" 2>/dev/null || echo "$proj")

    # Get current status for this project
    if [ -d "$proj/.ai-agents/library/.git" ] || [ -f "$proj/.ai-agents/library/.git" ]; then
      # Has submodule
      current_commit=$(cd "$proj/.ai-agents/library" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
      current_branch=$(cd "$proj/.ai-agents/library" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
      echo "  $((i+1)). $rel_path"
      echo "     Submodule: $current_branch @ $current_commit"
    elif [ -d "$proj/.claude/commands" ]; then
      # Has .claude/commands but no submodule - count commands
      cmd_count=$(ls "$proj/.claude/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
      agent_count=$(ls "$proj/.claude/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
      echo "  $((i+1)). $rel_path"
      echo "     Commands: $cmd_count, Agents: $agent_count (no submodule)"
    else
      echo "  $((i+1)). $rel_path"
      echo "     ⚠️  No .claude/commands/ found"
    fi
  done

  echo ""
  echo "─────────────────────────────────────────"
  echo ""
fi
```

## Step 0.2: Recursive Mode - Confirm Batch Update

**Only if `recursive_mode=true`:**

```markdown
## Batch Update Summary

**Mode:** Recursive
**Scan root:** {project_path}
**Projects found:** {project_count}

**What will happen:**

For each project found:
1. Fetch latest updates from AI_agents origin/master
2. Show available commits and file changes
3. Pull updates to submodule
4. Sync changed files to parent project
5. Generate update report

**Processing order:**
{List each project path}

**Safety:**
- Each project updated independently
- Conflicts reported per project
- Can skip individual projects
- Update reports saved per project

---

**Proceed with batch update?**

Options:
- **Yes** - Update all {project_count} projects
- **Select** - Choose which projects to update
- **Cancel** - Exit without updating
```

Wait for user response.

### If user chooses "Select":

```markdown
Select projects to update (comma-separated numbers):

{numbered list of projects}

Example: 1,3,5 (to update projects 1, 3, and 5)
```

Parse user selection and filter `found_projects` array.

### If user chooses "Yes":

Proceed with all projects.

### If user chooses "Cancel":

Exit.

## Step 0.3: Recursive Mode - Loop Through Projects

**Only if `recursive_mode=true`:**

```bash
# Track overall results
declare -A project_results
total_updated=0
total_skipped=0
total_failed=0

# Loop through each project
for i in "${!found_projects[@]}"; do
  current_project="${found_projects[$i]}"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📦 Project $((i+1))/$project_count"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Path: $current_project"
  echo ""

  # Set project_path for the single-project workflow
  project_path="$current_project"

  # Now proceed with Steps 1-10 for this project
  # (The rest of the workflow runs as normal for each project)

  # Track result
  # (Set in Step 10 based on success/failure)
done

# After all projects processed, show summary (see Step 10.1)
```

**Note:** For recursive mode, the single-project workflow (Steps 1-10) runs for each project in the loop. After all projects are processed, jump to Step 10.1 for the batch summary.

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

# Determine source directory (submodule or current repo)
if [ -d "$project_path/.ai-agents/library/.claude/commands" ]; then
  source_commands="$project_path/.ai-agents/library/.claude/commands"
else
  # No submodule - use current AI_agents repo as source
  source_commands="$(pwd)/.claude/commands"
fi

# Sync ALL commands from source (both new and updated)
echo ""
echo "📂 Syncing commands from: $source_commands"
echo ""

new_count=0
updated_count=0
skipped_count=0
conflict_count=0

for source_file in "$source_commands"/*.md; do
  [ -f "$source_file" ] || continue  # Skip if no .md files

  cmd_file=$(basename "$source_file")
  dest="$project_path/.claude/commands/$cmd_file"

  # Check if file exists locally
  if [ -f "$dest" ]; then
    # Compare files
    if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
      echo "  ✓ $cmd_file - already up to date"
      ((skipped_count++))
    else
      # Files differ - report conflict
      echo "  ⚠️  $cmd_file - local version differs (conflict)"
      ((conflict_count++))
      # Store conflict for later resolution
    fi
  else
    # New file - copy it
    cp "$source_file" "$dest"
    echo "  ✓ $cmd_file - created (new)"
    ((new_count++))
  fi
done

echo ""
echo "Commands sync summary:"
echo "  - New commands created: $new_count"
echo "  - Already up to date: $skipped_count"
echo "  - Conflicts (need review): $conflict_count"
```

### Agents Sync

```bash
# Create agents directory if needed
mkdir -p "$project_path/.claude/agents"

# Determine source directory (submodule or current repo)
if [ -d "$project_path/.ai-agents/library/.claude/agents" ]; then
  source_agents="$project_path/.ai-agents/library/.claude/agents"
else
  # No submodule - use current AI_agents repo as source
  source_agents="$(pwd)/.claude/agents"
fi

# Sync ALL agents from source (both new and updated)
echo ""
echo "📂 Syncing agents from: $source_agents"
echo ""

new_agent_count=0
skipped_agent_count=0
conflict_agent_count=0
project_specific_count=0

for source_file in "$source_agents"/*.md; do
  [ -f "$source_file" ] || continue  # Skip if no .md files

  agent_file=$(basename "$source_file")
  dest="$project_path/.claude/agents/$agent_file"

  # Check if this is a project-specific agent (custom managers, etc.)
  # Skip syncing if local version exists and contains project-specific content
  if [ -f "$dest" ]; then
    # Check if local file has project-specific markers
    if grep -q "project-specific\|custom\|local" "$dest" 2>/dev/null; then
      echo "  ⏭️  $agent_file - skipped (project-specific agent)"
      ((project_specific_count++))
      continue
    fi

    # Compare files
    if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
      echo "  ✓ $agent_file - already up to date"
      ((skipped_agent_count++))
    else
      # Files differ - report conflict
      echo "  ⚠️  $agent_file - local version differs (conflict)"
      ((conflict_agent_count++))
    fi
  else
    # New file - copy it
    cp "$source_file" "$dest"
    echo "  ✓ $agent_file - created (new)"
    ((new_agent_count++))
  fi
done

echo ""
echo "Agents sync summary:"
echo "  - New agents created: $new_agent_count"
echo "  - Already up to date: $skipped_agent_count"
echo "  - Project-specific (skipped): $project_specific_count"
echo "  - Conflicts (need review): $conflict_agent_count"
```

### Prompts Sync

```bash
# Create prompts directory if needed
mkdir -p "$project_path/prompts"
mkdir -p "$project_path/prompts/roles"

# Determine source directory (submodule or current repo)
if [ -d "$project_path/.ai-agents/library/prompts" ]; then
  source_prompts="$project_path/.ai-agents/library/prompts"
else
  # No submodule - use current AI_agents repo as source
  source_prompts="$(pwd)/prompts"
fi

# Sync ALL prompts from source (both new and updated)
echo ""
echo "📂 Syncing prompts from: $source_prompts"
echo ""

new_prompt_count=0
skipped_prompt_count=0
conflict_prompt_count=0

# Sync root-level prompts
for source_file in "$source_prompts"/*.md; do
  [ -f "$source_file" ] || continue

  prompt_file=$(basename "$source_file")
  dest="$project_path/prompts/$prompt_file"

  if [ -f "$dest" ]; then
    if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
      echo "  ✓ $prompt_file - already up to date"
      ((skipped_prompt_count++))
    else
      echo "  ⚠️  $prompt_file - local version differs (conflict)"
      ((conflict_prompt_count++))
    fi
  else
    cp "$source_file" "$dest"
    echo "  ✓ $prompt_file - created (new)"
    ((new_prompt_count++))
  fi
done

# Sync prompts/roles/ directory
if [ -d "$source_prompts/roles" ]; then
  for source_file in "$source_prompts/roles"/*.md; do
    [ -f "$source_file" ] || continue

    prompt_file=$(basename "$source_file")
    dest="$project_path/prompts/roles/$prompt_file"

    if [ -f "$dest" ]; then
      if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
        echo "  ✓ roles/$prompt_file - already up to date"
        ((skipped_prompt_count++))
      else
        echo "  ⚠️  roles/$prompt_file - local version differs (conflict)"
        ((conflict_prompt_count++))
      fi
    else
      cp "$source_file" "$dest"
      echo "  ✓ roles/$prompt_file - created (new)"
      ((new_prompt_count++))
    fi
  done
fi

echo ""
echo "Prompts sync summary:"
echo "  - New prompts created: $new_prompt_count"
echo "  - Already up to date: $skipped_prompt_count"
echo "  - Conflicts (need review): $conflict_prompt_count"
```

### Scripts Sync

```bash
# Create scripts directory if needed
mkdir -p "$project_path/scripts"

# Determine source directory (submodule or current repo)
if [ -d "$project_path/.ai-agents/library/scripts" ]; then
  source_scripts="$project_path/.ai-agents/library/scripts"
else
  # No submodule - use current AI_agents repo as source
  source_scripts="$(pwd)/scripts"
fi

# Sync scripts (be more careful - these can have local modifications)
echo ""
echo "📂 Syncing scripts from: $source_scripts"
echo ""

new_script_count=0
skipped_script_count=0
conflict_script_count=0

# Sync .py and .sh files
for ext in py sh; do
  for source_file in "$source_scripts"/*."$ext"; do
    [ -f "$source_file" ] || continue

    script_file=$(basename "$source_file")
    dest="$project_path/scripts/$script_file"

    if [ -f "$dest" ]; then
      if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
        echo "  ✓ $script_file - already up to date"
        ((skipped_script_count++))
      else
        echo "  ⚠️  $script_file - local version differs (conflict)"
        ((conflict_script_count++))
      fi
    else
      cp "$source_file" "$dest"
      echo "  ✓ $script_file - created (new)"
      ((new_script_count++))
    fi
  done
done

echo ""
echo "Scripts sync summary:"
echo "  - New scripts created: $new_script_count"
echo "  - Already up to date: $skipped_script_count"
echo "  - Conflicts (need review): $conflict_script_count"
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

## Step 10.1: Batch Summary Report (Recursive Mode Only)

**Only if `recursive_mode=true`:**

After all projects have been processed, generate a comprehensive batch summary:

```markdown
# Batch Update Summary

**Mode:** Recursive
**Scan root:** {scan_root_path}
**Date:** {ISO-8601 timestamp}
**Projects processed:** {total_projects}

## Results Overview

| Status | Count | Projects |
|--------|-------|----------|
| ✅ Updated | {total_updated} | {list of updated project names} |
| ⏭️ Skipped | {total_skipped} | {list of skipped project names} |
| ❌ Failed | {total_failed} | {list of failed project names} |

## Per-Project Details

### Updated Projects ({total_updated})

{For each updated project:}

#### {project_name}
- **Path:** {relative_path}
- **Submodule:** {old_commit} → {new_commit}
- **Files synced:**
  - Commands: {count} files
  - Agents: {count} files
  - Prompts: {count} files
  - Scripts: {count} files
- **Conflicts:** {count}
- **Report:** `.ai-agents/update-reports/update-{timestamp}.md`

---

### Skipped Projects ({total_skipped})

{For each skipped project:}

#### {project_name}
- **Path:** {relative_path}
- **Reason:** {Already up to date | User skipped | Other}
- **Current commit:** {commit}

---

### Failed Projects ({total_failed})

{For each failed project:}

#### {project_name}
- **Path:** {relative_path}
- **Error:** {error_message}
- **Action needed:** {troubleshooting steps}

---

## Overall Statistics

- **Total commits pulled:** {sum of all commit counts}
- **Total files synced:** {sum of all synced files}
- **Total conflicts:** {sum of all conflicts}
- **Execution time:** {duration}

## Next Steps

1. **Review individual reports:**
   - Each project has detailed report in `.ai-agents/update-reports/`
   - Check for conflicts and breaking changes

2. **Test projects:**
   - Run tests for each updated project
   - Verify new commands and agents work correctly

3. **Commit changes:**
   - Review and commit changes in each project repository
   - Consider using provided commit messages

4. **Resolve conflicts:**
   {If any conflicts detected:}
   - {List projects with conflicts}
   - Manual review required

## Rollback

If you need to revert updates for a specific project:

```bash
cd {project_path}/.ai-agents/library
git checkout {old_commit}
cd ../..
/pull-ai-agents-submodule {project_path}
```

---

**Batch update complete!** ✓

All projects under `{scan_root_path}` have been processed.
```

Save this batch summary report:

```bash
# Save batch summary in scan root
batch_report_file="$scan_root/.ai-agents/batch-update-$(date +%Y%m%d-%H%M%S).md"
mkdir -p "$(dirname "$batch_report_file")"
echo "{batch_summary_content}" > "$batch_report_file"

echo ""
echo "📊 Batch summary saved to:"
echo "   $batch_report_file"
echo ""
```

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

## Recursive Mode - Update All Projects

**NEW:** Update all projects under a directory tree automatically.

```bash
# Update all projects in current directory tree
/pull-ai-agents-submodule --recursive

# Update all projects under ./projects/
/pull-ai-agents-submodule ./projects --recursive

# Short form
/pull-ai-agents-submodule -r
/pull-ai-agents-submodule ./apps -r
```

### Example Workflow

```
my-mono-repo/
├── projects/
│   ├── trading-signal-ai/
│   │   └── .ai-agents/library/  ← Will be updated
│   ├── portfolio-tracker/
│   │   └── .ai-agents/library/  ← Will be updated
│   └── market-analyzer/
│       └── .ai-agents/library/  ← Will be updated
└── legacy/
    └── old-app/
        └── .ai-agents/library/  ← Will be updated
```

Run from mono-repo root:
```bash
cd /path/to/my-mono-repo
/pull-ai-agents-submodule --recursive
```

Output:
```
🔍 Recursive mode: Scanning for all projects under /path/to/my-mono-repo

Scanning for projects with AI_agents submodules...

Found 4 project(s) with AI_agents submodules:

  1. projects/trading-signal-ai
     Current: master @ a1b2c3d
  2. projects/portfolio-tracker
     Current: master @ a1b2c3d
  3. projects/market-analyzer
     Current: master @ e4f5g6h (behind)
  4. legacy/old-app
     Current: master @ x7y8z9w (behind)

─────────────────────────────────────────

Proceed with batch update?
- Yes
- Select (choose specific projects)
- Cancel
```

If you choose "Select":
```
Select projects to update (comma-separated numbers):
> 1,2,3

Updating projects: trading-signal-ai, portfolio-tracker, market-analyzer
Skipping: old-app
```

Each project gets updated independently with its own report.

## Mono-Repo Workflow Comparison

### Before (Manual):
```bash
# Update each project one at a time
/pull-ai-agents-submodule ./projects/trading-signal-ai
# ... review, commit ...
/pull-ai-agents-submodule ./projects/portfolio-tracker
# ... review, commit ...
/pull-ai-agents-submodule ./projects/market-analyzer
# ... review, commit ...
```

### After (Recursive):
```bash
# Update all at once
/pull-ai-agents-submodule ./projects --recursive
# ... batch summary shows all results ...
# ... review each project's report ...
# ... commit each project as needed ...
```

## Mono-Repo with Selective Updates

Only update projects under `./apps/`:

```bash
# Mono-repo structure
my-company/
├── apps/           ← Update these
│   ├── web/
│   ├── mobile/
│   └── api/
└── internal/       ← Skip these
    ├── admin/
    └── tools/

# Command
cd /path/to/my-company
/pull-ai-agents-submodule ./apps --recursive
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
✅ **Recursive mode:** Batch update multiple projects with selective control
✅ **Independent updates:** Each project processed independently (no cascade failures)
✅ **Batch summary:** Comprehensive report across all projects

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

## "No projects found" (Recursive Mode)

Recursive mode can't find any projects with .ai-agents/ directories:

```bash
# Check if .ai-agents directories exist
find . -type d -name ".ai-agents" -not -path "*/.ai-agents/*"

# Check for projects with .claude/commands/
find . -type d -name ".claude" -exec test -d {}/commands \; -print

# Initialize AI_agents in a project
cd ./projects/my-app
mkdir -p .ai-agents .claude/commands .claude/agents prompts
# Optionally add as submodule:
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library
```

## "Too many projects found" (Recursive Mode)

Recursive mode found more projects than expected:

```bash
# Use more specific path
/pull-ai-agents-submodule ./projects --recursive  # Instead of root

# Or use "Select" mode to choose specific projects
/pull-ai-agents-submodule --recursive
# Then choose: Select → 1,3,5
```

## "One project failed, stopped all updates" (Recursive Mode)

**This doesn't happen!** Each project is updated independently. If one fails, others continue.

Check the batch summary report for:
- Which projects succeeded
- Which projects failed
- Error details for failed projects

## "Want different update strategy per project" (Recursive Mode)

For fine-grained control, update projects individually:

```bash
# Update high-priority projects with careful review
/pull-ai-agents-submodule ./projects/production-app
# ... review carefully, commit ...

# Batch update low-priority projects
/pull-ai-agents-submodule ./projects/experiments --recursive
```

---

**Implementation Note:** This command automates the sync process while maintaining safety and giving users full visibility into what's changing in their AI agent system. Recursive mode extends this to mono-repos with multiple projects.
