---
description: Create manager session handoff with auto-numbering and resume instructions
argument-hint:
allowed-tools: [Read, Write, Bash, Glob]
---

You are creating a manager handoff to transfer context to the next session.

## Handoff Creation Protocol

### Step 1: Determine Session Number

Create handoffs directory if needed and determine next session number:

```bash
# Create handoffs directory
mkdir -p .ai-agents/handoffs

# Find existing handoffs and determine next number
handoffs=$(ls .ai-agents/handoffs/session-*.md 2>/dev/null | sort -V)

if [ -z "$handoffs" ]; then
  # No handoffs exist - this is session 001
  session_num="001"
else
  # Get latest session number and increment
  latest=$(echo "$handoffs" | tail -1 | grep -o '[0-9]\+')
  session_num=$(printf "%03d" $((latest + 1)))
fi

echo "Creating handoff for session: $session_num"
```

### Step 2: Run Cleanup (if available)

Check if cleanup script exists and run it:

```bash
if [ -f "scripts/cleanup-team-communication.py" ]; then
  echo "Running cleanup script..."
  python3 scripts/cleanup-team-communication.py
else
  echo "⚠️  Cleanup script not found at scripts/cleanup-team-communication.py"
  echo "Skipping cleanup. File size may be large."
fi
```

Check current file size:
```bash
wc -c .ai-agents/state/team-communication.json | awk '{print "~" int($1/4) " tokens"}'
```

### Step 3: Read All State Files

```bash
Read .ai-agents/state/team-communication.json
Read .ai-agents/state/session-progress.json
Read .ai-agents/state/feature-tracking.json
```

Review:
- Active tasks and their status
- Completed tasks this session
- Recent decisions made
- Any blockers
- Current phase and progress
- Verification checklist status

### Step 4: Update README.md

Read the current README:
```bash
Read README.md
```

Update the README.md to reflect:
- **Recent Progress**: What was accomplished this session
- **Current Status**: Active work and what's in progress
- **Next Steps**: What should happen next
- **Version**: Update version if significant features completed

Focus on high-level project status, not implementation details.

### Step 5: Create Enhanced Handoff Document

Create handoff at `.ai-agents/handoffs/session-{session_num}.md` with the following comprehensive structure:

```markdown
# Session Handoff - Session {session_num}

## Quick Resume

To resume this manager session in a fresh context:

\`\`\`bash
@manager /manager-resume
\`\`\`

This command will:
- Load your persistent manager agent
- Read this handoff automatically (finds latest session-*.md)
- Load all state files (team-communication, session-progress, feature-tracking)
- Present comprehensive status summary
- Ask what you want to do next

**Manual resume** (if needed):
\`\`\`bash
# 1. Load manager agent
@manager

# 2. Read this handoff
@.ai-agents/handoffs/session-{session_num}.md

# 3. Read state files
@.ai-agents/state/team-communication.json
@.ai-agents/state/session-progress.json
@.ai-agents/state/feature-tracking.json
\`\`\`

## Session Summary

**Session ID:** {session_num}
**Started:** {session-progress.start_time}
**Ended:** {current timestamp}
**Duration:** {calculated duration}

### What Was Accomplished

{Extract from session-progress.completed_tasks and team-communication.agent_updates}
- TASK-001: {description} ✓
- TASK-002: {description} ✓

### Current Status

- **Phase:** {session-progress.current_phase}
- **Completed Phases:** {list from session-progress.completed_phases}
- **Active Tasks:** {from team-communication.manager_instructions.active_tasks}
- **Blocked Tasks:** {from session-progress.blocked_tasks if any}

### Decisions Made This Session

{From session-progress.decisions_made}
1. {decision} - {rationale}
2. {decision} - {rationale}

## State Files Snapshot

### team-communication.json
- Last updated: {last_updated}
- Agent updates: {count of agent_updates}
- Active tasks: {count from manager_instructions.active_tasks}
- Completed tasks: {count from manager_instructions.completed_tasks}
- Questions pending: {count from manager_instructions.questions_for_manager}

### session-progress.json
- Current phase: {current_phase}
- Completed phases: {count}/{total phases}
- Completed tasks: {count}
- Progress: {percentage based on completed vs total phases}%

### feature-tracking.json
- Feature: {feature}
- Status: {status}
- Verification checklist: {completed_count}/{total_count} items
- Integration status: {integration_status}
- Review status: {review_status}

## Next Session Priority

{session-progress.next_session_priority OR infer from current status}

**Recommended Next Steps:**
1. {based on active_tasks and current_phase}
2. {next logical step}
3. {follow-up actions}

## Context for Next Manager

{Important context that new manager session should know}
- Completed work summary
- Any technical decisions to remember
- Known issues or considerations
- Integration points established

---

Generated: {ISO-8601 timestamp}
By: Manager session {session_num}
```

Key content to include:
- Quick Resume section prominently at top with both automated and manual instructions
- Session summary with timestamps and duration calculation
- All three state file snapshots with metrics
- Next session priority from session-progress.json or inferred
- Comprehensive context for next manager

### Step 6: Update session-progress.json

Add handoff reference to session-progress.json:

```json
{
  ...existing fields...,
  "last_handoff": {
    "session_id": "{session_num}",
    "file": ".ai-agents/handoffs/session-{session_num}.md",
    "timestamp": "{ISO-8601}",
    "next_session_priority": "{priority text}"
  }
}
```

Update next_session_priority if not already set (infer from current state).

### Step 7: Commit Everything

Stage all changes:
```bash
git add .ai-agents/handoffs/session-{session_num}.md .ai-agents/state/ README.md
```

Create commit:
```bash
git commit -m "chore: manager handoff - session {session_num}

Session summary:
- Phase: {current_phase}
- Tasks completed: {count}
- Tasks active: {count}
- Communication file: ~{X} tokens (cleaned)
- README updated with current status

Next session: {next_session_priority or immediate action}"
```

### Step 8: Inform User

Report to user:
```
Manager handoff created:
- Handoff: .ai-agents/handoffs/session-{session_num}.md
- Communication file: .ai-agents/state/team-communication.json (~{X} tokens)
- Session progress: .ai-agents/state/session-progress.json
- Feature tracking: .ai-agents/state/feature-tracking.json
- README.md updated with session progress

To resume: Start new manager session and run:
  @manager /manager-resume
```

Proceed with handoff creation now.
