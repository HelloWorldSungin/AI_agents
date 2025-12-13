---
description: Continue an existing autonomous development project from last session
argument-hint: [--status-only]
---

Continue working on an initialized project by recovering state from the external provider.

## Arguments

- `--status-only`: Only show current status, don't start a new session

## Process

### Step 1: Check Initialization

```
IF .project_state.json does NOT exist:
  ERROR: "Project not initialized"
  SUGGEST: "Run /start-project first"
  EXIT
```

### Step 2: Load Project State

Read `.project_state.json`:

```python
with open('.project_state.json') as f:
    project_state = json.load(f)

provider_type = project_state['state_provider']['type']
project_id = project_state['project_id']
```

### Step 3: Connect to State Provider

```python
from scripts.state_providers import get_provider

provider = get_provider()
```

### Step 4: Query Current State

```python
# Get all tasks
all_tasks = provider.get_tasks()

# Categorize
todo = [t for t in all_tasks if t.status == TaskStatus.TODO]
in_progress = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
blocked = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]
done = [t for t in all_tasks if t.status == TaskStatus.DONE]

# Get META context
meta = provider.get_meta()

# Get progress summary
progress = provider.get_progress_summary()
```

### Step 5: Check Regression Status

```python
regression_status = meta.regression_status

if regression_status == "failing":
    WARN: "Regression tests are FAILING"
    RECOMMEND: "Fix regression before new features"
elif regression_status == "unknown":
    RECOMMEND: "Run regression tests first"
```

### Step 6: If --status-only, Output and Exit

```markdown
# Project Status

**Project ID**: {project_id}
**Provider**: {provider_type}
**Sessions**: {meta.total_sessions}

## Progress
| Status | Count |
|--------|-------|
| Todo | {count} |
| In Progress | {count} |
| Blocked | {count} |
| Done | {count} |

**Completion**: {progress.completion_rate}%

## Regression Status
{regression_status} {emoji}

## In Progress Tasks
{list with task IDs and titles}

## Blocked Tasks
{list with blockers}

## Next Up (Priority Order)
{top 5 todo tasks}
```

### Step 7: Start New Session

```python
session_id = provider.start_session()
```

### Step 8: Provide Context Summary

Output context for coding work:

```markdown
# Session #{session_number} Started

**Project**: {project_id}
**Time**: {timestamp}

## Current State
- **Todo**: {count}
- **In Progress**: {count}
- **Blocked**: {count}
- **Done**: {count}
- **Completion**: {percentage}%

## Regression Status
{status} - {recommendation if not passing}

## In Progress Tasks
{For each in-progress task:}
### {task_id}: {title}
**Priority**: P{priority}
**Category**: {category}

**Acceptance Criteria**:
{list with checkboxes}

**Progress Notes**:
{any comments/notes from last session}

---

## Recommended Next Actions

{If regression failing:}
1. **Fix Regression** - Tests failing, fix before new work

{If tasks in progress:}
1. **Continue {task_id}** - {title} (was in progress)

{If blocked tasks:}
1. **Unblock {task_id}** - {blocker description}

{Otherwise:}
1. **Start {highest_priority_todo}** - {title}

## Session Guidelines
- Update task status as you work
- Check off acceptance criteria as completed
- Record blockers immediately
- Run tests after each task
- End session with `/end-session` or clean handoff
```

### Step 9: Update Marker File

```python
project_state['last_session'] = {
    'id': session_id,
    'started_at': datetime.now().isoformat(),
    'initial_state': progress
}

with open('.project_state.json', 'w') as f:
    json.dump(project_state, f, indent=2)
```

## Recovery Scenarios

### Stale In-Progress Tasks

If task has been in_progress for >24 hours with no updates:

```
WARN: "{task_id} has been in progress for {duration}"
ASK: "Review and update status?"
OPTIONS:
  1. Continue working on it
  2. Move back to Todo
  3. Mark as Blocked
```

### Missing META Issue

If META issue can't be found:

```
WARN: "META issue not found in {provider}"
OPTIONS:
  1. Create new META issue (loses history)
  2. Search for META issue manually
  3. Continue without META (reduced context)
```

### Provider Connection Failed

```
ERROR: "Could not connect to {provider}"
CHECK: "API key in ${api_key_env}?"
OPTIONS:
  1. Retry connection
  2. Switch to file provider (offline mode)
  3. Show cached state from marker file
```

## Integration with Execution Modes

### Autonomous Mode
```
/continue-project
→ Automatically picks up next task
→ Works until completion or error
→ Handles session transitions
```

### Interactive Mode
```
/continue-project
→ Shows context and recommendations
→ Waits for user to select task
→ Pauses at checkpoints
```

### Supervised Mode
```
/continue-project
→ Shows detailed state
→ Requires approval for each task start
→ Human reviews each completion
```

## Examples

### Standard Continue
```
/continue-project
```

### Status Check Only
```
/continue-project --status-only
```

### Output Example

```markdown
# Session #7 Started

**Project**: auth-system
**Time**: 2024-01-15T14:00:00Z

## Current State
- **Todo**: 5
- **In Progress**: 1
- **Blocked**: 0
- **Done**: 12

**Completion**: 66%

## Regression Status
PASSING ✓

## In Progress Tasks

### TASK-018: Implement password reset flow
**Priority**: P2
**Category**: functional

**Acceptance Criteria**:
- [x] Reset request sends email
- [x] Reset link valid for 24 hours
- [ ] New password validation
- [ ] Success confirmation page

**Progress Notes**:
"Email sending and link generation complete. Need to finish validation and UI."

---

## Recommended Next Actions

1. **Continue TASK-018** - Password reset flow (80% complete)
2. **Next: TASK-019** - Session management (P2)
3. **Next: TASK-020** - Rate limiting (P3)
```
