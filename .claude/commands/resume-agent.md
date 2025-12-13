---
description: Resume a paused agent session with full state restoration
argument-hint: [--status-only]
---

Resume a previously paused agent session, restoring all state and context.

## Arguments

- `--status-only`: Only show pause state, don't actually resume

## Process

### Step 1: Check for Pause State

```
IF .ai-agents/state/pause_state.json does NOT exist:
  ERROR: "No paused session found"
  SUGGEST: "Use /continue-project to start a new session"
  EXIT
```

### Step 2: Load Pause State

```python
with open('.ai-agents/state/pause_state.json') as f:
    pause_state = json.load(f)

paused_at = pause_state['paused_at']
session_id = pause_state['session_id']
turn_number = pause_state['turn_number']
summary = pause_state['summary']
in_progress_tasks = pause_state['in_progress_tasks']
```

### Step 3: Calculate Time Since Pause

```python
pause_time = datetime.fromisoformat(paused_at)
time_since_pause = datetime.now() - pause_time

# Check if pause is stale (>24 hours)
if time_since_pause > timedelta(hours=24):
    WARN: "Session paused {time_since_pause} ago"
    WARN: "External state may have changed"
```

### Step 4: If --status-only, Show State and Exit

```markdown
# Paused Session Status

**Paused At**: {paused_at}
**Time Ago**: {time_since_pause}
**Turn**: {turn_number}

## Summary
{summary}

## In Progress Tasks
{list with notes}

## Progress at Pause
{progress_snapshot}

## To Resume
/resume-agent
```

### Step 5: Connect to State Provider

```python
from scripts.state_providers import get_provider

provider = get_provider()
```

### Step 6: Verify External State

```python
# Check if tasks are still in expected state
current_tasks = provider.get_tasks()

# Compare with pause state
changes = detect_state_changes(pause_state, current_tasks)

if changes:
    WARN: "External state changed since pause"
    for change in changes:
        print(f"  - {change}")
    ASK: "Continue with updated state? (y/n)"
```

### Step 7: Start New Session

```python
from scripts.execution import TurnCounter

counter = TurnCounter()
new_session_id = counter.start_session()

# Record resume in META
provider.add_session_comment(f"""
## Session Resumed

**Time**: {datetime.now().isoformat()}
**Previous Session**: {session_id}
**Previous Turn**: {turn_number}
**Time Since Pause**: {time_since_pause}

### Context Restored
{summary}

### In Progress Tasks
{format_in_progress_tasks(in_progress_tasks)}
""")

provider.start_session()
```

### Step 8: Remove Pause State

```python
os.remove('.ai-agents/state/pause_state.json')
```

### Step 9: Output Context Summary

```markdown
# Session Resumed

**New Session**: {new_session_id}
**Resuming From**: {session_id} (Turn {turn_number})
**Pause Duration**: {time_since_pause}

## Context Restored

### What You Were Doing
{summary}

### In Progress Tasks
{For each task:}
#### {task_id}: {title}
**Status**: In Progress
**Notes from pause**: {notes}

**Acceptance Criteria**:
{list with checkboxes}

---

## Current State
- **Todo**: {count}
- **In Progress**: {count}
- **Done**: {count}
- **Completion**: {percentage}%

## Recommended Actions
1. {If tasks in progress:} Continue {task_id} - {title}
2. {If blocked:} Review blockers
3. {If changes detected:} Review external changes

## Ready to Continue
Pick up where you left off!
```

## State Change Detection

### Task State Changes
```
- Task moved from In Progress → Done (someone else completed it)
- Task moved from In Progress → Blocked (new blocker added)
- New tasks created since pause
- Tasks deleted/cancelled
```

### Response to Changes
```
If completed by someone else:
  "TASK-018 was completed while paused. Skip to next task?"

If blocked:
  "TASK-018 is now blocked: {blocker}. Work on different task?"

If new tasks:
  "3 new tasks added since pause. Review priority?"
```

## Error Handling

### Corrupted Pause State
```
TRY: Parse pause state
CATCH: JSON error
  WARN: "Pause state corrupted"
  SUGGEST: "Use /continue-project for fresh start"
  OFFER: "Show raw file contents for recovery?"
```

### Provider Connection Failed
```
WARN: "Cannot verify external state"
ASK: "Continue with local pause state only? (y/n)"
```

### Tasks No Longer Exist
```
WARN: "Task {task_id} no longer exists"
SUGGEST: "It may have been completed or cancelled"
CONTINUE: "Proceeding with remaining tasks"
```

## Examples

### Standard Resume
```
/resume-agent
```

### Status Check
```
/resume-agent --status-only
```

### Output Example (Standard)
```markdown
# Session Resumed

**New Session**: 20240116-090000
**Resuming From**: 20240115-140000 (Turn 45)
**Pause Duration**: 19h 0m

## Context Restored

### What You Were Doing
Working on password reset, email template done

### In Progress Tasks

#### TASK-018: Implement password reset
**Status**: In Progress
**Notes from pause**: Email template done, need validation UI

**Acceptance Criteria**:
- [x] Reset request sends email
- [x] Reset link valid for 24 hours
- [ ] New password validation
- [ ] Success confirmation page

---

## Current State
- **Todo**: 5
- **In Progress**: 1
- **Done**: 12
- **Completion**: 66%

## Recommended Actions
1. Continue TASK-018 - New password validation next

## Ready to Continue
Pick up where you left off!
```

### Output Example (With Changes)
```markdown
# Session Resumed (With Changes)

**New Session**: 20240116-090000
**Resuming From**: 20240115-140000 (Turn 45)
**Pause Duration**: 19h 0m

## ⚠️ External State Changed

The following changes occurred while paused:

- TASK-019 (Session management) moved to Done
- TASK-021 (Rate limiting) added (P2)
- 2 commits pushed to main branch

## Context Restored
...
```
