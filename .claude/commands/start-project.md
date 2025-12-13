---
description: Initialize a new autonomous development project with external state tracking
argument-hint: <requirements-file-or-description>
---

Initialize a new autonomous development project using the Session Continuity pattern.

## Arguments

- `$ARGUMENTS`: Path to requirements file OR inline project description

## Process

### Step 1: Validate Input

```
IF $ARGUMENTS is a file path:
  Read requirements from file
ELSE IF $ARGUMENTS is text:
  Use as inline requirements
ELSE:
  Ask user for requirements
```

### Step 2: Load Configuration

Read `.ai-agents/config.yml` for:
- `state_provider.type` (linear, github, file)
- `state_provider.api_key_env`
- `state_provider.team_id` / `repo`
- `session.continuity_enabled`

If no config exists, prompt user:
1. Which state provider to use?
2. API credentials (point to env var)
3. Project name

### Step 3: Check Existing State

```
IF .project_state.json exists:
  WARN: "Project already initialized"
  ASK: "Reinitialize? This will create new tasks (existing preserved)"
  IF no: EXIT
```

### Step 4: Parse Requirements

Extract from requirements document:

1. **Functional Requirements** → functional tasks
2. **UI/UX Requirements** → style tasks
3. **Technical Requirements** → infrastructure tasks
4. **Testing Requirements** → testing tasks

For each requirement, identify:
- Title (clear, actionable)
- Description (detailed)
- Acceptance Criteria (testable)
- Test Steps (verification)
- Priority (1-4)
- Category
- Dependencies

### Step 5: Initialize State Provider

```python
from scripts.state_providers import get_provider

provider = get_provider()
session_id = provider.start_session()
```

### Step 6: Create Tasks

For each parsed task:

```python
task_id = provider.create_task({
    "title": task.title,
    "description": task.description,
    "priority": task.priority,
    "category": task.category,
    "acceptance_criteria": task.acceptance_criteria,
    "test_steps": task.test_steps,
    "labels": task.labels
})
```

### Step 7: Create META Issue

The provider automatically creates META issue on first use.

Update META with initialization context:

```python
provider.update_meta({
    "current_focus": "Project initialization",
    "regression_status": "unknown",
    "notes": f"Initialized from: {requirements_source}"
})
```

### Step 8: Write Marker File

Create `.project_state.json`:

```json
{
  "project_id": "{generated_id}",
  "initialized_at": "{timestamp}",
  "state_provider": {
    "type": "{provider_type}",
    "team_id": "{team_id}",
    "project_id": "{project_id}",
    "meta_issue_id": "{meta_id}"
  },
  "requirements_source": "{file_or_inline}",
  "task_count": {count}
}
```

### Step 9: End Initialization Session

```python
provider.end_session(f"Project initialized with {task_count} tasks")
```

### Step 10: Output Summary

```markdown
# Project Initialized Successfully

**Project ID**: {id}
**State Provider**: {type}
**Tasks Created**: {count}

## Task Breakdown
| Category | Count | P1 | P2 | P3 | P4 |
|----------|-------|----|----|----|----|
| Functional | X | X | X | X | X |
| Style | X | X | X | X | X |
| Infrastructure | X | X | X | X | X |
| Testing | X | X | X | X | X |

## META Issue
URL: {meta_issue_url}

## Next Steps
1. Review created tasks in {provider}
2. Run `/continue-project` to start development
3. Tasks will be picked up by priority order

## Quick Start
```bash
# Continue in new session
/continue-project
```
```

## Error Handling

### No Config File
```
Create minimal config:
state_provider:
  type: "file"

Or prompt for Linear/GitHub setup
```

### API Connection Failed
```
1. Verify API key in environment
2. Check network connectivity
3. Fall back to file provider if user agrees
```

### Requirements Parsing Failed
```
1. Show parsing errors
2. Offer manual task creation mode
3. Create partial tasks for valid entries
```

## Examples

### From Requirements File
```
/start-project requirements.md
```

### Inline Requirements
```
/start-project "Build a user authentication system with login, signup, password reset, and session management"
```

### With Specific Provider
```
# In .ai-agents/config.yml
state_provider:
  type: "linear"
  api_key_env: "LINEAR_API_KEY"

/start-project requirements.md
```
