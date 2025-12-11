---
description: Create manager session handoff with auto-numbering and resume instructions
argument-hint: [--delegate]
allowed-tools: [Read, Write, Bash, Glob, Task]
---

You are creating a manager handoff to transfer context to the next session.

## Handoff Creation Protocol

### Step 0: Decide Execution Mode

**For Manager Agents:** If you're a manager agent with high context window usage (>70%), delegate to the session-handoff subagent to preserve your context.

**Check for delegation flag:**
- If `$ARGUMENTS` contains `--delegate` OR
- If you're a manager agent and want to preserve context

**To delegate (recommended for managers):**

Use the Task tool:
```
Task tool parameters:
- subagent_type: "session-handoff"
- description: "Create session handoff"
- prompt: |
    Create a session handoff.
    Manager agent: @{your-manager-agent-name}
    Session context: {brief summary of what was accomplished}
```

After the subagent completes, inform the user of the resume command and you're done.

**To run directly:** Proceed with Steps 1-9 below.

---

### Step 1: Determine Session Number

Source shared functions and determine session number:

```bash
# Source shared utilities (checks multiple locations)
for lib_path in ".ai-agents/library/handoff-functions.sh" \
                "external/AI_agents/.ai-agents/library/handoff-functions.sh" \
                "submodules/AI_agents/.ai-agents/library/handoff-functions.sh"; do
  [ -f "$lib_path" ] && source "$lib_path" && break
done

# If sourced successfully, use function; otherwise inline fallback
if type determine_session_number &>/dev/null; then
  session_num=$(determine_session_number)
else
  mkdir -p .ai-agents/handoffs
  handoffs=$(ls .ai-agents/handoffs/session-*.md 2>/dev/null | sort -V)
  if [ -z "$handoffs" ]; then
    session_num="001"
  else
    latest=$(echo "$handoffs" | tail -1 | grep -o '[0-9]\+')
    session_num=$(printf "%03d" $((latest + 1)))
  fi
fi

echo "Creating handoff for session: $session_num"
```

### Step 2: Run Cleanup (if available)

```bash
# Use shared function if available
if type run_cleanup &>/dev/null; then
  run_cleanup
else
  # Inline fallback
  for path in "scripts/cleanup-team-communication.py" \
              "external/AI_agents/scripts/cleanup-team-communication.py" \
              ".ai-agents/library/scripts/cleanup-team-communication.py"; do
    [ -f "$path" ] && python3 "$path" && break
  done
fi

# Check current file size
wc -c .ai-agents/state/team-communication.json 2>/dev/null | awk '{print "~" int($1/4) " tokens"}'
```

### Step 2.5: Discover Active Branches

**CRITICAL:** Discover all feature branches to prevent duplicate work.

```bash
if type discover_feature_branches &>/dev/null; then
  discover_feature_branches
else
  # Inline fallback
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  base_branch="main"
  git show-ref --verify --quiet refs/heads/main || base_branch="master"

  echo "Current: $current_branch, Base: $base_branch"
  echo ""

  git branch --list | while read branch; do
    branch=$(echo "$branch" | sed 's/^[\* ]*//')
    [ "$branch" = "$base_branch" ] && continue
    commits=$(git rev-list --count "$base_branch".."$branch" 2>/dev/null || echo "0")
    [ "$commits" -gt 0 ] && echo "  - $branch: $commits commits ahead"
  done
fi
```

Store branch info for the handoff document.

### Step 3: Detect Manager Agent

```bash
if type detect_manager_agent &>/dev/null; then
  agent_name=$(detect_manager_agent)
else
  agents=$(ls .claude/agents/*.md 2>/dev/null | grep -v "README.md" | head -1)
  agent_name=${agents:+$(basename "$agents" .md)}
  agent_name=${agent_name:-manager}
fi
echo "Manager agent: @$agent_name"
```

### Step 4: Read All State Files

Read and review:
- `.ai-agents/state/team-communication.json`
- `.ai-agents/state/session-progress.json`
- `.ai-agents/state/feature-tracking.json`

Extract: active tasks, completed tasks, decisions, blockers, current phase.

### Step 5: Update README.md

Read current README.md and update with:
- Recent progress from this session
- Current project status
- Next steps

### Step 5.5: Update CLAUDE.md

CLAUDE.md is auto-read by Claude Code at session start. Update with:

```markdown
# {Project} - Project Context

## Current Project State

**Manager Agent:** `@{agent_name}`
**Last Session:** {session_num}
**Current Phase:** {current_phase}
**Last Updated:** {timestamp}

## Quick Resume

```
@{agent_name} /manager-resume
```

## Active Work

- Phase: {current_phase}
- Active tasks: {list or "None"}
- Blocked tasks: {list or "None"}

## Recent Progress

{Last 5 completed tasks}

## Next Priority

{next_session_priority}

## State Files

- `.ai-agents/handoffs/session-{session_num}.md`
- `.ai-agents/state/team-communication.json`
- `.ai-agents/state/session-progress.json`
```

### Step 6: Create Handoff Document

Create `.ai-agents/handoffs/session-{session_num}.md`:

```markdown
# Session Handoff - Session {session_num}

## Quick Resume

**Manager Agent:** `@{agent_name}`

```
@{agent_name} /manager-resume
```

## Session Summary

**Session ID:** {session_num}
**Ended:** {timestamp}

### What Was Accomplished
{completed tasks}

### Current Status
- **Phase:** {current_phase}
- **Active Tasks:** {list}
- **Blocked Tasks:** {list}

### Decisions Made
{decisions}

## State Files Snapshot

- team-communication.json: {metrics}
- session-progress.json: {metrics}
- feature-tracking.json: {metrics}

## Git Branch Status

**Current Branch:** {current_branch}
**Base Branch:** {base_branch}

### Unmerged Feature Branches

| Branch | Commits Ahead | Last Commit |
|--------|---------------|-------------|
| `{branch}` | {N} | {hash} {msg} |

{If none: "No unmerged branches"}

## Next Session Priority

{priority and recommended steps}

## Context for Next Manager

{Important context}

---
Generated: {timestamp}
```

### Step 7: Update session-progress.json

Add handoff reference and active branches:

```json
{
  "manager_agent": "@{agent_name}",
  "current_branch": "{current_branch}",
  "base_branch": "{base_branch}",
  "active_branches": [...],
  "last_handoff": {
    "session_id": "{session_num}",
    "file": ".ai-agents/handoffs/session-{session_num}.md",
    "timestamp": "{ISO-8601}",
    "next_session_priority": "{priority}"
  }
}
```

### Step 8: Commit Everything

```bash
git add .ai-agents/handoffs/session-{session_num}.md .ai-agents/state/ README.md CLAUDE.md
git commit -m "chore: manager handoff - session {session_num}

Session: Phase {phase}, {N} tasks completed, {M} active
Next: {priority}"
```

### Step 9: Inform User

```
Manager handoff created:
- Handoff: .ai-agents/handoffs/session-{session_num}.md
- CLAUDE.md updated (auto-loaded on session start)

To resume: @{agent_name} /manager-resume
```
