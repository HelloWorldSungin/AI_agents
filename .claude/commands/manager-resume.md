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
Read .ai-agents/state/manager-context.json
```

Verify files exist. If any are missing, show warning but continue with available files.

### Step 2.5: Extract Manager Agent Name

Extract the manager agent name from the handoff or session-progress.json:

**From handoff document:**
Look for line: `**Manager Agent:** \`@{agent_name}\``

**From session-progress.json:**
Look for field: `"manager_agent": "@{agent_name}"`

**Fallback:**
If not found in either location, use `"manager"` as default.

Store the extracted agent name for use in the resume summary.

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
  - current_branch
  - base_branch
  - active_branches (array of unmerged feature branches)

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

**Manager Agent:** `@{agent_name}` {if agent_name != "manager", otherwise show: "(no specific agent detected)"}

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

## Original Plan Context

{If .ai-agents/state/manager-context.json exists:}

**Project:** {plan_summary.project}
**Objective:** {plan_summary.objective}
**Mode:** {plan_summary.mode}

### Phases Overview

{For each phase in plan_summary.phases:}
- **{phase.name}:** {phase.description}

### Success Criteria

{For each criterion in plan_summary.success_criteria:}
- [ ] {criterion}

**Plan Source:** {plan_source}

{If manager-context.json does NOT exist:}

⚠️ No original plan context available (manager-context.json not found).

This manager session was created before plan context tracking was added,
or was started without using `/create-manager-meta-prompt`.

You can still continue - use the handoff document and state files for context.

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

## ⚠️ Git Branch Status

{From session-progress.json: current_branch, base_branch, active_branches}

**Current Branch:** {current_branch}
**Base Branch:** {base_branch}

### Unmerged Feature Branches

{If active_branches array exists and has items:}

| Branch | Commits Ahead | Last Commit | Status |
|--------|---------------|-------------|--------|
| `{name}` | {commits_ahead} | {last_commit} {last_commit_message} | {status} |

**⚠️ ACTION REQUIRED:** Review these branches before starting new work!
- Merge completed branches: `git checkout {base_branch} && git merge {branch_name}`
- Continue incomplete work: `git checkout {branch_name}`
- Delete abandoned: `git branch -d {branch_name}`

{If active_branches is empty or not present:}
✅ No unmerged feature branches - all work is on {base_branch}

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

---

**Note:** You loaded this resume using `@{agent_name} /manager-resume`. This manager agent is persistent across sessions - use it for all handoffs and resumes.

What would you like to do?
```

### Step 5: Verify Manager Agent Match

After extracting the agent name, verify it matches the current context:

**If agent name extracted from handoff/state:**
```markdown
✓ Loaded with correct manager agent: @{agent_name}
```

**If no agent name found (backward compatibility):**
```markdown
⚠️  No manager agent recorded in handoff (older format)

This handoff was created before manager agent tracking was added.
You can continue, but future handoffs will track the agent name automatically.

Current session uses: @{detected_from_current_context or "manager"}
```

**If mismatch detected (user loaded wrong agent):**
```markdown
⚠️  Warning: Agent mismatch detected!

Handoff expects: @{expected_agent_name}
You loaded with: @{current_agent_name}

Recommended: Use `@{expected_agent_name} /manager-resume` instead for consistency.
Continuing anyway...
```

### Step 6: Handle Edge Cases

**Case 1: No handoffs exist**
Show error message as per Step 1 bash script.

**Case 2: Manager agent name not found**
Use "manager" as default and show backward compatibility message.

**Case 3: State files missing**
```
⚠️  Warning: Some state files not found

Missing:
- {list missing files}

Proceeding with available state files...
```

Continue processing with whatever files are available.

**Case 4: Empty state files or arrays**
Handle gracefully - show "No data" or "✅ None" instead of errors.

**Case 5: Multiple handoffs (normal case)**
Always use the latest (sort -V ensures proper version sorting).

### Implementation Notes

**Extracting Manager Agent Name:**
- **Priority 1:** Look in handoff markdown for: `**Manager Agent:** \`@agent-name\``
- **Priority 2:** Look in session-progress.json for: `"manager_agent": "@agent-name"`
- **Fallback:** Use "manager" as default for backward compatibility
- Strip the `@` prefix when storing, add it back when displaying

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

**Extracting Plan Context from manager-context.json:**
- Check if `.ai-agents/state/manager-context.json` exists
- If exists: Extract `plan_summary.project`, `plan_summary.objective`, `plan_summary.mode`
- Extract phases array and format each as "Phase Name: Description"
- Extract success_criteria array and format as checklist items
- Include `plan_source` to show where the plan came from
- If file doesn't exist: Show backward compatibility message

**Why Plan Context Matters:**
- New managers immediately understand the bigger picture
- Success criteria provide clear targets to track progress against
- Phases overview shows where the project started and where it's going
- Prevents managers from losing sight of original objectives

Proceed with resume now.
