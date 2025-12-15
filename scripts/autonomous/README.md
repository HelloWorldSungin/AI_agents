# Autonomous Runner (Two-Agent Pattern)

A fully autonomous execution system for AI development tasks using Claude Code CLI, implementing Anthropic's recommended **two-agent pattern** for optimal context window management.

## Overview

The autonomous runner implements the two-agent pattern:

1. **Initializer Agent (Phase 1)** - Analyzes requirements and creates structured tasks
2. **Coding Agent (Phase 2)** - Executes tasks with fresh context per task

This separation ensures optimal context window usage:
- Initializer uses full context for planning/decomposition
- Each coding session starts fresh, maximizing working memory
- Communication happens via external state provider (Linear, GitHub, File)

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIALIZER AGENT                         │
│  (Session 1 - Fresh Context)                                │
│                                                             │
│  1. Read requirements/spec file                             │
│  2. Analyze and break down into tasks                       │
│  3. Create tasks in state provider (Linear/GitHub/File)     │
│  4. Create META tracking task                               │
│  5. Write .project_state.json marker                        │
│  6. Exit (context discarded)                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CODING AGENT(S)                           │
│  (Sessions 2+ - Fresh Context Each)                         │
│                                                             │
│  1. Query state provider for next TODO task                 │
│  2. Claim task (status → In Progress)                       │
│  3. Implement with FRESH context                            │
│  4. Test/verify                                             │
│  5. Update status + add implementation notes                │
│  6. Exit (context discarded, next agent starts fresh)       │
└─────────────────────────────────────────────────────────────┘
```

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

### Phase 1: Initialize Project

```bash
# Create tasks from a requirements/spec file
python -m scripts.autonomous init --spec requirements.md

# With custom project name
python -m scripts.autonomous init --spec spec.md --project-name "My App"

# Force re-initialization
python -m scripts.autonomous init --spec requirements.md --force
```

**What happens:**
1. Claude analyzes your spec file
2. Creates structured tasks in state provider
3. Creates META tracking task
4. Writes `.project_state.json` marker

### Phase 2: Run Coding Agent

```bash
# Start the coding agent
python -m scripts.autonomous start

# Resume from previous session
python -m scripts.autonomous start --resume
```

**What happens:**
1. Fetches next TODO task from provider
2. Claims task (status → In Progress)
3. Implements with full fresh context
4. Tests and verifies
5. Updates status and continues

### Other Commands

```bash
# Show session recovery context
python -m scripts.autonomous resume

# Check status
python -m scripts.autonomous status

# View tasks
python -m scripts.autonomous tasks

# Stop gracefully
python -m scripts.autonomous stop

# View logs
python -m scripts.autonomous logs --tail 100

# Validate configuration
python -m scripts.autonomous config
```

## Alternative: Anthropic SDK Backend

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

## Claude Code SDK Backend (Recommended for Production)

For real-time streaming, tool visibility, and Linear MCP integration, use the SDK-based runner:

### Installation

```bash
pip install claude-code-sdk>=0.0.25
```

Verify installation:
```bash
python -c "from claude_code_sdk import ClaudeCodeOptions; print('✓ SDK ready')"
```

### Benefits over CLI Backend

| Feature | CLI Backend | SDK Backend |
|---------|-------------|-------------|
| **Streaming** | ❌ Blocking subprocess | ✅ Real-time async streaming |
| **Progress Updates** | ❌ Batch at end | ✅ Posted as they happen |
| **Tool Visibility** | ❌ Silent execution | ✅ Real-time tool use logs |
| **Error Messages** | ❌ Basic (`error=None`) | ✅ Detailed with context |
| **Linear Integration** | ❌ Separate API calls | ✅ Direct MCP access |
| **Performance** | ❌ 30min timeout risk | ✅ No blocking wait |
| **Debugging** | ❌ Post-mortem only | ✅ Real-time visibility |
| **Failure Handling** | ⚠️ Continues to next task | ✅ Stops immediately |

### Configuration

```yaml
autonomous:
  backend: "claude-code-sdk"  # New SDK backend
  model: "claude-opus-4-5-20251101"
  max_turns_per_task: 150  # Increased for complex tasks
  oauth_token_env: "CLAUDE_CODE_OAUTH_TOKEN"
  linear_api_key_env: "LINEAR_API_KEY"
  project_dir: "/path/to/project"
```

### CRITICAL: allowed_tools Configuration

**IMPORTANT:** When using the Claude Code SDK, you MUST explicitly configure `allowed_tools` or the Write tool will not create files.

The SDK runner automatically configures this:
```python
ClaudeCodeOptions(
    model="claude-opus-4-5-20251101",
    system_prompt=system_prompt,
    max_turns=150,
    cwd="/path/to/project",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash", "TodoWrite"],  # Required!
    mcp_servers=mcp_servers
)
```

Without this parameter, Claude will attempt Write operations but files will not be created.

### Usage

#### Python (Async)
```python
import asyncio
from scripts.autonomous.runner_sdk import AutonomousRunnerSDK, RunnerConfig

async def main():
    config = RunnerConfig.from_yaml(".ai-agents/config.yml")
    runner = AutonomousRunnerSDK(config)
    await runner.start()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Command Line
```bash
# Start SDK runner
python -m scripts.autonomous.runner_sdk

# Or use the CLI wrapper (if available)
python -m scripts.autonomous start --runner sdk
```

### Stop-on-Failure Pattern

The SDK runner implements a **stop-on-failure pattern** to prevent cascading failures:

```python
if result.success:
    tasks_completed += 1
    self.logger.info(f"Task {task.id} completed successfully")
else:
    # CRITICAL: Stop on failure
    self.logger.error(f"Task {task.id} failed: {result.error}")
    self.logger.error("Stopping runner - cannot proceed with failed task")
    self.state = RunnerState.ERROR
    break  # Exit loop immediately
```

**Why this matters:**
- Prevents dependent tasks from running when prerequisites fail
- Example: If "[PROJECT-1.2] Create callback" fails, don't attempt "[PROJECT-1.3] Add metrics to callback"
- Ensures data integrity and prevents wasted compute on doomed tasks

### Troubleshooting

See [SDK_TROUBLESHOOTING.md](./SDK_TROUBLESHOOTING.md) for common issues and solutions.

### Reference Implementation

For complete details and best practices:
- [Claude SDK Migration Guide](../../.ai-agents/library/guides/claude-sdk-migration.md)
- [Reference Implementation](https://github.com/coleam00/Linear-Coding-Agent-Harness)

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
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Initializer Agent  │  │  Coding Agent   │  │  Coding Agent   │
│    (Session 1)      │  │   (Session 2)   │  │   (Session 3)   │
│                     │  │                 │  │                 │
│  - Parse spec       │  │  - Get task     │  │  - Get task     │
│  - Create tasks     │  │  - Implement    │  │  - Implement    │
│  - Setup META       │  │  - Test         │  │  - Test         │
│  - Write marker     │  │  - Update       │  │  - Update       │
└─────────────────────┘  └─────────────────┘  └─────────────────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  .project_state │
                          │      .json      │
                          └─────────────────┘
```

## Execution Flow

### Initializer Agent (Phase 1)

1. **Parse Requirements**: Read spec/requirements file
2. **Analyze**: Use Claude to break down into tasks
3. **Create Tasks**: Create structured tasks in state provider
4. **Setup META**: Create tracking issue for coordination
5. **Write Marker**: Write `.project_state.json` for detection

### Coding Agent (Phase 2)

1. **Start Session**: Initialize provider, load state, start tracking
2. **Get Next Task**: Fetch next task using phase-aware sorting (see below)
3. **Execute Task**:
   - Build task prompt from description and criteria
   - Call Claude with system prompt
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

## Task Execution Order

The coding agent uses **phase-aware sorting** to determine task execution order. This ensures tasks run in the correct sequence, respecting phases and dependencies.

### Supported Title Patterns

| Pattern | Example | Sort Key |
|---------|---------|----------|
| META tasks | `META: Project Tracker` | Always first (phase 0) |
| `[PREFIX-X.Y]` | `[AUTH-1.2] Implement login` | phase=1, task=2 |
| `X.Y:` at start | `1.2: Setup database` | phase=1, task=2 |
| `Phase X.Y` | `Phase 2.1 - Add tests` | phase=2, task=1 |
| `Task X.Y` | `Task 1.5 API endpoints` | phase=1, task=5 |
| Linear-style ID | `ARK-123` | sorted by ID number |
| Other | `Fix bug in login` | priority only |

### Sort Priority

Tasks are sorted by: `(phase, task_number, priority)`

1. **Phase number** - Lower phases run first (Phase 1 before Phase 2)
2. **Task number** - Within a phase, lower task numbers run first (1.1 before 1.2)
3. **Priority** - If phase/task are equal, higher priority tasks run first

### Example Execution Order

Given these tasks:
```
[AUTH-2.1] Add password reset     (Priority: HIGH)
[AUTH-1.3] Validate login form    (Priority: NORMAL)
[AUTH-1.1] Create login endpoint  (Priority: HIGH)
META: Authentication Project      (Priority: LOW)
[AUTH-1.2] Add session handling   (Priority: HIGH)
```

Execution order:
1. `META: Authentication Project` (phase 0)
2. `[AUTH-1.1] Create login endpoint` (phase 1, task 1)
3. `[AUTH-1.2] Add session handling` (phase 1, task 2)
4. `[AUTH-1.3] Validate login form` (phase 1, task 3)
5. `[AUTH-2.1] Add password reset` (phase 2, task 1)

### Cross-Phase Dependency Checking

The runner enforces **strict dependency ordering**:

1. **Earlier phases block later phases** - Phase 2 tasks won't start until ALL Phase 1 tasks are DONE
2. **Earlier tasks block later tasks** - Task 1.3 won't start until 1.1 and 1.2 are DONE
3. **Blocked tasks are logged** - Runner logs which tasks are blocking

Example scenario:
```
[AUTH-1.1] DONE
[AUTH-1.2] IN_PROGRESS
[AUTH-1.3] TODO
[AUTH-2.1] TODO
```

Runner behavior:
- `[AUTH-1.3]` is blocked by `[AUTH-1.2]` (same phase, earlier task not done)
- `[AUTH-2.1]` is blocked by `[AUTH-1.2]` and `[AUTH-1.3]` (earlier phase not complete)
- Logs: `Skipping AUTH-2.1 - blocked by: AUTH-1.2 (in_progress), AUTH-1.3 (todo)`

### Best Practices for Task Titles

Use consistent naming in your spec file:
```markdown
## Phase 1: Core Authentication
- [AUTH-1.1] Create user model and database schema
- [AUTH-1.2] Implement login endpoint
- [AUTH-1.3] Add JWT token generation

## Phase 2: Enhanced Features
- [AUTH-2.1] Add password reset flow
- [AUTH-2.2] Implement email verification
```

The initializer agent will preserve these patterns when creating tasks.

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

Example from spec file:

```markdown
# Requirements

## User Authentication

The system should support user authentication with:
- Login with email/password
- Password reset via email
- Session management with JWT
- Rate limiting on login attempts

## Dashboard

Users should see a dashboard with:
- Overview metrics
- Recent activity
- Quick actions
```

The initializer will parse this into structured tasks.

## Programmatic Usage

```python
from scripts.autonomous import ProjectInitializer, AutonomousRunner
from scripts.autonomous import InitializerConfig, RunnerConfig

# Phase 1: Initialize
init_config = InitializerConfig(
    model="claude-opus-4-20250514",
    backend="claude-code"
)
initializer = ProjectInitializer(init_config)
result = initializer.initialize("requirements.md", project_name="My App")

print(f"Created {result.tasks_created} tasks")

# Phase 2: Execute
runner_config = RunnerConfig(
    model="claude-opus-4-20250514",
    max_tasks_per_session=5
)
runner = AutonomousRunner(runner_config)
runner.start()

# Check status
status = runner.get_status()
print(f"State: {status['state']}")
print(f"Tasks: {status['tasks_completed']}")
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

### No tasks being parsed

- Ensure your spec file has clear, structured requirements
- Check the raw analysis output for debugging
- Try simplifying the spec structure

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
- [Linear-Coding-Agent-Harness](https://github.com/coleam00/Linear-Coding-Agent-Harness) - Reference implementation
