# Execution Modes Pattern

**Version:** 1.0.0
**Category:** Control Pattern
**Purpose:** Configure agent autonomy level with human checkpoints

---

## Overview

The Execution Modes Pattern provides configurable control over agent autonomy, allowing teams to balance speed with oversight. It enables agents to run continuously for well-defined tasks while pausing for human input on complex decisions.

### Key Insight

> Not all tasks need the same level of oversight.
> Match autonomy level to task risk and team confidence.

---

## Execution Modes

### 1. Autonomous Mode

**Behavior**: Agent runs continuously until completion or error.

**Best For**:
- Well-defined tasks with clear acceptance criteria
- Overnight or unattended builds
- Repetitive tasks with established patterns
- Teams with high confidence in agent capabilities

**Characteristics**:
- No human intervention required
- Stops only on error, completion, or configured limits
- Maximum velocity
- Requires comprehensive test coverage

```yaml
execution:
  mode: "autonomous"
  checkpoints:
    turn_interval: 0  # Disabled
    before_new_issue: false
    on_regression_failure: true  # Only stop on failures
```

### 2. Interactive Mode

**Behavior**: Agent pauses at configured checkpoints for human review.

**Best For**:
- New projects with evolving requirements
- Complex features requiring architectural decisions
- Teams learning to work with agents
- Tasks with uncertain scope

**Characteristics**:
- Human-in-the-loop at key points
- Balances velocity with oversight
- Prevents runaway implementations
- Enables course correction

```yaml
execution:
  mode: "interactive"
  checkpoints:
    turn_interval: 50  # Pause every 50 turns
    before_new_issue: true
    after_issue_complete: false
    on_regression_failure: true
    on_blocker: true
    on_uncertainty: true
```

### 3. Supervised Mode

**Behavior**: Agent pauses before every significant action.

**Best For**:
- Production systems with high risk
- Compliance-sensitive environments
- Training new team members
- Debugging agent behavior

**Characteristics**:
- Maximum human control
- Every destructive action requires approval
- Slowest but safest
- Audit trail for all decisions

```yaml
execution:
  mode: "supervised"
  checkpoints:
    turn_interval: 10
    before_new_issue: true
    after_issue_complete: true
    on_regression_failure: true
    on_blocker: true
    on_uncertainty: true
    before_file_delete: true
    before_git_push: true
    before_deploy: true
```

---

## Checkpoint Types

### Turn-Based Checkpoints

Pause after a fixed number of agent turns:

```yaml
checkpoints:
  turn_interval: 50  # Pause every 50 turns (0 = disabled)
```

**Use When**:
- Want regular check-ins regardless of progress
- Running long sessions unattended
- Preventing context bloat

### Task-Based Checkpoints

Pause at task boundaries:

```yaml
checkpoints:
  before_new_issue: true   # Pause before starting each task
  after_issue_complete: true  # Pause after completing
```

**Use When**:
- Want to approve each task before it starts
- Need to review completed work before continuing
- Tasks have varying complexity

### Event-Based Checkpoints

Pause when specific events occur:

```yaml
checkpoints:
  on_regression_failure: true  # Tests started failing
  on_blocker: true             # Agent reports being blocked
  on_uncertainty: true         # Agent confidence is low
```

**Use When**:
- Want automatic escalation on problems
- Agent should ask for help when stuck
- Quality gates are important

### Action-Based Checkpoints (Supervised Mode)

Pause before specific risky actions:

```yaml
checkpoints:
  before_file_delete: true  # Before rm/delete operations
  before_git_push: true     # Before pushing to remote
  before_deploy: true       # Before any deployment
  before_schema_change: true  # Before DB migrations
```

**Use When**:
- Actions are irreversible
- Production impact possible
- Compliance requires approval

---

## Checkpoint Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Checkpoint Decision Flow                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Agent Turn N                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                       │
│  │ Check: Turn     │──YES──► Checkpoint: "Turn limit"      │
│  │ interval?       │                    │                   │
│  └────────┬────────┘                    ▼                   │
│           │ NO                    Wait for approval         │
│           ▼                             │                   │
│  ┌─────────────────┐                    │                   │
│  │ Check: Starting │──YES──► Checkpoint: "New task"        │
│  │ new task?       │                    │                   │
│  └────────┬────────┘                    ▼                   │
│           │ NO                    Show task preview         │
│           ▼                             │                   │
│  ┌─────────────────┐                    │                   │
│  │ Check: Risky    │──YES──► Checkpoint: "Approval"        │
│  │ action?         │                    │                   │
│  └────────┬────────┘                    ▼                   │
│           │ NO                    Describe action           │
│           ▼                             │                   │
│  ┌─────────────────┐                    │                   │
│  │ Check: Event    │──YES──► Checkpoint: "Event"           │
│  │ triggered?      │                    │                   │
│  └────────┬────────┘                    ▼                   │
│           │ NO                    Show event details        │
│           ▼                             │                   │
│      Continue                           │                   │
│      to Turn N+1                        │                   │
│           ▲                             │                   │
│           │                             │                   │
│           └─────────────────────────────┘                   │
│                    (on approval)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Approval Interface

When a checkpoint triggers, the agent presents:

### CLI Interface

```
╔════════════════════════════════════════════════════════════╗
║                    CHECKPOINT TRIGGERED                     ║
╠════════════════════════════════════════════════════════════╣
║ Type: Turn Interval (Turn 50 of session)                   ║
║ Time: 2024-01-15T14:30:00Z                                 ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║ Progress Since Last Checkpoint:                            ║
║ - Completed: TASK-015 (User authentication)                ║
║ - In Progress: TASK-016 (Dashboard layout) - 60%           ║
║ - Tests: 45 passing, 0 failing                             ║
║                                                            ║
║ Context Usage: 45% (within limits)                         ║
║ Regression Status: PASSING ✓                               ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║ Options:                                                   ║
║   [c] Continue - Resume agent work                         ║
║   [p] Pause - Save state and stop session                  ║
║   [d] Details - Show more information                      ║
║   [r] Redirect - Give new instructions                     ║
║   [a] Abort - Stop immediately, preserve state             ║
║                                                            ║
║ Auto-continue in: 58:32 (timeout: 60 min)                  ║
╚════════════════════════════════════════════════════════════╝

>
```

### Notification Interface (Slack/Email)

```markdown
## 🔔 Checkpoint: Turn Interval

**Project**: auth-system
**Agent**: coding-agent-001
**Turn**: 50

### Progress
- ✅ TASK-015: User authentication
- 🔄 TASK-016: Dashboard layout (60%)

### Tests
45 passing, 0 failing

### Actions
- [Continue](approve-link) - Resume work
- [Pause](pause-link) - Stop session
- [Details](details-link) - More info

⏱️ Auto-continues in 60 minutes
```

---

## Configuration Reference

### Full Configuration

```yaml
execution:
  # Mode selection
  mode: "interactive"  # "autonomous", "interactive", "supervised"

  # Turn-based checkpoints
  checkpoints:
    turn_interval: 50  # 0 = disabled

    # Task-based
    before_new_issue: true
    after_issue_complete: false

    # Event-based
    on_regression_failure: true
    on_blocker: true
    on_uncertainty: true
    on_context_high: true  # Context > 80%

    # Action-based (supervised)
    before_file_delete: false
    before_git_push: false
    before_deploy: false
    before_schema_change: false

  # Approval settings
  approval:
    timeout_minutes: 60  # 0 = wait forever
    default_action: "pause"  # "pause", "continue", "abort"

    # Notification channels
    notification:
      cli: true  # Always show in terminal
      slack_webhook: "${SLACK_WEBHOOK_URL}"
      email: "team@example.com"
      linear_comment: true  # Comment on META issue

  # Safety limits
  limits:
    max_turns_per_session: 500
    max_files_modified: 50
    max_lines_changed: 5000
    context_warning_threshold: 0.7
    context_pause_threshold: 0.85
```

### Mode Presets

Quick presets for common scenarios:

```yaml
# Preset: overnight-build
execution:
  mode: "autonomous"
  checkpoints:
    on_regression_failure: true
  limits:
    max_turns_per_session: 1000

# Preset: pair-programming
execution:
  mode: "interactive"
  checkpoints:
    turn_interval: 20
    before_new_issue: true

# Preset: production-deploy
execution:
  mode: "supervised"
  checkpoints:
    before_git_push: true
    before_deploy: true
  approval:
    timeout_minutes: 0  # No auto-continue
```

---

## Implementation Integration

### With State Provider

```python
# Checkpoint manager queries state
progress = provider.get_progress_summary()
meta = provider.get_meta()

checkpoint_data = {
    "turn": current_turn,
    "progress": progress,
    "regression_status": meta.regression_status,
    "context_usage": get_context_usage()
}

# Record checkpoint in META
provider.add_session_comment(f"""
## Checkpoint: Turn {current_turn}
{checkpoint_summary}
""")
```

### With Session Continuity

Checkpoints persist across sessions:

```python
# On session end at checkpoint
provider.update_meta({
    "pending_checkpoint": {
        "type": "turn_interval",
        "turn": 50,
        "waiting_since": datetime.now().isoformat()
    }
})

# On session resume
meta = provider.get_meta()
if meta.pending_checkpoint:
    # Resume from checkpoint
    show_checkpoint(meta.pending_checkpoint)
```

---

## Best Practices

### Choosing a Mode

| Scenario | Recommended Mode |
|----------|------------------|
| New project, unfamiliar codebase | Supervised |
| Established project, routine tasks | Autonomous |
| Complex feature, many decisions | Interactive |
| Production deployment | Supervised |
| Bug fixes with tests | Autonomous |
| Architectural changes | Interactive/Supervised |

### Checkpoint Frequency

| Turn Interval | Best For |
|---------------|----------|
| 10-20 | Learning agent behavior, high risk |
| 50-100 | Standard interactive work |
| 200+ | Well-tested autonomous runs |
| 0 (disabled) | Maximum autonomy, trusted tasks |

### Timeout Settings

| Timeout | Best For |
|---------|----------|
| 0 (disabled) | Production approvals, compliance |
| 15-30 min | Active supervision |
| 60 min | Async team review |
| 240+ min | Overnight runs |

---

## Troubleshooting

### Checkpoints Too Frequent

```
Problem: Agent keeps stopping, slowing progress
Solution:
  - Increase turn_interval
  - Disable before_new_issue for routine tasks
  - Switch to autonomous mode
```

### Missing Important Checkpoints

```
Problem: Agent made changes that should have been reviewed
Solution:
  - Enable action-based checkpoints
  - Add on_uncertainty trigger
  - Lower turn_interval
```

### Approval Timeouts

```
Problem: Approvals timing out, work pausing unexpectedly
Solution:
  - Increase timeout_minutes
  - Set default_action to "continue" for low-risk
  - Add notification channels
```

---

## Version History

- **1.0.0** (2024-01-15): Initial execution modes pattern
