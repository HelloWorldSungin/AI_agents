# Scripts & Tools

Automation scripts, starter templates, and development tools.

**Version:** 1.5.0
**Last Updated:** 2025-12-14

---

## Core Scripts

Essential scripts for agent composition and project setup.

| Script | Purpose | Location |
|--------|---------|----------|
| `compose-agent.py` | Compose agents from components (base + platform + context + skills) | `scripts/compose-agent.py` |
| `generate-template.py` | Generate starter templates for existing projects | `starter-templates/generate-template.py` |
| `setup-commands.py` | Install tool selector wrappers to other projects | `scripts/setup-commands.py` |
| `security_validator.py` | Security validation for autonomous execution | `scripts/security_validator.py` |

### New in v1.5.0

| Module | Purpose | Location |
|--------|---------|----------|
| `autonomous/` | **Autonomous runner with Claude API** | `scripts/autonomous/` |

### New in v1.4.0

| Module | Purpose | Location |
|--------|---------|----------|
| `state_providers/` | External state provider abstraction (Linear, File) | `scripts/state_providers/` |
| `execution/` | Execution control (checkpoints, turns, approval) | `scripts/execution/` |
| `progress/` | Real-time progress tracking and notifications | `scripts/progress/` |
| `security/` | Configurable command validation | `scripts/security/` |

### compose-agent.py

**Purpose:** Compose complete agent prompts from modular components

**Usage:**
```bash
# Compose all agents from config
python scripts/compose-agent.py --config ../config.yml --all

# Compose specific agent
python scripts/compose-agent.py --config ../config.yml --agent backend_dev
```

**What it Does:**
- Reads config.yml
- Combines base agent + platform + skills + context
- Generates complete agent prompts
- Outputs to `.ai-agents/composed/`

**Example Output:**
```
.ai-agents/composed/
├── backend_developer.md      # Base + web/backend + mcp-builder skill
├── frontend_developer.md     # Base + web/frontend + web-artifacts skill
└── manager.md                # Manager base + create-plans skill
```

### generate-template.py

**Purpose:** Generate starter templates for existing projects

**Usage:**
```bash
# Interactive mode (recommended)
cd your-project
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive

# Direct mode
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

**What it Creates:**
- Complete `.ai-agents/` directory structure
- Pre-configured context files (architecture, API contracts, coding standards)
- Ready-to-use agent configurations
- Example config.yml

**See:** [Starter Templates](#starter-templates) section below

### setup-commands.py

**Purpose:** Install tool selector wrappers for cross-project tool access

**Usage:**
```bash
# List available tools
python scripts/setup-commands.py --list

# Install to current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py

# Install globally (all projects)
python /path/to/AI_agents/scripts/setup-commands.py --global
```

**What it Installs:**
- 30 wrapper commands (~200-300 bytes each)
- `/ai-tools` discovery command
- All `/consider:*` thinking models

**See:** [Tool Selector](#tool-selector-new-v130) section below

### security_validator.py

**Purpose:** Security validation for autonomous execution mode

**New in:** Autonomous agent integration (v1.2.0)

**Usage:**
```python
from scripts.security_validator import SecurityValidator

validator = SecurityValidator("schemas/security-policy.json")
result = validator.validate_command("rm -rf /tmp/cache")

if result.allowed:
    # Execute command
    pass
else:
    print(f"Blocked: {result.reason}")
```

**Features:**
- Three-layer defense-in-depth
- Command allowlist checking
- Destructive pattern detection
- Filesystem scope restrictions

**Security Layers:**
1. **Allowlist:** Only approved commands execute
2. **Destructive Patterns:** Block `rm -rf /`, `DROP TABLE`, etc.
3. **Filesystem Scope:** Restrict to project directory

**Config:** `schemas/security-policy.json`

**See:** `docs/guides/SECURITY.md` for complete guide

---

## Autonomous Runner (NEW v1.5.0)

Implements Anthropic's recommended **two-agent pattern** for optimal context management.

**Location:** `scripts/autonomous/`

| File | Purpose |
|------|---------|
| `initializer.py` | Initializer agent - analyzes spec and creates tasks |
| `runner.py` | Coding agent - executes tasks with fresh context |
| `cli.py` | Command-line interface (init, start, resume, status, etc.) |
| `config.yml` | Default configuration template |
| `README.md` | Detailed documentation |

### Two-Agent Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIALIZER AGENT                         │
│  (Phase 1 - `init` command)                                 │
│                                                             │
│  1. Read spec file → 2. Analyze with Claude                 │
│  3. Create tasks in provider → 4. Write .project_state.json │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CODING AGENT(S)                           │
│  (Phase 2 - `start` command)                                │
│                                                             │
│  1. Get TODO task → 2. Implement with FRESH context         │
│  3. Test/verify → 4. Update status → 5. Next task           │
└─────────────────────────────────────────────────────────────┘
```

### Quick Start

```bash
# 1. Verify Claude Code CLI is installed (uses your subscription!)
claude --version

# 2. Phase 1: Initialize project from spec
python -m scripts.autonomous init --spec requirements.md

# 3. Phase 2: Run coding agent
python -m scripts.autonomous start

# 4. Monitor status
python -m scripts.autonomous status
```

**Note:** By default, uses Claude Code CLI (subscription-based) - no extra API costs!

### CLI Commands

```bash
# Phase 1: Initialize project from spec (Initializer Agent)
python -m scripts.autonomous init --spec FILE [--project-name NAME] [--force]

# Phase 2: Run coding agent (Coding Agent)
python -m scripts.autonomous start [--config CONFIG] [--resume]

# Show session recovery context
python -m scripts.autonomous resume

# Check status
python -m scripts.autonomous status

# Stop gracefully
python -m scripts.autonomous stop

# View logs
python -m scripts.autonomous logs [--tail N]

# View tasks
python -m scripts.autonomous tasks

# Validate configuration
python -m scripts.autonomous config [--config CONFIG]
```

### Configuration

```yaml
# .ai-agents/config.yml
autonomous:
  # Backend: "claude-code" (subscription) or "anthropic-sdk" (API)
  backend: "claude-code"  # Uses your Claude Code subscription!
  model: "opus"  # opus, sonnet, haiku
  max_tokens: 8192
  system_prompt_path: "prompts/roles/software-developer.md"
  max_turns_per_task: 50
  max_tasks_per_session: 10
  rate_limit_rpm: 50

execution:
  mode: "autonomous"
  checkpoints:
    turn_interval: 25
    on_regression_failure: true
    on_blocker: true
```

**Alternative (Anthropic SDK):**
```yaml
autonomous:
  backend: "anthropic-sdk"  # Uses API credits
  api_key_env: "ANTHROPIC_API_KEY"
  model: "claude-opus-4-20250514"
  cost_limit_per_session: 10.0
```

### Programmatic Usage

```python
from scripts.autonomous import ProjectInitializer, AutonomousRunner
from scripts.autonomous import InitializerConfig, RunnerConfig

# Phase 1: Initialize project from spec
init_config = InitializerConfig(
    model="opus",
    backend="claude-code"
)
initializer = ProjectInitializer(init_config)
result = initializer.initialize("requirements.md", project_name="My App")

print(f"Created {result.tasks_created} tasks")

# Phase 2: Execute tasks
runner_config = RunnerConfig(
    model="opus",
    max_tasks_per_session=5
)
runner = AutonomousRunner(runner_config)
runner.start()

# Check status
status = runner.get_status()
print(f"Tasks: {status['tasks_completed']}, State: {status['state']}")
```

### Execution Flow

**Phase 1 - Initializer Agent:**
1. **Read Spec**: Parse requirements/spec file
2. **Analyze**: Use Claude to break down into tasks (robust 3-strategy JSON extraction)
3. **Create Tasks**: Create structured tasks in state provider
4. **Setup META**: Create tracking issue for coordination
5. **Write Marker**: Write `.project_state.json` for detection

**Phase 2 - Coding Agent:**
1. **Start Session**: Initialize provider, load state
2. **Get Task**: Fetch next task using phase-aware sorting
3. **Execute**: Call Claude with FRESH context
4. **Parse Response**: Check for completion/blocker signals
5. **Update Status**: Mark task done, blocked, or in-progress
6. **Check Limits**: Cost, tasks, turns
7. **Repeat** until complete

### Task Execution Order

Tasks are sorted by **phase → task number → priority**:

| Pattern | Example | Sort Key |
|---------|---------|----------|
| META tasks | `META: Project` | phase 0 (always first) |
| `[PREFIX-X.Y]` | `[AUTH-1.2] Login` | phase=1, task=2 |
| `X.Y:` at start | `1.2: Setup DB` | phase=1, task=2 |
| `Phase X.Y` | `Phase 2.1 tests` | phase=2, task=1 |
| Linear ID | `ARK-123` | sorted by ID |
| Other | `Fix bug` | priority only |

**Best practice:** Name tasks with `[PREFIX-X.Y]` pattern in your spec:
```markdown
## Phase 1: Setup
- [APP-1.1] Create project structure
- [APP-1.2] Configure database

## Phase 2: Features
- [APP-2.1] Implement auth
```

### Cross-Phase Dependency Checking

Runner enforces strict ordering:
- **Earlier phases block later** - Phase 2 waits for ALL Phase 1 to be DONE
- **Earlier tasks block later** - Task 1.3 waits for 1.1 and 1.2
- **Blocked tasks logged** - Shows which tasks are blocking

### Safety Features

- **Cost Limits**: Stop when session cost exceeds limit
- **Rate Limiting**: Respect API rate limits
- **Turn Limits**: Maximum turns per task
- **Graceful Shutdown**: Signal handlers for clean exit
- **State Persistence**: Resume from where you left off

**See:** `scripts/autonomous/README.md` for complete documentation

---

## State Providers (NEW v1.4.0)

External state provider abstraction for session continuity.

**Location:** `scripts/state_providers/`

| File | Purpose |
|------|---------|
| `__init__.py` | Provider interface, dataclasses, factory function |
| `linear_provider.py` | Linear.app API integration |
| `file_provider.py` | Local file-based fallback |

### Usage

```python
from scripts.state_providers import get_provider

# Initialize from config
provider = get_provider()

# Or create directly
from scripts.state_providers.linear_provider import LinearStateProvider
provider = LinearStateProvider()
provider.initialize({'api_key_env': 'LINEAR_API_KEY'})

# Create task
task_id = provider.create_task({
    'title': 'Implement login',
    'priority': 2,
    'acceptance_criteria': ['Form displays', 'Validation works']
})

# Track session
session_id = provider.start_session()
# ... work ...
provider.end_session('Completed login implementation')

# Get progress
summary = provider.get_progress_summary()
print(f"Done: {summary['done']}/{summary['total']}")
```

### Provider Interface

```python
class StateProvider(ABC):
    def create_task(task_data: Dict) -> str
    def get_task(task_id: str) -> Optional[Task]
    def update_task(task_id: str, updates: Dict) -> bool
    def get_tasks(**filters) -> List[Task]
    def get_meta() -> Optional[SessionMeta]
    def update_meta(updates: Dict) -> bool
    def start_session() -> str
    def end_session(summary: str) -> bool
    def get_progress_summary() -> Dict
```

**See:** `prompts/patterns/external-state-provider.md` for full documentation

---

## Execution Control (NEW v1.4.0)

Configurable execution modes with checkpoints and approval handling.

**Location:** `scripts/execution/`

| File | Purpose |
|------|---------|
| `checkpoint_manager.py` | Checkpoint triggering and approval flow |
| `turn_counter.py` | Turn tracking across sessions |
| `approval_handler.py` | Multi-channel approval (CLI, Slack, Linear) |
| `__init__.py` | Module exports |

### Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `autonomous` | Minimal intervention, checkpoint on events | CI/CD, trusted workflows |
| `interactive` | Approval at key decisions | Development, learning |
| `supervised` | Approval for every action | Security-sensitive, production |

### Checkpoint Configuration

```yaml
# .ai-agents/config.yml
execution:
  mode: "interactive"
  checkpoints:
    turn_interval: 50        # Pause every 50 turns
    before_new_issue: true   # Pause before creating issues
    on_regression_failure: true
    on_blocker: true
    on_uncertainty: true
  approval:
    timeout_minutes: 60
    default_action: "pause"
    notification:
      cli: true
      slack_webhook: "${SLACK_WEBHOOK_URL}"
      linear_comment: true
  limits:
    max_turns_per_session: 500
    context_warning_threshold: 0.7
    context_pause_threshold: 0.85
```

### Usage

```python
from scripts.execution import CheckpointManager, TurnCounter

# Initialize
checkpoint_mgr = CheckpointManager(config)
turn_counter = TurnCounter()

# Track turns
turn_counter.increment()

# Check if checkpoint needed
if checkpoint_mgr.should_checkpoint(turn_counter.count):
    checkpoint_mgr.trigger_checkpoint("turn_interval")
```

**See:** `prompts/patterns/execution-modes.md` for full documentation

---

## Progress Tracking (NEW v1.4.0)

Real-time progress tracking with notifications.

**Location:** `scripts/progress/`

| File | Purpose |
|------|---------|
| `progress_tracker.py` | Metrics, events, display, notifications |
| `__init__.py` | Module exports |

### Features

- Real-time progress metrics
- Event logging with timestamps
- CLI display with progress bars
- Slack webhook notifications
- Rate limiting for notifications

### Usage

```python
from scripts.progress import create_progress_tracker

# Create with Slack notifications
tracker = create_progress_tracker(
    provider=state_provider,
    slack_webhook="https://hooks.slack.com/..."
)

# Track events
tracker.task_started("TASK-001", "Implement login")
tracker.task_completed("TASK-001", "Implement login")
tracker.blocker_detected("TASK-002", "Waiting for API")

# Get CLI display
print(tracker.get_cli_display())

# Output:
# ╔══════════════════════════════════════╗
# ║         PROJECT PROGRESS             ║
# ╠══════════════════════════════════════╣
# ║ Total: 10  Done: 6  Active: 2        ║
# ║ [██████████████░░░░░░] 60%           ║
# ╚══════════════════════════════════════╝
```

---

## Orchestration Scripts

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

**Location:** `scripts/orchestration/`

| Script | Purpose | Token Savings | Best For |
|--------|---------|---------------|----------|
| `simple_orchestrator.py` | Basic multi-agent orchestration via API | N/A | Learning, simple workflows |
| `prompt_cache.py` | Prompt caching for cost reduction | API cost savings | Repeated operations |
| `sandbox_executor.py` | Secure code execution sandbox | 37% per workflow | Multi-step workflows |
| `programmatic_orchestrator.py` | Programmatic tool calling | 37% reduction | Advanced automation |
| `file_based_orchestrator.py` | File-based agent coordination | N/A | Human-coordinated workflows |
| `custom_orchestrator_example.py` | Custom orchestration patterns | N/A | Custom use cases |

### Run Demos

```bash
# Test sandbox executor
python3 scripts/orchestration/sandbox_executor.py

# Run simple orchestrator
python3 scripts/orchestration/simple_orchestrator.py

# Test prompt caching
python3 scripts/orchestration/prompt_cache.py
```

### Key Patterns

**1. Prompt Caching** - Cache stable components for 5 minutes
**2. Sandbox Execution** - Execute code in isolated sandbox
**3. Programmatic Tools** - Generate code that calls tools (37% reduction)

**See:** [07-advanced.md](07-advanced.md) for detailed guide

---

## Tool Selector (NEW v1.3.0)

Enable `/command` style access to AI_agents tools from other projects.

### Installation

```bash
# List available tools
python scripts/setup-commands.py --list

# Install to current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py

# Install globally (all projects)
python /path/to/AI_agents/scripts/setup-commands.py --global
```

### What Gets Installed

**30 Wrapper Commands** (~200-300 bytes each):
- 12 thinking models (`/consider:*`)
- Workflow commands (`/debug`, `/create-plan`, `/whats-next`)
- Skill creation (`/create-agent-skill`)
- 1 discovery command (`/ai-tools`)

### Token Impact

**At-rest:** ~50 tokens (command names only)
**Per invocation:** +60 tokens (~1.5% overhead)

**Calculation:**
- 30 commands × 1.67 tokens per wrapper = 50 tokens at-rest
- Full skill load on invocation: 60 tokens overhead

### Usage in Target Project

```bash
# Discover available tools
/ai-tools

# Use thinking models
/consider:first-principles "Should we use microservices?"
/consider:pareto "Which features drive 80% of value?"

# Use workflow commands
/debug "Login fails after deployment"
/create-plan "Implement payment system"

# Create resources
/create-agent-skill "database migration skill"
/create-prompt "Analyze log files for errors"
```

### Benefits

1. **Access tools from any project** - No need to copy files
2. **Minimal footprint** - ~50 tokens at-rest
3. **Lazy loading** - Tools load on-demand
4. **Centralized updates** - Update AI_agents once, available everywhere
5. **Clean separation** - Project files stay minimal

### Removal

```bash
# Remove from current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py --remove

# Remove from all projects
python /path/to/AI_agents/scripts/setup-commands.py --remove --global
```

---

## Starter Templates

Quick-start templates for existing projects.

**New in:** v1.1.0
**Location:** `starter-templates/`

### Available Templates

| Template | Best For | Command | Location |
|----------|----------|---------|----------|
| `web-app` | Full-stack web apps (React/Vue + Node/Python) | `--type web-app` | `starter-templates/web-app/` |
| `mobile-app` | Mobile apps (React Native, Flutter, native) | `--type mobile-app` | `starter-templates/mobile-app/` |
| `full-stack` | Complete full-stack with multiple services | `--type full-stack` | `starter-templates/full-stack/` |
| `api-service` | Backend API service or microservice | `--type api-service` | `starter-templates/api-service/` |
| `data-pipeline` | Data processing or analytics project | `--type data-pipeline` | `starter-templates/data-pipeline/` |

### Interactive Mode (Recommended)

```bash
cd your-existing-project
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive
```

**Prompts you through:**
1. Select template type
2. Enter project name
3. Choose output directory
4. Configure agents
5. Set context files

### Direct Mode

```bash
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

### What You Get

```
your-project/
├── .ai-agents/
│   ├── config.yml                    # Agent configuration
│   ├── context/
│   │   ├── architecture.md           # System architecture
│   │   ├── api-contracts.md          # API documentation
│   │   ├── coding-standards.md       # Code style guide
│   │   └── tech-stack.md             # Technology choices
│   ├── state/
│   │   └── team-communication.json   # Initial state file
│   └── composed/                     # Generated agents (run compose-agent.py)
├── README.md                         # Updated with AI agent info
└── [your existing files]
```

### Template Details

#### web-app
**Best For:** React/Vue + Node/Python web applications

**Agents:**
- Manager
- Frontend Developer (React/Vue)
- Backend Developer (Node/Python)
- QA Tester

**Context Files:**
- Frontend architecture (components, routing, state)
- Backend architecture (API, database, auth)
- API contracts (endpoints, schemas)

#### mobile-app
**Best For:** React Native, Flutter, native iOS/Android

**Agents:**
- Manager
- Mobile Developer
- Backend Developer
- QA Tester

**Context Files:**
- Mobile architecture (navigation, state, native modules)
- Backend API contracts
- Platform-specific guidelines (iOS/Android)

#### full-stack
**Best For:** Multiple services, microservices, complex systems

**Agents:**
- Manager
- Frontend Developer
- Backend Developer × 2
- DevOps Engineer
- QA Tester

**Context Files:**
- Microservices architecture
- Service contracts
- Infrastructure setup
- Deployment pipeline

#### api-service
**Best For:** Backend API, microservice, REST/GraphQL service

**Agents:**
- Manager
- Backend Developer
- QA Tester

**Context Files:**
- API architecture
- Database schema
- Authentication/authorization
- Endpoint documentation

#### data-pipeline
**Best For:** ETL, data processing, analytics, ML pipelines

**Agents:**
- Manager
- Data Engineer
- Backend Developer
- QA Tester

**Context Files:**
- Pipeline architecture
- Data sources and schemas
- Processing logic
- Output formats

---

## Init Scripts Templates

Project-specific environment setup scripts generated by IT Specialist.

**New in:** Autonomous agent integration (v1.2.0)
**Location:** `templates/init-scripts/`

### Available Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `nodejs-react-init.sh` | Node.js + React projects | `templates/init-scripts/nodejs-react-init.sh` |
| `python-django-init.sh` | Python + Django projects | `templates/init-scripts/python-django-init.sh` |
| `fullstack-init.sh` | Full-stack multi-service projects | `templates/init-scripts/fullstack-init.sh` |
| `README.md` | Template documentation | `templates/init-scripts/README.md` |

### What Init Scripts Do

1. **Dependency Checks** - Verify required tools installed (node, python, docker, etc.)
2. **Installation** - Install project dependencies
3. **Configuration** - Set up environment variables
4. **Database Setup** - Create DB, run migrations
5. **Test Infrastructure** - Verify tests can run
6. **Build Verification** - Ensure project builds
7. **Documentation** - Display next steps

### When Generated

IT Specialist (Complex Mode, Phase 4) generates `init.sh` after validating infrastructure:
- Detects project type (Node, Python, etc.)
- Selects appropriate template
- Customizes for project specifics
- Outputs to project root

### Usage

```bash
# After IT Specialist generates init.sh
chmod +x init.sh
./init.sh

# Script will:
# ✓ Check dependencies
# ✓ Install packages
# ✓ Configure environment
# ✓ Set up database
# ✓ Run test suite
# ✓ Build project
```

**See:** `prompts/it-specialist-agent.md` (Phase 4: Environment Automation)

---

## Best Practices

### Script Usage

1. **Use compose-agent.py** - Always compose agents from config, don't edit manually
2. **Version control config.yml** - Track agent configurations
3. **Generate templates once** - Don't regenerate, modify config instead
4. **Test init scripts** - Run on clean environment before sharing

### Tool Selector

5. **Install selectively** - Only install in projects that need it
6. **Update regularly** - Pull AI_agents updates for new tools
7. **Monitor token usage** - Track overhead if using many tools

### Security

8. **Review security-policy.json** - Adjust allowlist for your needs
9. **Test validator** - Verify blocked commands before autonomous execution
10. **Restrict scope** - Limit filesystem access to project directory

---

## See Also

- **Advanced Features:** [07-advanced.md](07-advanced.md)
- **Orchestration Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`
- **Starter Templates:** `starter-templates/README.md`
- **Security Guide:** `docs/guides/SECURITY.md`
- **IT Specialist:** [02-agents.md](02-agents.md#it-specialist)

---

[← Back to Index](index.md) | [Previous: Workflows](05-workflows.md) | [Next: Advanced Features →](07-advanced.md)
