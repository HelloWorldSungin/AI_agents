# Autonomous Runner

A fully autonomous execution system for AI development tasks using Claude Code CLI.

## Overview

The autonomous runner executes development tasks without human intervention by:

1. **Fetching tasks** from a state provider (Linear, GitHub, or file-based)
2. **Executing tasks** using Claude Code CLI (uses your subscription - no extra API costs!)
3. **Updating status** based on results (done, blocked, in-progress)
4. **Respecting checkpoints** for safety control
5. **Tracking progress** with notifications and logging

## Quick Start

### Prerequisites

1. **Claude Code CLI installed** (comes with your Claude Code subscription):
   ```bash
   # Verify installation
   claude --version
   ```

2. Create a configuration file at `.ai-agents/config.yml`:
   ```yaml
   state_provider:
     type: "file"

   autonomous:
     backend: "claude-code"  # Uses your subscription!
     model: "opus"
     max_tasks_per_session: 10

   execution:
     mode: "autonomous"
   ```

### Alternative: Anthropic SDK Backend

If you prefer to use the Anthropic API directly (incurs usage costs):

```bash
pip install anthropic
export ANTHROPIC_API_KEY='your-api-key'
```

```yaml
autonomous:
  backend: "anthropic-sdk"  # Uses API credits
  model: "claude-opus-4-20250514"
  cost_limit_per_session: 10.0
```

### Running

```bash
# Start the runner
python -m scripts.autonomous start

# Check status
python -m scripts.autonomous status

# Stop gracefully
python -m scripts.autonomous stop

# View logs
python -m scripts.autonomous logs

# Validate configuration
python -m scripts.autonomous config
```

## Configuration

The runner is configured via `.ai-agents/config.yml`. See `config.yml` in this directory for a complete example with all options.

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `autonomous.backend` | `claude-code` (subscription) or `anthropic-sdk` (API) | `claude-code` |
| `autonomous.model` | Model to use (`opus`, `sonnet`, `haiku` for claude-code) | `opus` |
| `autonomous.max_tokens` | Max tokens per response | `8192` |
| `autonomous.max_turns_per_task` | Max turns per task | `50` |
| `autonomous.max_tasks_per_session` | Max tasks before stopping | `10` |
| `autonomous.cost_limit_per_session` | USD limit (anthropic-sdk only) | `10.0` |
| `autonomous.rate_limit_rpm` | Requests per minute | `50` |
| `execution.mode` | `autonomous`, `interactive`, `supervised` | `autonomous` |
| `execution.checkpoints.turn_interval` | Turns between checkpoints | `25` |

### State Providers

#### Linear (Recommended for Teams)

```yaml
state_provider:
  type: "linear"
  api_key_env: "LINEAR_API_KEY"
  team_id: "your-team-id"  # Optional, auto-detected
  project_name: "My Project"
```

#### GitHub Issues

```yaml
state_provider:
  type: "github"
  api_key_env: "GITHUB_TOKEN"
  repo: "owner/repo"
```

#### File-based (Local Development)

```yaml
state_provider:
  type: "file"
  state_dir: ".ai-agents/state"
```

## Architecture

```
                          ┌─────────────────┐
                          │  State Provider │
                          │ (Linear/GitHub) │
                          └────────┬────────┘
                                   │
                                   │ Tasks
                                   ▼
┌─────────────────────────────────────────────────────────┐
│                   Autonomous Runner                      │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │ Task Queue  │──▶│ Claude API   │──▶│ Result      │ │
│  │             │   │ (Anthropic)  │   │ Handler     │ │
│  └─────────────┘   └──────────────┘   └─────────────┘ │
│                           │                            │
│         ┌─────────────────┼─────────────────┐         │
│         ▼                 ▼                 ▼         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ │
│  │ Checkpoint  │   │ Progress    │   │ Turn        │ │
│  │ Manager     │   │ Tracker     │   │ Counter     │ │
│  └─────────────┘   └─────────────┘   └─────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Output    │
                   │ (Logs/Slack)│
                   └─────────────┘
```

## Execution Flow

1. **Start Session**: Initialize provider, load state, start tracking
2. **Get Next Task**: Fetch highest-priority TODO task
3. **Execute Task**:
   - Build task prompt from description and criteria
   - Call Claude API with system prompt
   - Parse response for completion/blocker signals
   - Continue conversation if needed
4. **Update Status**: Mark task done, blocked, or keep in-progress
5. **Check Limits**: Cost, tasks, turns
6. **Repeat** until no tasks or limits reached

## Checkpoints

Checkpoints pause execution for human review:

- **Turn Interval**: Every N turns (e.g., every 25)
- **Regression Failure**: When tests fail
- **Blocker Detected**: When agent reports being stuck
- **Context High**: When context usage exceeds threshold

In **autonomous mode**, only critical checkpoints (failures, high context) trigger.

## Safety Features

- **Turn Limits**: Maximum turns per task prevents infinite loops
- **Task Limits**: Maximum tasks per session
- **Rate Limiting**: Respect request frequency limits
- **Graceful Shutdown**: Signal handlers for clean exit
- **State Persistence**: Resume from where you left off
- **Cost Limits**: Stop when cost exceeds limit (anthropic-sdk backend only)

**Note:** When using `claude-code` backend, you're using your Claude Code subscription - no per-request API costs!

## Monitoring

### CLI Status

```bash
python -m scripts.autonomous status
```

Shows:
- Runner state (running, paused, stopped)
- Tasks completed
- Total cost
- Progress metrics
- Recent events

### Slack Notifications

Configure Slack webhook for real-time updates:

```yaml
progress:
  slack_webhook: "https://hooks.slack.com/services/..."
  notification_interval: 300  # Every 5 minutes
  notify_on_complete: true
  notify_on_blocked: true
```

### Log Files

```bash
# View recent logs
python -m scripts.autonomous logs --tail 100

# Full logs at:
cat .ai-agents/logs/autonomous.log
```

## Task Format

Tasks should include:

- **Title**: Short description
- **Description**: Detailed requirements
- **Acceptance Criteria**: Checklist of requirements
- **Test Steps**: How to verify completion

Example from Linear:

```markdown
# Title: Add user authentication endpoint

## Description
Implement POST /api/auth/login endpoint with JWT token generation.

## Acceptance Criteria
- [ ] Endpoint accepts username and password
- [ ] Returns JWT token on success
- [ ] Returns 401 on invalid credentials
- [ ] Rate limited to 5 attempts per minute

## Test Steps
1. Send valid credentials, expect 200 with token
2. Send invalid credentials, expect 401
3. Send 6 requests in 1 minute, expect 429
```

## Programmatic Usage

```python
from scripts.autonomous.runner import AutonomousRunner, RunnerConfig

# Create config
config = RunnerConfig(
    model="claude-opus-4-20250514",
    max_tasks_per_session=5,
    cost_limit_per_session=5.0
)

# Create and run
runner = AutonomousRunner(config)
runner.start()

# Or resume from previous session
runner.start(resume=True)

# Check status
status = runner.get_status()
print(f"State: {status['state']}")
print(f"Tasks: {status['tasks_completed']}")
print(f"Cost: {status['total_cost']}")
```

## Troubleshooting

### "Claude Code CLI not found"

Ensure Claude Code is installed and in your PATH:
```bash
claude --version
```

If not installed, get it from: https://claude.ai/code

### "API key not found" (anthropic-sdk backend only)

Set the `ANTHROPIC_API_KEY` environment variable:
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "Could not initialize state provider"

Check your state provider configuration. For Linear:
```bash
export LINEAR_API_KEY='lin_api_...'
```

### Tasks not completing

- Check task has clear acceptance criteria
- Increase `max_turns_per_task`
- Review logs for blockers

### "Cost limit reached" (anthropic-sdk backend only)

Increase `cost_limit_per_session` in config or start a new session.

**Tip:** Use `claude-code` backend to avoid per-request costs!

## See Also

- [State Providers](../state_providers/README.md)
- [Execution Control](../execution/README.md)
- [Progress Tracking](../progress/README.md)
- [CHEAT_SHEET](../../docs/reference/CHEAT_SHEET/)
