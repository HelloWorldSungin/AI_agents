---
description: Resume manager session from latest handoff with full context
argument-hint:
allowed-tools: [Read, Glob, Bash]
---

You are resuming a manager session from the latest handoff.

## Resume Protocol

### Step 1: Find Latest Handoff

Find the most recent handoff file:

```bash
# List all handoffs, sort by version number, get latest
latest_handoff=$(ls .ai-agents/handoffs/session-*.md 2>/dev/null | sort -V | tail -1)

if [ -z "$latest_handoff" ]; then
  echo "❌ No handoff files found in .ai-agents/handoffs/"
  echo ""
  echo "This is likely your first manager session."
  echo ""
  echo "To create a handoff for future sessions:"
  echo "  /manager-handoff"
  exit 0
fi

echo "Found latest handoff: $latest_handoff"
```

### Step 2: Read All State Files

Read the latest handoff and all state files:

```bash
Read $latest_handoff
Read .ai-agents/state/team-communication.json
Read .ai-agents/state/session-progress.json
Read .ai-agents/state/feature-tracking.json
```

Verify files exist. If any are missing, show warning but continue with available files.

### Step 3: Extract Session Information

From the handoff file, extract:
- Session number (from filename)
- Session end timestamp
- Completed work summary
- Next priority

From state files, extract:
- **session-progress.json:**
  - current_phase
  - completed_phases (count)
  - completed_tasks (list with details)
  - active_tasks
  - blocked_tasks
  - next_session_priority

- **team-communication.json:**
  - Last 3-5 agent_updates (most recent first)
  - manager_instructions.active_tasks
  - manager_instructions.questions_for_manager
  - manager_instructions.completed_tasks

- **feature-tracking.json:**
  - verification_checklist (items with status)
  - integration_status
  - review_status

### Step 4: Generate Comprehensive Resume Summary

Present the following structured summary:

```markdown
# Resuming Manager Session

## Last Session Summary

**Session:** {session_num from latest handoff filename}
**Ended:** {timestamp from handoff or session-progress}

### Completed

{Extract from session-progress.completed_tasks}
✓ INFRA-001: Infrastructure Planning & Analysis
✓ TASK-001: /create-sub-task Command Implementation
✓ TASK-002: /create-manager-meta-prompt Enhancement
✓ TASK-003: /manager-handoff Enhancement

### Current Status

**Phase:** {session-progress.current_phase}
**Progress:** {completed_phases_count} of {total_phases} phases complete

## Recent Agent Updates

{Last 3-5 updates from team-communication.agent_updates - most recent first}

Most recent:
- **{agent_id}** ({timestamp}): {summary}
- **{agent_id}** ({timestamp}): {summary}
- **{agent_id}** ({timestamp}): {summary}

## Current State

### Active Tasks

{From team-communication.manager_instructions.active_tasks}

{If active_tasks is empty or array is empty}
✅ No active tasks - ready to start new phase

{If active_tasks has items}
⏳ Active:
- {task_id}: {description} (assigned to {assigned_to})

### Blocked Tasks

{From session-progress.blocked_tasks}

{If blocked_tasks is empty or array is empty}
✅ No blockers

{If blocked_tasks has items}
🚫 Blocked:
- {task_id}: {blocker description}

### Questions Pending

{From team-communication.manager_instructions.questions_for_manager}

{If empty or array is empty}
✅ No pending questions

{If has items}
❓ Pending:
- {question from agent}

## Verification Status

{From feature-tracking.verification_checklist}

Progress: {completed_count}/{total_count} items

Recent completions:
- ✓ {item 1 where status = "completed"}
- ✓ {item 2 where status = "completed"}

Still pending:
- ⏳ {item 1 where status = "pending" or "in_progress"}
- ⏳ {item 2 where status = "pending" or "in_progress"}

## Next Priority

{From session-progress.next_session_priority OR last handoff OR infer from current_phase}

**Recommended Next Steps:**
1. {based on current_phase and active_tasks}
2. {next logical step from plan}
3. {follow-up actions}

---

**Ready to continue?**

Options:
- Continue with next phase
- Review specific agent updates
- Address blocked tasks (if any)
- Answer pending questions (if any)
- Revise plan based on progress

What would you like to do?
```

### Step 5: Handle Edge Cases

**Case 1: No handoffs exist**
Show error message as per Step 1 bash script.

**Case 2: State files missing**
```
⚠️  Warning: Some state files not found

Missing:
- {list missing files}

Proceeding with available state files...
```

Continue processing with whatever files are available.

**Case 3: Empty state files or arrays**
Handle gracefully - show "No data" or "✅ None" instead of errors.

**Case 4: Multiple handoffs (normal case)**
Always use the latest (sort -V ensures proper version sorting).

### Implementation Notes

**Counting Completed Items:**
- For verification checklist: Count items where `status === "completed"`
- For phases: Count items in `completed_phases` array
- For total phases: Extract from `manager_instructions.phases` array length if available

**Formatting Timestamps:**
- Display in readable format if possible
- Fall back to ISO-8601 if conversion not available

**Session Number Extraction:**
- Extract from filename: `session-001.md` → `001`
- Use regex or string manipulation: `[0-9]{3}`

**Recent Updates Sorting:**
- Take last 3-5 items from `agent_updates` array (array is chronological)
- Display most recent first (reverse order)

**Inferring Next Priority:**
- If `next_session_priority` is set in session-progress.json: use it
- Else if handoff contains next priority: use it
- Else infer from current_phase: "Continue with {current_phase}"

Proceed with resume now.
