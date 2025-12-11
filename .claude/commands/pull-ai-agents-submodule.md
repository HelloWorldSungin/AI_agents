---
description: Pull and sync latest AI_agents updates from submodule to parent project(s)
argument-hint: [project-path] [--recursive | -r]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Pull AI_agents Submodule Updates

Updates your project(s) with latest AI_agents improvements from the submodule.

**Usage:**
```bash
/pull-ai-agents-submodule                     # Update current directory
/pull-ai-agents-submodule ./projects/my-app   # Update specific project
/pull-ai-agents-submodule --recursive         # Update all projects in tree
/pull-ai-agents-submodule ./projects -r       # Update all under ./projects/
```

**Prerequisites:**
- AI_agents installed as submodule at `{project-path}/.ai-agents/library/`
- Project has `.claude/commands/`, `.claude/agents/`, and `prompts/` directories

---

## Step 0: Parse Arguments and Source Utilities

```bash
# Parse arguments
recursive_mode=false
project_path="."

for arg in "$@"; do
  if [[ "$arg" == "--recursive" ]] || [[ "$arg" == "-r" ]]; then
    recursive_mode=true
  elif [[ "$arg" != -* ]]; then
    project_path="$arg"
  fi
done

project_path=$(cd "$project_path" 2>/dev/null && pwd) || { echo "Error: Invalid path"; exit 1; }

# Source shared utilities
for lib_path in "$project_path/.ai-agents/library/handoff-functions.sh" \
                ".ai-agents/library/handoff-functions.sh"; do
  [ -f "$lib_path" ] && source "$lib_path" && break
done

echo "$( [ "$recursive_mode" = true ] && echo "Recursive" || echo "Single" ) mode: $project_path"
```

## Step 0.1: Recursive Mode - Scan for Projects

**Only if `recursive_mode=true`:**

```bash
if [ "$recursive_mode" = true ]; then
  found_projects=()

  while IFS= read -r ai_agents_path; do
    proj_dir=$(dirname "$ai_agents_path")
    # Include if has .claude/commands/ or .ai-agents/library/
    [ -d "$proj_dir/.claude/commands" ] || [ -d "$ai_agents_path/library" ] && found_projects+=("$proj_dir")
  done < <(find "$project_path" -type d -name ".ai-agents" -not -path "*/.ai-agents/*" 2>/dev/null)

  found_projects=($(printf '%s\n' "${found_projects[@]}" | sort -u))
  project_count=${#found_projects[@]}

  [ $project_count -eq 0 ] && { echo "No projects found"; exit 1; }

  echo "Found $project_count project(s):"
  for i in "${!found_projects[@]}"; do
    proj="${found_projects[$i]}"
    if type get_submodule_info &>/dev/null; then
      read commit branch <<< $(get_submodule_info "$proj")
      echo "  $((i+1)). $(basename "$proj") - $branch @ $commit"
    else
      echo "  $((i+1)). $(basename "$proj")"
    fi
  done
fi
```

## Step 0.2: Confirm Batch Update (Recursive Only)

Ask user to proceed with all projects, select specific ones, or cancel.

## Step 0.3: Loop Through Projects (Recursive Only)

```bash
if [ "$recursive_mode" = true ]; then
  for current_project in "${found_projects[@]}"; do
    echo "━━━ Processing: $current_project ━━━"
    project_path="$current_project"
    # Run Steps 1-10 for each project
  done
fi
```

---

## Step 1: Validate Submodule Setup

```bash
if type validate_submodule &>/dev/null; then
  validate_submodule "$project_path" || { echo "Submodule not found"; exit 1; }
else
  [ -d "$project_path/.ai-agents/library" ] || { echo "Submodule not found at .ai-agents/library/"; exit 1; }
fi

cd "$project_path/.ai-agents/library"
current_commit=$(git rev-parse HEAD)
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current: $current_branch @ ${current_commit:0:7}"
cd - > /dev/null
```

## Step 2: Fetch and Show Available Updates

```bash
cd "$project_path/.ai-agents/library"
git fetch origin master

remote_commit=$(git rev-parse origin/master)
[ "$current_commit" = "$remote_commit" ] && { echo "Already up to date"; exit 0; }

echo "New commits:"
git log --oneline --graph HEAD..origin/master

echo "Files changed:"
git diff --stat HEAD..origin/master
cd - > /dev/null
```

## Step 3: Analyze Changes (Optimized - Single Pass)

```bash
cd "$project_path/.ai-agents/library"

# Single pass categorization (vs 5 separate git diff calls)
if type categorize_changes &>/dev/null; then
  categorize_changes HEAD origin/master
  commands_changed=$CHANGES_COMMANDS
  agents_changed=$CHANGES_AGENTS
  prompts_changed=$CHANGES_PROMPTS
  scripts_changed=$CHANGES_SCRIPTS
  docs_changed=$CHANGES_DOCS
else
  # Fallback: single git diff, categorize in bash
  declare -A counts
  while IFS= read -r file; do
    case "$file" in
      .claude/commands/*) ((counts[commands]++)) ;;
      .claude/agents/*) ((counts[agents]++)) ;;
      prompts/*) ((counts[prompts]++)) ;;
      scripts/*) ((counts[scripts]++)) ;;
      docs/*) ((counts[docs]++)) ;;
    esac
  done < <(git diff --name-only HEAD..origin/master)

  commands_changed=${counts[commands]:-0}
  agents_changed=${counts[agents]:-0}
  prompts_changed=${counts[prompts]:-0}
  scripts_changed=${counts[scripts]:-0}
  docs_changed=${counts[docs]:-0}
fi

echo "Changes: Commands=$commands_changed Agents=$agents_changed Prompts=$prompts_changed Scripts=$scripts_changed Docs=$docs_changed"
cd - > /dev/null
```

## Step 4: User Confirmation

Show summary and ask: **Yes** (proceed), **Show details** (detailed analysis), or **Cancel**.

## Step 5: Pull Submodule Updates

```bash
cd "$project_path/.ai-agents/library"
git pull origin master
new_commit=$(git rev-parse HEAD)
echo "Updated to ${new_commit:0:7}"
cd - > /dev/null
```

## Step 6: Detailed Change Analysis (if requested)

Read each changed file and provide analysis with recommendations.

## Step 7: Sync Files to Parent Project (Consolidated)

Uses shared `sync_directory` function or inline equivalent:

```bash
# Determine source (submodule or current repo)
if [ -d "$project_path/.ai-agents/library/.claude" ]; then
  source_base="$project_path/.ai-agents/library"
else
  source_base="$(pwd)"
fi

# Define sync helper if shared function not available
if ! type sync_directory &>/dev/null; then
  sync_directory() {
    local src="$1" dst="$2" name="$3" exts="${4:-md}" check_specific="${5:-false}"
    mkdir -p "$dst"
    local new=0 skip=0 conflict=0 specific=0

    for ext in $exts; do
      for f in "$src"/*."$ext"; do
        [ -f "$f" ] || continue
        local fn=$(basename "$f")
        local dest="$dst/$fn"

        if [ -f "$dest" ]; then
          [ "$check_specific" = "true" ] && grep -q "project-specific\|custom\|local" "$dest" 2>/dev/null && { ((specific++)); continue; }
          diff -q "$f" "$dest" > /dev/null 2>&1 && ((skip++)) || ((conflict++))
        else
          cp "$f" "$dest" && ((new++))
        fi
      done
    done

    echo "$name: $new new, $skip unchanged, $conflict conflicts"
    [ "$specific" -gt 0 ] && echo "  ($specific project-specific skipped)"
  }
fi

# Sync all directories
sync_directory "$source_base/.claude/commands" "$project_path/.claude/commands" "Commands"
sync_directory "$source_base/.claude/agents" "$project_path/.claude/agents" "Agents" "md" "true"
sync_directory "$source_base/prompts" "$project_path/prompts" "Prompts"
sync_directory "$source_base/prompts/roles" "$project_path/prompts/roles" "Prompt Roles"
sync_directory "$source_base/scripts" "$project_path/scripts" "Scripts" "py sh"
```

## Step 8: Update State File Schemas (if changed)

Check if state file schemas changed and show migration guide if needed.

## Step 9: Generate Update Report

Create report at `.ai-agents/update-reports/update-{timestamp}.md`:

```markdown
# AI_agents Submodule Update Report

**Project:** {project_path}
**Updated:** {old_commit} → {new_commit}
**Date:** {timestamp}

## Files Synced
- Commands: {count} ({new} new, {conflicts} conflicts)
- Agents: {count} ({new} new, {specific} project-specific skipped)
- Prompts: {count}
- Scripts: {count}

## Conflicts Detected
{List files requiring manual review}

## New Features
{Summary from commit messages}

## Rollback
```bash
cd .ai-agents/library && git checkout {old_commit}
```
```

## Step 10: Save Report and Suggest Commit

```bash
mkdir -p "$project_path/.ai-agents/update-reports"
# Save report

cd "$project_path"
git status

echo "Suggested commit:"
echo "chore: sync AI_agents submodule ${old_commit:0:7} → ${new_commit:0:7}"
```

## Step 10.1: Batch Summary (Recursive Only)

After all projects processed, show summary table with results per project.

---

# Safety Features

- Non-destructive: Shows changes before applying
- Conflict detection: Warns about local modifications
- Project-specific agents: Skipped automatically
- Rollback support: Can revert to previous version
- Update reports: Full audit trail

# Troubleshooting

**"Submodule not found"**: Initialize with `git submodule add <url> .ai-agents/library`

**"Merge conflicts"**: Files flagged but not auto-merged - review manually

**"Wrong project updated"**: Specify path explicitly: `/pull-ai-agents-submodule ./projects/my-app`

**"No projects found" (recursive)**: Ensure projects have `.ai-agents/` or `.claude/commands/`
