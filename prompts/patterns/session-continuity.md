# Session Continuity Pattern

**Version:** 1.0.0
**Category:** Architectural Pattern
**Purpose:** Enable unlimited session continuity for autonomous agents

---

## Overview

The Session Continuity Pattern enables AI agents to work on long-running projects across multiple sessions by using external systems as distributed memory. This pattern addresses the fundamental limitation of context windows by storing all critical state outside the agent's context.

### Key Insight

> Context windows are temporary. External systems are persistent.
> Use external state as the source of truth, not internal memory.

---

## Problem Statement

AI agents face several challenges with long-running tasks:

1. **Context Window Limits**: Conversations eventually exceed token limits
2. **Session Boundaries**: Work stops when sessions end
3. **Knowledge Loss**: Important context is lost between sessions
4. **State Inconsistency**: Local files may become stale or corrupted
5. **Human Visibility**: Progress is opaque to human supervisors

---

## Solution: Two-Phase Architecture

### Phase 1: Initializer

The Initializer Agent runs first to:
- Parse requirements into structured tasks
- Create tasks in external tracker (Linear, GitHub, etc.)
- Establish META issue for cross-session knowledge
- Write marker file for quick detection

### Phase 2: Coding Agent(s)

Coding Agents run with fresh contexts and:
- Query external tracker for current state
- Work on tasks independently
- Update external state as they progress
- Hand off cleanly when sessions end

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Continuity Flow                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Session 1              Session 2              Session N    │
│  ┌─────────┐           ┌─────────┐           ┌─────────┐   │
│  │ Init    │           │ Coding  │           │ Coding  │   │
│  │ Agent   │           │ Agent   │           │ Agent   │   │
│  └────┬────┘           └────┬────┘           └────┬────┘   │
│       │                     │                     │         │
│       ▼                     ▼                     ▼         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              External State Provider                 │   │
│  │  (Linear / GitHub Issues / Notion / File)           │   │
│  │                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │   │
│  │  │  Tasks   │  │  META    │  │  Session Logs    │  │   │
│  │  │  (Todo,  │  │  Issue   │  │  (Handoff notes, │  │   │
│  │  │  Done)   │  │          │  │   decisions)     │  │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Components

### 1. Marker File Pattern

Create `.project_state.json` in project root:

```json
{
  "project_id": "proj-abc123",
  "initialized_at": "2024-01-15T10:00:00Z",
  "state_provider": {
    "type": "linear",
    "team_id": "TEAM_ID",
    "project_id": "PROJECT_ID",
    "meta_issue_id": "ISSUE_ID"
  },
  "last_session": {
    "id": "20240115-103000",
    "ended_at": "2024-01-15T12:30:00Z",
    "tasks_completed": 3
  }
}
```

**Purpose**: Fast initialization detection without API calls.

### 2. META Issue Pattern

A dedicated issue/document that tracks:

```markdown
# [META] Project State Tracker

## Architecture Decisions
- 2024-01-15: Using React for frontend (rationale: team familiarity)
- 2024-01-15: PostgreSQL for database (rationale: relational needs)

## Known Issues
- API rate limiting on external service
- Mobile layout needs work

## Regression Status
**Status**: PASSING ✓
Last run: 2024-01-15T14:00:00Z

## Session History
See comments below for session logs.
```

**Session comments** are added to META issue:

```markdown
## Session #5 Start
Time: 2024-01-15T14:00:00Z
State: Todo=5, In Progress=2, Done=12

## Session #5 End
Time: 2024-01-15T16:30:00Z
Completed: TASK-015, TASK-016
In Progress: TASK-017 (80% done)
Notes: Auth flow complete, starting on dashboard
```

### 3. Task Structure

Tasks in external system include:

```yaml
title: "Implement user authentication"
description: |
  Add JWT-based authentication to the API.

  ## Acceptance Criteria
  - [ ] Login endpoint returns JWT token
  - [ ] Token validates on protected routes
  - [ ] Refresh token mechanism works
  - [ ] Invalid credentials return 401

  ## Test Steps
  1. POST /auth/login with valid credentials
  2. Verify JWT token in response
  3. Use token on GET /api/protected
  4. Verify 200 response

priority: 2  # High
category: functional
labels: [auth, backend, security]
```

### 4. Session Lifecycle

```
Session Start:
├── Check .project_state.json exists?
│   ├── YES: Load state from provider
│   │        Query current tasks
│   │        Load META issue context
│   │        Record session start
│   │
│   └── NO:  Run Initializer Agent
│            Parse requirements
│            Create tasks
│            Create META issue
│            Write marker file

Session Work:
├── Pick highest priority Todo task
├── Update task to In Progress
├── Implement per acceptance criteria
├── Run tests per test steps
├── Update task to Done
├── Repeat until session ends

Session End:
├── Record session summary in META
├── Document any blockers
├── Update marker file
├── Clean handoff for next session
```

---

## Recovery Scenarios

### Scenario 1: Normal Continuation

```
Agent: "Checking project state..."
Agent: "Found .project_state.json"
Agent: "Loading from Linear..."
Agent: "Session #6 starting"
Agent: "Current state: 3 Todo, 1 In Progress, 15 Done"
Agent: "Continuing TASK-020 (was 60% complete)"
```

### Scenario 2: Partial Context Loss

```
Agent: "Checking project state..."
Agent: "Found .project_state.json"
Agent: "Loading from Linear..."
Agent: "Warning: TASK-018 marked In Progress but no recent activity"
Agent: "Reviewing TASK-018 acceptance criteria..."
Agent: "2 of 4 criteria checked - resuming from criterion 3"
```

### Scenario 3: Regression Failure

```
Agent: "Checking project state..."
Agent: "Loading from Linear..."
Agent: "META shows regression status: FAILING"
Agent: "Priority: Fix regression before new features"
Agent: "Running regression suite..."
Agent: "Found: TASK-015 broke test_auth_flow"
Agent: "Creating bugfix task..."
```

### Scenario 4: Fresh Project

```
Agent: "Checking project state..."
Agent: "No .project_state.json found"
Agent: "This appears to be a new project"
Agent: "Running initialization..."
Agent: "Parsing requirements.md..."
Agent: "Created 15 tasks in Linear"
Agent: "META issue created: PROJ-META"
Agent: "Ready for development"
```

---

## Best Practices

### DO:

1. **Always check external state first**
   - Never assume local state is current
   - Query provider on session start

2. **Record decisions in META**
   - Architecture choices
   - Technology selections
   - Important constraints

3. **Use acceptance criteria as checkpoints**
   - Check off completed criteria
   - Resume from last unchecked

4. **Maintain regression status**
   - Run tests before new work
   - Update META with results

5. **Clean handoffs**
   - Document partial progress
   - Note blockers and dependencies
   - Suggest next actions

### DON'T:

1. **Don't rely on conversation history**
   - Context will be lost
   - External state is truth

2. **Don't skip META updates**
   - Future sessions need context
   - Human supervisors need visibility

3. **Don't leave tasks In Progress indefinitely**
   - Either complete or document status
   - Stale tasks create confusion

4. **Don't modify issue descriptions**
   - Original requirements are immutable
   - Add comments for updates

5. **Don't ignore regression failures**
   - Fix before new features
   - Cascading bugs are expensive

---

## Configuration

In `.ai-agents/config.yml`:

```yaml
session:
  # Enable session continuity features
  continuity_enabled: true

  # Use META issue for cross-session knowledge
  meta_issue_enabled: true

  # Require regression tests before new work
  regression_testing: "required"  # "required", "recommended", "disabled"

  # Session timeout (auto-end if no activity)
  timeout_minutes: 120

  # Maximum session duration
  max_duration_minutes: 480

state_provider:
  type: "linear"  # "linear", "github", "notion", "file"
  api_key_env: "LINEAR_API_KEY"
  team_id: "YOUR_TEAM_ID"
  project_name: "AI Development Project"
  meta_issue_label: "meta"
```

---

## Integration with Execution Modes

Session continuity works with all execution modes:

| Mode | Session Handling |
|------|------------------|
| Autonomous | Sessions run unattended, state persists |
| Interactive | Checkpoints may span sessions |
| Supervised | Human approval persists across sessions |

When a checkpoint occurs at session boundary:

```
Session N ends with checkpoint pending
→ State saved to external provider
→ Checkpoint status recorded

Session N+1 starts
→ State loaded from provider
→ Checkpoint status detected
→ Resume from checkpoint (human approval may still be pending)
```

---

## Metrics and Monitoring

Track these metrics for session health:

| Metric | Target | Alert If |
|--------|--------|----------|
| Session duration | 2-4 hours | > 6 hours (context bloat) |
| Tasks per session | 2-5 | 0 (stuck) or > 10 (rushing) |
| Handoff quality | Complete | Missing notes or unclear state |
| Regression status | Passing | Failing or Unknown |
| META freshness | < 1 hour | > 4 hours since update |

---

## Version History

- **1.0.0** (2024-01-15): Initial session continuity pattern
