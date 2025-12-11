#!/bin/bash
# Shared functions for manager handoff workflows
# Used by: manager-handoff.md, session-handoff subagent, pull-ai-agents-submodule

#==============================================================================
# SESSION NUMBER MANAGEMENT
#==============================================================================

# Determine the next session number for handoffs
# Usage: session_num=$(determine_session_number)
determine_session_number() {
  mkdir -p .ai-agents/handoffs

  local handoffs=$(ls .ai-agents/handoffs/session-*.md 2>/dev/null | sort -V)

  if [ -z "$handoffs" ]; then
    echo "001"
  else
    local latest=$(echo "$handoffs" | tail -1 | grep -o '[0-9]\+')
    printf "%03d" $((latest + 1))
  fi
}

#==============================================================================
# CLEANUP SCRIPT DISCOVERY
#==============================================================================

# Find cleanup script in various locations (supports submodule setups)
# Usage: cleanup_script=$(find_cleanup_script)
find_cleanup_script() {
  local paths=(
    "scripts/cleanup-team-communication.py"
    "external/AI_agents/scripts/cleanup-team-communication.py"
    "submodules/AI_agents/scripts/cleanup-team-communication.py"
    ".ai-agents/library/scripts/cleanup-team-communication.py"
    "ai-agents/scripts/cleanup-team-communication.py"
  )

  for path in "${paths[@]}"; do
    if [ -f "$path" ]; then
      echo "$path"
      return 0
    fi
  done

  return 1
}

# Run cleanup script if available
# Usage: run_cleanup
run_cleanup() {
  local cleanup_script=$(find_cleanup_script)

  if [ -n "$cleanup_script" ]; then
    echo "Running cleanup: $cleanup_script"
    python3 "$cleanup_script"
    return 0
  else
    echo "Cleanup script not found (checked: scripts/, external/AI_agents/, submodules/AI_agents/, .ai-agents/library/)"
    return 1
  fi
}

#==============================================================================
# GIT BRANCH DISCOVERY
#==============================================================================

# Get base branch name (main or master)
# Usage: base_branch=$(get_base_branch)
get_base_branch() {
  if git show-ref --verify --quiet refs/heads/main; then
    echo "main"
  elif git show-ref --verify --quiet refs/heads/master; then
    echo "master"
  else
    git rev-parse --abbrev-ref HEAD
  fi
}

# Discover all unmerged feature branches
# Usage: discover_feature_branches [--json]
# Outputs branch info to stdout
discover_feature_branches() {
  local json_output=false
  [ "$1" = "--json" ] && json_output=true

  local current_branch=$(git rev-parse --abbrev-ref HEAD)
  local base_branch=$(get_base_branch)

  if [ "$json_output" = true ]; then
    echo "["
    local first=true
  else
    echo "Current branch: $current_branch"
    echo "Base branch: $base_branch"
    echo ""
  fi

  git branch --list | while read branch; do
    branch=$(echo "$branch" | sed 's/^[\* ]*//')
    [ "$branch" = "$base_branch" ] && continue

    local commits_ahead=$(git rev-list --count "$base_branch".."$branch" 2>/dev/null || echo "0")

    if [ "$commits_ahead" -gt 0 ]; then
      local last_commit_hash=$(git log -1 --format="%h" "$branch" 2>/dev/null)
      local last_commit_msg=$(git log -1 --format="%s" "$branch" 2>/dev/null)

      if [ "$json_output" = true ]; then
        [ "$first" = true ] || echo ","
        first=false
        cat <<EOF
    {
      "name": "$branch",
      "commits_ahead": $commits_ahead,
      "last_commit": "$last_commit_hash",
      "last_commit_message": "$last_commit_msg",
      "status": "unknown"
    }
EOF
      else
        echo "  - $branch: $commits_ahead commits ahead"
        echo "    Last: $last_commit_hash $last_commit_msg"
      fi
    fi
  done

  [ "$json_output" = true ] && echo "]"
}

#==============================================================================
# FILE SYNC UTILITIES (for pull-ai-agents-submodule)
#==============================================================================

# Generic directory sync function
# Usage: sync_directory <source_dir> <dest_dir> <type_name> [extensions] [check_project_specific]
# Returns: JSON object with counts
sync_directory() {
  local source_dir="$1"
  local dest_dir="$2"
  local type_name="$3"
  local extensions="${4:-md}"
  local check_project_specific="${5:-false}"

  # Create destination if needed
  mkdir -p "$dest_dir"

  local new_count=0
  local skipped_count=0
  local conflict_count=0
  local project_specific_count=0

  echo ""
  echo "Syncing $type_name from: $source_dir"
  echo ""

  # Handle multiple extensions (space-separated)
  for ext in $extensions; do
    for source_file in "$source_dir"/*."$ext"; do
      [ -f "$source_file" ] || continue

      local filename=$(basename "$source_file")
      local dest="$dest_dir/$filename"

      if [ -f "$dest" ]; then
        # Check for project-specific markers
        if [ "$check_project_specific" = "true" ]; then
          if grep -q "project-specific\|custom\|local" "$dest" 2>/dev/null; then
            echo "  -> $filename - skipped (project-specific)"
            ((project_specific_count++))
            continue
          fi
        fi

        # Compare files
        if diff -q "$source_file" "$dest" > /dev/null 2>&1; then
          echo "  = $filename - up to date"
          ((skipped_count++))
        else
          echo "  ! $filename - conflict (local differs)"
          ((conflict_count++))
        fi
      else
        cp "$source_file" "$dest"
        echo "  + $filename - created"
        ((new_count++))
      fi
    done
  done

  echo ""
  echo "$type_name sync: $new_count new, $skipped_count unchanged, $conflict_count conflicts"
  [ "$project_specific_count" -gt 0 ] && echo "  ($project_specific_count project-specific skipped)"

  # Return counts via environment variables (bash doesn't support returning arrays)
  export SYNC_NEW=$new_count
  export SYNC_SKIPPED=$skipped_count
  export SYNC_CONFLICTS=$conflict_count
  export SYNC_PROJECT_SPECIFIC=$project_specific_count
}

# Categorize changed files from git diff (single pass)
# Usage: categorize_changes <ref1> <ref2>
# Sets: CHANGES_COMMANDS, CHANGES_AGENTS, CHANGES_PROMPTS, CHANGES_SCRIPTS, CHANGES_DOCS
categorize_changes() {
  local ref1="$1"
  local ref2="$2"

  local commands=0
  local agents=0
  local prompts=0
  local scripts=0
  local docs=0

  while IFS= read -r file; do
    case "$file" in
      .claude/commands/*) ((commands++)) ;;
      .claude/agents/*) ((agents++)) ;;
      prompts/*) ((prompts++)) ;;
      scripts/*) ((scripts++)) ;;
      docs/*) ((docs++)) ;;
    esac
  done < <(git diff --name-only "$ref1".."$ref2")

  export CHANGES_COMMANDS=$commands
  export CHANGES_AGENTS=$agents
  export CHANGES_PROMPTS=$prompts
  export CHANGES_SCRIPTS=$scripts
  export CHANGES_DOCS=$docs
}

#==============================================================================
# TOKEN ESTIMATION
#==============================================================================

# Estimate tokens from file size
# Usage: estimate_tokens <file_path>
estimate_tokens() {
  local file="$1"
  if [ -f "$file" ]; then
    local bytes=$(wc -c < "$file" | tr -d ' ')
    echo "~$((bytes / 4)) tokens"
  else
    echo "file not found"
  fi
}

#==============================================================================
# MANAGER AGENT DETECTION
#==============================================================================

# Detect manager agent from .claude/agents/
# Usage: agent_name=$(detect_manager_agent)
detect_manager_agent() {
  local agents=$(ls .claude/agents/*.md 2>/dev/null | grep -v "README.md" | head -1)

  if [ -n "$agents" ]; then
    basename "$agents" .md
  else
    echo "manager"
  fi
}

#==============================================================================
# SUBMODULE VALIDATION
#==============================================================================

# Validate that AI_agents submodule exists and is valid
# Usage: validate_submodule <project_path>
# Returns: 0 if valid, 1 if not
validate_submodule() {
  local project_path="${1:-.}"

  if [ ! -d "$project_path/.ai-agents/library" ]; then
    return 1
  fi

  # Check if it's actually a git repo
  if [ ! -f "$project_path/.ai-agents/library/.git" ] && \
     [ ! -d "$project_path/.ai-agents/library/.git" ]; then
    return 1
  fi

  # Verify we can get HEAD
  (cd "$project_path/.ai-agents/library" && git rev-parse HEAD > /dev/null 2>&1) || return 1

  return 0
}

# Get submodule commit info
# Usage: get_submodule_info <project_path>
# Outputs: <commit> <branch>
get_submodule_info() {
  local project_path="${1:-.}"

  if validate_submodule "$project_path"; then
    local commit=$(cd "$project_path/.ai-agents/library" && git rev-parse --short HEAD)
    local branch=$(cd "$project_path/.ai-agents/library" && git rev-parse --abbrev-ref HEAD)
    echo "$commit $branch"
  else
    echo "unknown unknown"
  fi
}
