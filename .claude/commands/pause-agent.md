---
description: Pause the current agent session with state preservation
argument-hint: [--summary "optional summary"]
---

Pause the current agent session, preserving state for later resumption.

## Arguments

- `--summary`: Optional summary of current work (will prompt if not provided)

## Process

### Step 1: Validate Active Session

```
IF no active session:
  ERROR: "No active session to pause"
  EXIT
```

### Step 2: Capture Current State

Gather state information:

```python
from scripts.state_providers import get_provider
from scripts.execution import TurnCounter

provider = get_provider()
counter = TurnCounter()

state = {
    "session_id": counter.session_id,
    "turn_number": counter.current_turn,
    "session_turns": counter.get_session_turns(),
    "progress": provider.get_progress_summary(),
    "in_progress_tasks": provider.get_tasks(status=TaskStatus.IN_PROGRESS),
    "context_usage": get_current_context_usage()
}
```

### Step 3: Get Pause Summary

```
IF --summary provided:
  summary = $ARGUMENTS.summary
ELSE:
  PROMPT: "Enter pause summary (what you were working on):"
  summary = user_input
```

### Step 4: Save Pause State

Create pause marker:

```python
pause_state = {
    "paused_at": datetime.now().isoformat(),
    "session_id": state["session_id"],
    "turn_number": state["turn_number"],
    "summary": summary,
    "in_progress_tasks": [
        {"id": t.id, "title": t.title, "notes": ""}
        for t in state["in_progress_tasks"]
    ],
    "context_usage": state["context_usage"],
    "progress_snapshot": state["progress"]
}

with open('.ai-agents/state/pause_state.json', 'w') as f:
    json.dump(pause_state, f, indent=2)
```

### Step 5: Update External State

```python
# Record pause in META issue
provider.add_session_comment(f"""
## Session Paused

**Time**: {datetime.now().isoformat()}
**Turn**: {state['turn_number']}
**Reason**: Manual pause

### Summary
{summary}

### In Progress
{format_in_progress_tasks(state['in_progress_tasks'])}

### Context Usage
{state['context_usage'] * 100:.1f}%

---
_Use `/resume-agent` to continue_
""")

# End session with pause status
counter.end_session()
provider.end_session(f"Paused: {summary}")
```

### Step 6: Output Confirmation

```markdown
# Session Paused

**Session**: {session_id}
**Turn**: {turn_number}
**Duration**: {session_duration}

## State Saved
- Progress snapshot preserved
- In-progress tasks recorded
- Context state captured

## In Progress Tasks
{list of tasks with partial progress notes}

## Summary
{summary}

## To Resume
```bash
/resume-agent
```

## Note
All state has been saved. You can safely close this session.
The next `/resume-agent` will restore your exact context.
```

## Error Handling

### No State Provider
```
Fall back to file-only pause state
Warn user that external sync may be incomplete
```

### Save Failed
```
Retry 3 times
If persistent, output state to console for manual copy
Warn user to not close session
```

## Examples

### With Summary
```
/pause-agent --summary "Working on password reset, email template done"
```

### Interactive
```
/pause-agent
> Enter pause summary: Debugging auth flow, found issue in token validation
```

### Output Example
```markdown
# Session Paused

**Session**: 20240115-140000
**Turn**: 45
**Duration**: 2h 15m

## State Saved
- Progress snapshot preserved
- In-progress tasks recorded
- Context state captured

## In Progress Tasks
- TASK-018: Implement password reset (80% - email template done)

## Summary
Working on password reset, email template done

## To Resume
/resume-agent
```
