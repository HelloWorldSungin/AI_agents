---
description: Sync AI_agents commands and agents to child projects without submodule setup
argument-hint: [path] [--dry-run | -n]
allowed-tools: [Bash, Read, Write, Glob]
---

<objective>
Recursively find `.ai-agents` directories in child projects and sync the latest commands, agents, and prompts from this AI_agents repository.

This is for projects that **don't** have `.ai-agents/library` submodule initialized - they just have a `.ai-agents` directory for state files. Unlike `/pull-ai-agents-submodule` which requires submodule setup, this command directly copies files from the current repo.
</objective>

<context>
Source repository: !`pwd`
Commands available: !`ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' '` commands
Agents available: !`ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' '` agents
</context>

<process>

## Step 1: Parse Arguments

```bash
dry_run=false
search_path="."

for arg in $ARGUMENTS; do
  case "$arg" in
    --dry-run|-n) dry_run=true ;;
    *) [ -d "$arg" ] && search_path="$arg" ;;
  esac
done

source_repo="$(pwd)"
search_path=$(cd "$search_path" 2>/dev/null && pwd) || { echo "Invalid path"; exit 1; }

echo "Source: $source_repo"
echo "Search: $search_path"
echo "Mode: $( [ "$dry_run" = true ] && echo "DRY RUN" || echo "LIVE" )"
```

## Step 2: Find Child Projects

Find all directories with `.ai-agents` that are NOT this repository and DON'T have submodule initialized:

```bash
found_projects=()

while IFS= read -r ai_agents_dir; do
  project_dir=$(dirname "$ai_agents_dir")

  # Skip the source repository itself
  [ "$project_dir" = "$source_repo" ] && continue

  # Skip if submodule already initialized (use /pull-ai-agents-submodule instead)
  [ -d "$ai_agents_dir/library/.git" ] || [ -f "$ai_agents_dir/library/.git" ] && continue

  found_projects+=("$project_dir")
done < <(find "$search_path" -type d -name ".ai-agents" 2>/dev/null)

# Remove duplicates
found_projects=($(printf '%s\n' "${found_projects[@]}" | sort -u))

echo ""
echo "Found ${#found_projects[@]} project(s) to sync:"
for proj in "${found_projects[@]}"; do
  rel_path=$(realpath --relative-to="$search_path" "$proj" 2>/dev/null || basename "$proj")
  has_commands=$( [ -d "$proj/.claude/commands" ] && echo "yes" || echo "no" )
  has_agents=$( [ -d "$proj/.claude/agents" ] && echo "yes" || echo "no" )
  echo "  - $rel_path (commands: $has_commands, agents: $has_agents)"
done
```

## Step 3: Confirm Sync

Ask user to confirm:
- **Yes** - Sync all projects
- **Select** - Choose specific projects
- **Cancel** - Exit

## Step 4: Sync Each Project

For each project, sync commands, agents, and prompts:

```bash
sync_files() {
  local src_dir="$1"
  local dst_dir="$2"
  local label="$3"
  local check_specific="${4:-false}"

  [ -d "$src_dir" ] || return 0
  mkdir -p "$dst_dir"

  local new=0 updated=0 skipped=0 specific=0

  for src_file in "$src_dir"/*.md; do
    [ -f "$src_file" ] || continue
    local filename=$(basename "$src_file")
    local dst_file="$dst_dir/$filename"

    # Skip project-specific files
    if [ "$check_specific" = "true" ] && [ -f "$dst_file" ]; then
      if grep -q "project-specific\|custom\|local-only" "$dst_file" 2>/dev/null; then
        ((specific++))
        continue
      fi
    fi

    if [ ! -f "$dst_file" ]; then
      # New file
      if [ "$dry_run" = true ]; then
        echo "    + $filename (new)"
      else
        cp "$src_file" "$dst_file"
      fi
      ((new++))
    elif ! diff -q "$src_file" "$dst_file" > /dev/null 2>&1; then
      # Updated file
      if [ "$dry_run" = true ]; then
        echo "    ~ $filename (updated)"
      else
        cp "$src_file" "$dst_file"
      fi
      ((updated++))
    else
      ((skipped++))
    fi
  done

  echo "  $label: $new new, $updated updated, $skipped unchanged"
  [ "$specific" -gt 0 ] && echo "    ($specific project-specific skipped)"
}

# Process each project
for project in "${found_projects[@]}"; do
  echo ""
  echo "━━━ $(basename "$project") ━━━"

  # Create directories if needed
  [ "$dry_run" = true ] || mkdir -p "$project/.claude/commands" "$project/.claude/agents" "$project/prompts/roles"

  # Sync each category
  sync_files "$source_repo/.claude/commands" "$project/.claude/commands" "Commands"
  sync_files "$source_repo/.claude/agents" "$project/.claude/agents" "Agents" "true"
  sync_files "$source_repo/prompts" "$project/prompts" "Prompts"
  sync_files "$source_repo/prompts/roles" "$project/prompts/roles" "Prompt Roles"
done
```

## Step 5: Generate Summary

```bash
echo ""
echo "━━━ Sync Complete ━━━"
echo ""
echo "Projects synced: ${#found_projects[@]}"
echo ""

if [ "$dry_run" = true ]; then
  echo "This was a DRY RUN. No files were modified."
  echo "Run without --dry-run to apply changes."
fi
```

</process>

<success_criteria>
- All child projects with `.ai-agents` directories discovered
- Projects with submodule already initialized are skipped (they should use `/pull-ai-agents-submodule`)
- New commands and agents copied to projects that don't have them
- Updated files overwrite older versions (unless marked project-specific)
- Project-specific files preserved (contain "project-specific", "custom", or "local-only")
- Summary shows what was synced to each project
</success_criteria>

<verification>
After sync, verify:
- Check a synced project: `ls {project}/.claude/commands/`
- Compare counts match source: `ls .claude/commands/*.md | wc -l`
- Confirm project-specific files preserved if they existed
</verification>

<output>
Files synced to each child project:
- `.claude/commands/*.md` - Slash commands
- `.claude/agents/*.md` - Subagent definitions
- `prompts/*.md` - Prompt templates
- `prompts/roles/*.md` - Role prompts
</output>
