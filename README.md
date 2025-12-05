# AI Agents Library

A comprehensive, modular library for building multi-agent software development systems based on advanced context engineering principles.

**Version:** 1.3.0

---

## What is This?

This library provides reusable, composable AI agent prompts and infrastructure for teams of AI agents working together on software projects. Instead of manually crafting prompts for each project, you can compose specialized agents from modular components.

### Key Features

✨ **Modular Design**: Base prompts + platform augmentations + project context
🎓 **Skills Integration**: Anthropic Skills for specialized capabilities
🚀 **Starter Templates**: Quick-start templates for existing projects
🤝 **Dual-Mode Workflows**: Simple Mode (default) + Complex Mode (with infrastructure validation & code review)
⚙️ **Specialized Agents**: IT Specialist for infrastructure, Senior Engineer for code review
📊 **Optional Project Tracking**: Scrum Master agent for visibility, sprint metrics, and AppFlowy integration
🧠 **Advanced Context Management**: Ultra-lean Manager context (15-25%)
🌲 **Git-Based Workflow**: Branch isolation prevents conflicts
📡 **Structured Communication**: JSON-based inter-agent messaging
🎯 **Platform Agnostic**: Web, mobile, desktop, and more
⚡ **Advanced Tool Use**: Deferred loading, prompt caching, programmatic orchestration (37% token reduction)
💭 **Slash Commands**: 12 thinking model commands, debugging workflows, task management
🔍 **Quality Auditors**: Agent-based review for skills, slash commands, and subagents
📐 **XML Architecture**: Pure XML prompt structure with 25% token efficiency improvement
🔌 **Tool Selector**: Cross-project tool access via `/command` style wrappers

---

## Quick Start

### For Existing Projects

Choose the approach that fits your needs:

| Approach | Best For | Setup Time |
|----------|----------|------------|
| **Option A: Starter Templates** | Quick setup with pre-configured files | ~5 minutes |
| **Option B: Git Submodule** | Stay synced with library updates | ~10 minutes |
| **Option C: Direct Copy** | Full control, no external dependencies | ~10 minutes |

---

#### Option A: Starter Templates (Fastest)

Use pre-configured templates for instant setup:

```bash
cd your-project

# Interactive mode (recommended)
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive

# Or direct command
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

**What you get:**
- ✅ Complete `.ai-agents/` directory structure
- ✅ Pre-configured context files (architecture, API contracts, coding standards)
- ✅ Ready-to-use agent configurations

**Available templates:** `web-app`, `mobile-app`, `full-stack`, `api-service`, `data-pipeline`

See [starter-templates/README.md](starter-templates/README.md) for complete guide.

---

#### Option B: Git Submodule (Recommended - Stays Updated)

Add the library as a submodule to receive updates:

```bash
cd your-project

# 1. Add library as submodule
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library

# 2. Create project structure
mkdir -p .ai-agents/{context,state,skills,composed}

# 3. Copy example config
cp .ai-agents/library/examples/web-app-team/config.yml .ai-agents/config.yml

# 4. Create your context files
touch .ai-agents/context/{architecture,coding-standards,api-contracts}.md
```

**Your structure:**
```
your-project/
├── .ai-agents/
│   ├── library/           # Git submodule (this repo)
│   ├── config.yml         # Your agent configuration
│   ├── context/           # Your project documentation
│   │   ├── architecture.md
│   │   ├── coding-standards.md
│   │   └── api-contracts.md
│   ├── skills/            # Your custom skills (optional)
│   └── composed/          # Generated agent prompts
└── src/                   # Your project code
```

**Updating the library:**
```bash
cd .ai-agents/library && git pull origin main && cd ../..
git add .ai-agents/library && git commit -m "Update AI Agents library"
```

See [skills/PROJECT_INTEGRATION.md](skills/PROJECT_INTEGRATION.md) for detailed guide.

---

#### Option C: Direct Copy (Full Control)

Copy the library directly for complete ownership:

```bash
cd your-project

# Copy library
cp -r path/to/AI_agents .ai-agents/

# Remove git history to make it part of your repo
rm -rf .ai-agents/.git

# Create your context files
mkdir -p .ai-agents/context
touch .ai-agents/context/{architecture,coding-standards,api-contracts}.md
```

**Trade-offs:**
- ✅ Full control over all files
- ✅ No submodule complexity
- ❌ Manual process to sync updates from library

---

### After Setup: Create Context Files

Regardless of which option you chose, populate your context files:

1. **`architecture.md`** - Your system architecture, tech stack, key components
2. **`coding-standards.md`** - Your team conventions, style guides
3. **`api-contracts.md`** - Your API specifications, endpoints
4. **`current-features.md`** - Feature roadmap, priorities (optional)

See [examples/](examples/) for reference templates.

### Compose Your Agents

```bash
cd .ai-agents/library  # or .ai-agents if using direct copy
python scripts/compose-agent.py --config ../config.yml --all
```

This generates complete agent prompts in `.ai-agents/composed/`.

---

## Where to Place .ai-agents/

### The Simple Rule

**`.ai-agents/` goes next to `.git/`** - Place it at your repository root, regardless of where your code lives.

### Common Scenarios

#### Scenario 1: Standard Repository
```
my-project/              ← Repository root
├── .git/
├── .ai-agents/          ✅ Place here
├── src/
├── package.json
└── README.md
```

#### Scenario 2: Code in Subdirectory
```
my-project/              ← Repository root
├── .git/
├── .ai-agents/          ✅ Place here (NOT in app/)
├── app/                 ← Code lives here
│   ├── src/
│   └── package.json
├── docs/
└── README.md
```

**Why?** The library uses relative paths from repository root. Config references like `context/architecture.md` assume `.ai-agents/` is at the root.

#### Scenario 3: Monorepo - Single Team
```
monorepo/                ← Repository root
├── .git/
├── .ai-agents/          ✅ Single shared setup
├── packages/
│   ├── frontend/
│   ├── backend/
│   └── mobile/
└── package.json
```

**Best for:** One team working across all packages with shared standards.

#### Scenario 4: Monorepo - Per-Package Teams
```
monorepo/                ← Repository root
├── .git/
├── packages/
│   ├── frontend/
│   │   └── .ai-agents/  ✅ Per-package setup
│   ├── backend/
│   │   └── .ai-agents/  ✅ Per-package setup
│   └── mobile/
│       └── .ai-agents/  ✅ Per-package setup
└── package.json
```

**Best for:** Independent teams with different tech stacks and standards.

### Quick Decision Guide

| Your Project Structure | Where to Place .ai-agents/ | Why |
|------------------------|---------------------------|-----|
| Standard repo | Next to .git/ | Standard setup |
| Code in subdirectory | Next to .git/ (NOT in subdirectory) | Relative paths from root |
| Monorepo - single team | Root, next to .git/ | Shared config for all packages |
| Monorepo - multiple teams | Inside each package/ | Independent configs per team |
| Nested repositories | Next to each .git/ | Each repo is independent |

### Pro Tips

✅ **DO:**
- Place at repository root (next to `.git/`)
- Use relative paths in configs (e.g., `../../src/components`)
- Add `.ai-agents/state/` and `.ai-agents/checkpoints/` to `.gitignore`

❌ **DON'T:**
- Place inside code directories (e.g., `src/.ai-agents/`)
- Use absolute paths in configs
- Commit agent runtime state

### Starter Template Automatic Placement

When using starter templates, the `--output` parameter determines placement:

```bash
# Standard repo - output to current directory (repository root)
cd my-project/
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "MyProject" \
  --output .

# Code in subdirectory - still output to root
cd my-project/  # Repository root
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "MyProject" \
  --output .  # Creates my-project/.ai-agents/

# Monorepo with per-package setup
cd monorepo/packages/frontend/
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "Frontend" \
  --output .  # Creates monorepo/packages/frontend/.ai-agents/
```

**The generator always creates `.ai-agents/` in the `--output` directory.**

---

## Architecture

### Layered Composition

```
┌─────────────────────────────────────────┐
│   Project Context (Your Requirements)   │
│   • Business logic                       │
│   • API contracts                        │
│   • Team conventions                     │
├─────────────────────────────────────────┤
│   Skills (Domain Expertise) ✨ NEW      │
│   • Specialized workflows                │
│   • Tool integrations                    │
│   • Domain knowledge                     │
├─────────────────────────────────────────┤
│   Platform Augmentation (Specialized)    │
│   • Web/Mobile/Desktop expertise         │
│   • Framework knowledge                  │
│   • Platform best practices              │
├─────────────────────────────────────────┤
│   Base Agent (Universal)                 │
│   • Core software engineering            │
│   • Testing, debugging, git              │
│   • Security, performance                │
└─────────────────────────────────────────┘
```

### Multi-Agent Team Workflows

**🔹 Simple Mode** (90% of projects - Default)
```
┌──────────────┐
│   Manager    │ ← Plans & coordinates
└──────┬───────┘
       │
   ┌───┴───┬──────────┬─────────┐
   │       │          │         │
┌──▼───┐ ┌▼──────┐ ┌─▼─────┐ ┌─▼────────┐
│Archi-│ │Frontend│ │Backend│ │Integration│
│tect  │ │  Dev   │ │  Dev  │ │  Agent   │
└──────┘ └────────┘ └───────┘ └──────────┘
```

**🔸 Complex Mode** (10% of projects - Advanced)
```
        ┌──────────────┐
        │   Manager    │ ← Coordinates only
        └──────┬───────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼─────┐    ┌────▼──────────┐
│     IT     │    │    Senior     │
│ Specialist │    │   Engineer    │
│(Infra)     │    │(Review+Merge) │
└──────┬─────┘    └────▲──────────┘
       │               │
       │          ┌────┴────┬──────────┬─────────┐
       └─────────►│         │          │         │
                ┌─▼─────┐ ┌▼──────┐ ┌─▼─────┐ ┌─▼──┐
                │Backend│ │Frontend│ │Backend│ │ QA │
                │ Dev 1 │ │  Dev   │ │ Dev 2 │ │Test│
                └───────┘ └────────┘ └───────┘ └────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

---

## Repository Structure

```
AI_agents/
├── .claude/                 # Claude Code extensions
│   ├── commands/            # Slash commands
│   │   ├── ai-tools.md      # Tool discovery router 🔌 NEW
│   │   ├── consider/        # 12 thinking model commands
│   │   │   ├── first-principles.md
│   │   │   ├── 5-whys.md
│   │   │   ├── swot.md
│   │   │   ├── cost-benefit.md
│   │   │   ├── premortem.md
│   │   │   ├── second-order.md
│   │   │   ├── eisenhower.md
│   │   │   ├── inversion.md
│   │   │   ├── opportunity-cost.md
│   │   │   ├── stakeholder-mapping.md
│   │   │   ├── devils-advocate.md
│   │   │   └── reversible-irreversible.md
│   │   ├── whats-next.md    # Context handoff between sessions
│   │   ├── debug.md         # Systematic debugging methodology
│   │   ├── add-to-todos.md  # Add tasks to todo list
│   │   └── check-todos.md   # Review todo list
│   └── agents/              # Quality auditor agents
│       ├── skill-auditor.md         # Reviews skills for best practices
│       ├── slash-command-auditor.md # Reviews slash commands
│       └── subagent-auditor.md      # Reviews agent configurations
│
├── prompts/                 # All agent prompts
│   ├── roles/               # Base agent prompts
│   │   ├── software-developer.md
│   │   ├── manager.md
│   │   ├── qa-tester.md
│   │   ├── architect.md
│   │   └── scrum-master.md      # Optional: Project tracking & visibility
│   ├── manager-task-delegation.md      # Comprehensive Manager guide (dual-mode)
│   ├── manager-quick-reference.md      # Quick-start Manager template
│   ├── it-specialist-agent.md          # Infrastructure validation specialist
│   └── senior-engineer-agent.md        # Code review & integration specialist
│
├── platforms/               # Platform specializations
│   ├── web/
│   │   ├── frontend-developer.md
│   │   └── backend-developer.md
│   ├── mobile/
│   │   └── mobile-developer.md
│   └── ...
│
├── skills/                  # Anthropic Skills integration ✨
│   ├── README.md            # Skills overview
│   ├── CATALOG.md           # Available skills directory
│   ├── INTEGRATION.md       # Technical guide
│   ├── anthropic/           # Anthropic skills (submodule)
│   ├── custom/              # Project-specific skills
│   │   └── appflowy-integration/  # AppFlowy task tracking (for Scrum Master)
│   └── taches-cc/           # taches-cc skills 🎯 NEW
│       ├── create-agent-skills/  # Skill authoring best practices
│       ├── create-plans/         # Hierarchical project planning
│       └── debug-like-expert/    # Systematic debugging with domain expertise
│
├── starter-templates/       # Project templates 🚀 NEW
│   ├── generate-template.py # Template generator
│   ├── web-app/            # Web application template
│   ├── mobile-app/         # Mobile app template
│   └── README.md           # Template documentation
│
├── schemas/                 # JSON schemas
│   ├── communication-protocol.json
│   ├── communication-protocol-examples.json  # Tool use examples
│   ├── state-management.json
│   ├── agent-schema.json    # v2.0 with deferred loading support
│   └── project-config.json
│
├── tools/                   # Tool definitions
│   ├── skill-search.md      # Deferred skill discovery
│   └── programmatic-tools.md # Programmatic orchestration tools
│
├── workflows/               # Multi-agent patterns
├── examples/                # Example configurations
│
├── scripts/                 # Automation tools
│   ├── compose-agent.py     # Agent composition with deferred loading
│   ├── setup-commands.py    # Tool selector installer 🔌 NEW
│   └── orchestration/       # Advanced orchestration
│       ├── simple_orchestrator.py      # Basic multi-agent orchestration
│       ├── prompt_cache.py             # Prompt caching for cost reduction
│       ├── sandbox_executor.py         # Secure code execution sandbox
│       └── programmatic_orchestrator.py # Programmatic tool calling
│
├── docs/                    # Documentation
│   └── PROGRAMMATIC_TOOL_CALLING.md    # Programmatic orchestration guide
│
├── tests/                   # Test suite
│   └── test_compose_agent.py           # Composition tests
│
└── memory/                  # RAG and knowledge base
```

---

## Examples

### Quick Start with Starter Templates 🚀

**Use pre-configured templates for instant setup:**

```bash
# For existing web app
cd your-project
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .

# For existing mobile app
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type mobile-app \
  --name "YourApp" \
  --output .
```

See [starter-templates/README.md](starter-templates/README.md) for complete guide and all available templates.

---

### Web Application Team (Manual Configuration)

```yaml
# .ai-agents/config.yml
agents:
  team_manager:
    base: "prompts/roles/manager.md"

  frontend_developer:
    base: "prompts/roles/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "core/artifacts-builder"
      - "design/theme-factory"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/api-contracts.md"

  backend_developer:
    base: "prompts/roles/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      - "core/mcp-builder"
```

See [examples/web-app-team/](examples/web-app-team/) for complete example.

### Mobile Application Team

See [examples/mobile-app-team/](examples/mobile-app-team/) for React Native example.

---

## Slash Commands

The library includes powerful slash commands for enhanced workflows in Claude Code:

### Thinking Model Commands (`/consider:*`)

12 analytical frameworks for structured problem-solving:

| Command | Description | Use When |
|---------|-------------|----------|
| `/consider:first-principles` | Break down to fundamental truths | Complex problems, novel solutions |
| `/consider:5-whys` | Root cause analysis | Debugging, understanding failures |
| `/consider:swot` | Strengths, Weaknesses, Opportunities, Threats | Strategic decisions, architecture choices |
| `/consider:cost-benefit` | Analyze tradeoffs | Technology selection, refactoring |
| `/consider:premortem` | Imagine future failures | Risk assessment, deployment planning |
| `/consider:second-order` | Identify downstream effects | System design, breaking changes |
| `/consider:eisenhower` | Urgent vs Important prioritization | Sprint planning, task management |
| `/consider:inversion` | Think backwards from failure | Avoiding pitfalls, security review |
| `/consider:opportunity-cost` | What are you NOT doing? | Resource allocation, priorities |
| `/consider:stakeholder-mapping` | Identify affected parties | API changes, migrations |
| `/consider:devils-advocate` | Challenge assumptions | Code review, architecture review |
| `/consider:reversible-irreversible` | Categorize by reversibility | Deployment strategy, data migrations |

### Workflow Commands

| Command | Description | Use When |
|---------|-------------|----------|
| `/whats-next` | Context handoff between sessions | Starting new session, resuming work |
| `/debug` | Systematic debugging methodology | Troubleshooting, investigating issues |
| `/add-to-todos` | Add tasks to todo list | Planning work, tracking tasks |
| `/check-todos` | Review current todo list | Status check, progress review |

**Usage Example:**
```bash
# Before making an architecture decision
/consider:swot

# Before deploying a major change
/consider:premortem

# When debugging a complex issue
/debug
```

### Quality Auditor Agents

Run quality checks on your agent configurations:

| Agent | Purpose | Usage |
|-------|---------|-------|
| `skill-auditor` | Reviews skills for best practices | Validate new skills, optimize token usage |
| `slash-command-auditor` | Reviews slash command quality | Ensure command clarity and effectiveness |
| `subagent-auditor` | Reviews agent configurations | Validate agent composition, check for issues |

**Usage:**
```bash
# Audit a skill
claude-code agent:.claude/agents/skill-auditor.md --input skills/custom/my-skill/

# Audit a slash command
claude-code agent:.claude/agents/slash-command-auditor.md --input .claude/commands/my-command.md

# Audit an agent configuration
claude-code agent:.claude/agents/subagent-auditor.md --input .ai-agents/composed/backend-developer.md
```

### Tool Selector (Cross-Project Access)

Use AI_agents tools from any project via `/command` style wrappers:

```bash
# Install tools to your project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py

# Or install globally
python /path/to/AI_agents/scripts/setup-commands.py --global

# List available tools
python /path/to/AI_agents/scripts/setup-commands.py --list
```

**What gets installed:**
- 30 wrapper commands (~60 tokens overhead per invocation)
- `/ai-tools` discovery command
- All `/consider:*` thinking models

**Usage in target project:**
```bash
/ai-tools                    # Discover available tools
/create-prompt [description] # Create optimized prompts
/debug [issue]               # Apply debugging methodology
/consider:first-principles   # Break down to fundamentals
```

**Token impact:** Negligible (~50 tokens at-rest, +60 tokens per invocation)

---

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - quick start guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed system architecture with Skills Integration |
| [Context_Engineering.md](Context_Engineering.md) | Foundational principles (the "HOLY BIBLE") |
| [SKILLS_GUIDE.md](SKILLS_GUIDE.md) | **Comprehensive skills guide** - Selection, usage, best practices |
| [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) | **Human-coordinated workflows** - Step-by-step multi-agent coordination |
| [PARALLEL_EXECUTION_GUIDE.md](PARALLEL_EXECUTION_GUIDE.md) | Multi-agent parallelization strategies |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Adding skills to existing projects |
| [starter-templates/README.md](starter-templates/README.md) | **Starter templates guide** - Quick setup for existing projects 🚀 |
| [prompts/manager-task-delegation.md](prompts/manager-task-delegation.md) | **Manager guide** - Dual-mode workflow (Simple + Complex) |
| [prompts/manager-quick-reference.md](prompts/manager-quick-reference.md) | **Manager quick-start** - Copy-paste templates |
| [prompts/it-specialist-agent.md](prompts/it-specialist-agent.md) | **IT Specialist** - Infrastructure validation (8 critical checks) |
| [prompts/senior-engineer-agent.md](prompts/senior-engineer-agent.md) | **Senior Engineer** - Code review & integration |
| [skills/README.md](skills/README.md) | Skills integration overview |
| [skills/CATALOG.md](skills/CATALOG.md) | Available skills directory with token estimates |
| [skills/INTEGRATION.md](skills/INTEGRATION.md) | Skills technical implementation guide |
| [skills/taches-cc/create-agent-skills/](skills/taches-cc/create-agent-skills/) | **Skill authoring best practices** - Create high-quality skills 🎯 |
| [skills/taches-cc/create-plans/](skills/taches-cc/create-plans/) | **Hierarchical planning** - Break down complex projects 🎯 |
| [skills/taches-cc/debug-like-expert/](skills/taches-cc/debug-like-expert/) | **Expert debugging** - Systematic issue resolution 🎯 |
| [.claude/commands/consider/](./claude/commands/consider/) | **Thinking models** - 12 analytical frameworks 💭 |
| [.claude/agents/](./claude/agents/) | **Quality auditors** - Review skills, commands, and agents 🔍 |
| [docs/PROGRAMMATIC_TOOL_CALLING.md](docs/PROGRAMMATIC_TOOL_CALLING.md) | **Advanced Tool Use** - Programmatic orchestration guide |
| [examples/](examples/) | Reference implementations with skills |

---

## How It Works

### Dual-Mode Workflow System

The library supports two workflow modes depending on project complexity:

**🔹 Simple Mode** (90% of projects):
```
User → Manager → Task Agents → Integration Agent
```

**🔸 Complex Mode** (10% of projects):
```
User → Manager → IT Specialist → Task Agents → Senior Engineer
```

### Optional: Project Tracking with Scrum Master

For projects requiring visibility and reporting, add the **Scrum Master** agent:

**With Scrum Master** (Simple Mode):
```
User → Manager → [Scrum Master Setup] → Task Agents → Integration Agent
                  ↓
          [AppFlowy Tracking]
```

**With Scrum Master** (Complex Mode):
```
User → Manager → [Scrum Master Setup] → IT Specialist → Task Agents → Senior Engineer
                  ↓
          [AppFlowy Tracking + Daily Summaries]
```

**When to Enable Scrum Master:**
- ✅ External stakeholders need visibility (clients, executives)
- ✅ Sprint velocity tracking required
- ✅ Daily standup summaries needed
- ✅ You have AppFlowy server (self-hosted or cloud)

**What Scrum Master Does:**
- Tracks all tasks in AppFlowy workspace
- Generates daily standup summaries
- Calculates sprint velocity metrics
- Reports blockers to Manager
- Creates stakeholder presentations

**What Scrum Master Does NOT Do:**
- ❌ Create or assign tasks (Manager's job)
- ❌ Make technical decisions
- ❌ Review code or approve merges

See `examples/web-app-team/config-with-scrum-master.yml` for configuration and
`skills/custom/appflowy-integration/README.md` for setup guide.

### Example: User Authentication Feature

### 1. User Makes a Request

```
User: "Implement user authentication"
```

### 2. Manager Chooses Mode & Breaks Down Task

**Complex Mode** (new project with infrastructure needs):

```
Manager:
1. Chooses Complex Mode (first feature, needs infrastructure validation)
2. Delegates to IT Specialist for infrastructure setup
3. Creates task breakdown:
   ├── TASK-001: Implement JWT service (Backend Dev + mcp-builder skill)
   ├── TASK-002: Create auth API (Backend Dev + mcp-builder skill)
   ├── TASK-003: Build login form (Frontend Dev + artifacts-builder skill)
   └── TASK-004: Write tests (QA Tester + webapp-testing skill)
4. Delegates to Senior Engineer for review & integration
```

**Simple Mode** (established project):

```
Manager:
1. Creates task breakdown (same as above)
2. Delegates directly to Task Agents
3. Delegates to Integration Agent when complete
```

### 3. Agents Work in Parallel

```
feature/user-auth/
├── agent/architect/design
├── agent/backend-dev/jwt-service
├── agent/backend-dev/auth-api
├── agent/frontend-dev/login-form
└── agent/mobile-dev/login-screen
```

### 4. Agents Communicate

```json
{
  "type": "status_update",
  "agent_id": "frontend-dev-001",
  "task_id": "TASK-004",
  "status": "in_progress",
  "progress": 75
}
```

### 5. Manager Coordinates Integration

- Ensures API contracts are followed
- Resolves conflicts
- Coordinates testing
- Merges when complete

---

## Coordination Models: Three Approaches

**IMPORTANT**: The workflow described above represents the **conceptual model** of multi-agent coordination. In practice, there are **three ways** to implement this:

### 🤝 Human-Coordinated (Practical Today)

**What it is**: You manually run agents in sequence and relay information between them.

**How it works**:
```
You → Manager Agent (creates task plan)
You → Backend Agent (works on TASK-001)
You → Frontend Agent (works on TASK-002, you relay backend's progress)
You → Manager Agent (coordinates integration, you provide status from both)
```

**Communication**:
- Agents write status to `.ai-agents/state/team-communication.json`
- You read the file and relay relevant info to other agents
- Agents can see each other's updates by reading the shared file
- You act as coordinator and decision-maker

**Tools**:
- Claude Code, ChatGPT, or any LLM tool
- One agent session at a time
- Manual switching between agents

**Best for**:
- ✅ **90% of users** - Most practical approach today
- ✅ Small to medium teams (1-5 agents)
- ✅ Projects where you want control and visibility
- ✅ Learning multi-agent patterns
- ✅ When using tools like Claude Code that run one session at a time

**See**: [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) for complete tutorial

---

### 🔧 Task Tool Delegation (Best of Both Worlds) ✨ **NEW**

**What it is**: Manager spawns agents using Claude Code's Task tool. Each agent gets a fresh context window.

**How it works**:
```
Manager (in Claude Code):
  ├─ Uses Task tool → IT Specialist (fresh context, 0 tokens)
  ├─ Uses Task tool → Backend Dev (fresh context, 0 tokens)
  ├─ Uses Task tool → Frontend Dev (fresh context, 0 tokens)
  └─ Uses Task tool → Senior Engineer (fresh context, 0 tokens)

Each agent:
  - Starts with 0 tokens (no inherited context)
  - Reads only what Manager provides in prompt
  - Reports back to Manager when done
  - Manager context stays lean (~15-25%)
```

**Communication**:
- Manager delegates via Task tool
- Agents read `team-communication.json` for context
- Agents report back with brief summaries
- Manager acknowledges and moves to next task

**Tools**:
- Claude Code (Task tool feature)
- No API costs (runs within Claude Code session)
- Single user session, multiple sub-agents
- Fresh context per agent (isolation benefits)

**Best for**:
- ✅ **Recommended for most users** - Great balance of control and efficiency
- ✅ Complex projects (5+ agents)
- ✅ First-time infrastructure setup
- ✅ Projects needing code review
- ✅ When you want Manager to stay lean (<25% context)

**Dual-Mode Workflow**:
- **Simple Mode**: Manager → Task Agents → Integration Agent (3-5 agents)
- **Complex Mode**: Manager → IT Specialist → Task Agents → Senior Engineer (5+ agents)

**See**: [prompts/manager-task-delegation.md](prompts/manager-task-delegation.md) for complete guide

---

### 🤖 Fully Automated (Requires Custom Tooling)

**What it is**: Programmatic orchestration system that runs multiple agents via LLM APIs.

**How it works**:
```python
orchestrator = MultiAgentOrchestrator()
orchestrator.assign_task("TASK-001", backend_agent)
orchestrator.assign_task("TASK-002", frontend_agent)

# Agents run in parallel, communicate automatically
# Manager receives updates via callbacks
# System coordinates integration automatically
```

**Communication**:
- Direct agent-to-agent messaging via message queue
- Automatic status propagation
- Real-time coordination without human intervention

**Tools**:
- Custom Python scripts using LLM APIs (Claude API, OpenAI API)
- Message queue (Redis, RabbitMQ) or event system
- Orchestration framework (custom or tools like LangGraph, CrewAI)

**Best for**:
- ⚠️ Advanced users with programming experience
- ⚠️ Large-scale projects (5+ agents)
- ⚠️ CI/CD automation
- ⚠️ When you need true parallel execution

**See**: [scripts/orchestration/](scripts/orchestration/) for example implementations

---

### Quick Comparison

| Aspect | Human-Coordinated | Task Tool Delegation ✨ | Fully Automated |
|--------|-------------------|------------------------|-----------------|
| **Setup** | ✅ Simple (any LLM tool) | ✅ Simple (Claude Code) | ⚠️ Complex (custom code) |
| **Control** | ✅ Full visibility | ✅ Full visibility | ⚠️ Less direct control |
| **Speed** | ⚠️ Sequential | ⚠️ Sequential (per manager) | ✅ True parallel |
| **Context Isolation** | ❌ No isolation | ✅ Fresh context per agent | ✅ Fresh context per agent |
| **Manager Context** | ⚠️ Can overflow | ✅ Stays lean (15-25%) | N/A |
| **Communication** | Manual relay | Automatic (Task tool) | Automatic (message queue) |
| **Best for** | Learning, simple projects | **Most users** | Advanced automation |
| **Learning curve** | Low | Low | High (programming required) |
| **Cost** | Lower (one at a time) | **No API costs** | Higher (API calls) |

---

### Which Should You Use?

**🔧 Task Tool Delegation (Recommended for Most)** if you:
- ✅ Use Claude Code
- ✅ Have complex projects (5+ agents)
- ✅ Want Manager to stay lean (no context overflow)
- ✅ Need infrastructure validation and code review
- ✅ Want **zero API costs** with fresh context isolation
- ✅ Prefer Simple vs Complex mode flexibility

**🤝 Human-Coordinated** if you:
- Learning multi-agent systems for the first time
- Using tools other than Claude Code (ChatGPT, etc.)
- Have 1-3 agents total
- Want to manually control every step

**🤖 Fully Automated** when you:
- Have 5+ agents needing true parallelization
- Built custom orchestration tooling
- Need CI/CD integration
- Have budget for parallel API calls
- Understand coordination patterns deeply

**Recommended Path**:
1. **Start**: Human-Coordinated (learn the patterns)
2. **Move to**: Task Tool Delegation (most projects - best balance)
3. **Advanced**: Fully Automated (only if you need true parallel execution)

The library supports all three models equally well.

---

## Key Concepts

### Context Engineering

Based on the [Context Engineering Guide](Context_Engineering.md), this library implements:

- **Multi-tier memory** - Never lose critical information
- **Progressive compression** - Manage context window efficiently
- **Checkpointing** - Resume from failures
- **RAG integration** - Long-term project memory

### Communication Protocol

Agents use structured JSON for coordination via **three complementary state files**:

**Within-Session Communication** (`.ai-agents/state/team-communication.json`):
- **Task assignments** - Manager → Agent
- **Status updates** - Agent → Manager
- **Blocker reports** - Agent → Manager
- **Integration requests** - Agent → Agent (via Manager)
- **Code reviews** - Manager → Agent

**Cross-Session Tracking** (`.ai-agents/state/session-progress.json`):
- Current project phase
- Completed vs. active tasks
- Blockers and priorities
- Git baseline for resumption

**Feature Verification** (`.ai-agents/state/feature-tracking.json`):
- Feature ID, description, status
- Test files and pass/fail status
- Verification history
- Progress metrics

See [schemas/communication-protocol.json](schemas/communication-protocol.json) for message formats and [docs/guides/LONG_RUNNING_AGENTS.md](docs/guides/LONG_RUNNING_AGENTS.md) for workflow examples.

### Branch Isolation

Prevents conflicts through git branch strategy:

```
feature/<name>/agent/<role>/<task>

✓ feature/auth/agent/frontend-dev/login-form
✓ feature/auth/agent/backend-dev/jwt-service
```

---

## Advanced Features

### Composition Script

Automatically assembles agents from components:

```bash
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent frontend_developer \
  --output .ai-agents/composed
```

### State Management

Central project state in `.ai-agents/state/project-state.json`:

```json
{
  "active_tasks": [...],
  "agent_states": {...},
  "shared_resources": {...},
  "metrics": {...}
}
```

### Memory & RAG

Long-term memory for:
- Architectural decisions (ADRs)
- Code patterns
- Troubleshooting solutions
- Requirements

### Long-Running Agent Patterns

Based on Anthropic's research, AI_agents now supports multi-session projects with a **three-file state management system**:

#### State File System

**1. Real-Time Communication** (`.ai-agents/state/team-communication.json`):
- Live coordination between agents **within a single session**
- Task assignments (Manager → Agents)
- Status updates (Agents → Manager)
- Integration requests (Agent ↔ Agent)
- Cleared/reset between sessions

**2. Session Progress Tracking** (`.ai-agents/state/session-progress.json`):
- **Cross-session continuity** - resume work without rediscovery
- Tracks completed/active tasks across sessions
- Records blockers and priorities
- Maintains git baseline
- Reduces session startup time by 50%

**3. Feature Status Management** (`.ai-agents/state/feature-tracking.json`):
- Structured feature lists with pass/fail status
- Prevents premature "done" declarations
- Mandatory E2E testing for user-facing features
- Clear progress visibility (e.g., "6/8 features passing")

#### Additional Enhancements

**Environment Automation** (`init.sh`):
- IT Specialist generates project-specific setup scripts
- Automates dependency installation
- Ensures consistent environments
- Onboards new team members in minutes

**Security Framework** (`scripts/security_validator.py`):
- Three-layer defense-in-depth for autonomous execution
- Command allowlist
- Destructive pattern detection
- Filesystem scope restrictions

#### How They Work Together

- **Within session**: Agents use `team-communication.json` for real-time coordination
- **End of session**: Manager updates `session-progress.json` and `feature-tracking.json`
- **Next session**: Manager reads progress files first → skips redundant planning → 50% faster startup

**Simple Mode**: Uses `team-communication.json` only
**Complex Mode**: Uses all three state files for full project tracking

See [docs/guides/LONG_RUNNING_AGENTS.md](docs/guides/LONG_RUNNING_AGENTS.md) for complete guide with workflows and examples.

---

## Advanced Tool Use

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use), this library implements three optimization patterns:

### 1. Deferred Skill Loading (85% Token Reduction)

Instead of loading all skills at startup, skills are discovered on-demand:

```yaml
# config.yml - New format
agents:
  orchestrator:
    skills:
      always_loaded:
        - "core/skill-creator"      # Always needed
      deferred:
        - path: "testing/webapp-testing"
          triggers: ["test", "QA", "coverage"]
        - path: "communication/internal-comms"
          triggers: ["coordinate", "communicate"]
```

**How it works:**
- `always_loaded` skills are included in the agent prompt
- `deferred` skills are listed in a manifest with triggers
- When a trigger matches, the skill is loaded on-demand
- Result: 85% reduction in initial context tokens

See [tools/skill-search.md](tools/skill-search.md) for implementation details.

### 2. Prompt Caching (Cost Reduction)

Reduce API costs by caching stable prompt components:

```python
from scripts.orchestration.prompt_cache import CachedAnthropicClient

client = CachedAnthropicClient(api_key)
response, cache_info = client.call_with_cache(
    system_prompt=system_prompt,  # Cached
    messages=messages
)

print(f"Cache hit: {cache_info['cache_read_input_tokens']} tokens saved")
```

**Benefits:**
- Stable context (system prompts, tools) cached for 5 minutes
- Dynamic context (messages) always fresh
- Significant cost reduction on repeated calls

See [scripts/orchestration/prompt_cache.py](scripts/orchestration/prompt_cache.py).

### 3. Programmatic Tool Calling (37% Token Reduction)

Instead of N tool calls = N inference passes, Claude writes orchestration code:

```
Traditional:                    Programmatic:
┌─────────────────────┐        ┌─────────────────────┐
│ Tool call 1         │        │ Claude generates    │
│ → Result in context │        │ Python code         │
│ Tool call 2         │        │       ↓             │
│ → Result in context │        │ Sandbox executes:   │
│ Tool call 3         │        │ - call tool 1       │
│ → Result in context │        │ - call tool 2       │
│ ...N times...       │        │ - process results   │
│                     │        │ - return summary    │
│ Context: 50KB+      │        │ Context: 1KB        │
└─────────────────────┘        └─────────────────────┘
```

**Run the demo:**
```bash
python3 scripts/orchestration/sandbox_executor.py
```

**Key features:**
- Secure sandbox (no imports, no file access, no network)
- Tool injection - only registered tools available
- Timeout protection
- Only final `result` returned to model

See [docs/PROGRAMMATIC_TOOL_CALLING.md](docs/PROGRAMMATIC_TOOL_CALLING.md) for complete guide.

### Quick Comparison

| Pattern | Token Savings | Best For |
|---------|--------------|----------|
| Deferred Loading | 85% initial | Large skill libraries |
| Prompt Caching | API cost | Repeated operations |
| Programmatic Calls | 37% per workflow | Multi-tool orchestration |

---

## XML Prompt Architecture

All agent prompts and skills now use pure XML structure for improved parsing and token efficiency.

### Benefits

- **25% Token Reduction**: XML is more compact than markdown with nested structures
- **Better Parsing**: LLMs parse XML structure more reliably
- **Consistent Structure**: Enforced schema across all prompts
- **Easier Composition**: XML elements compose cleanly

### Structure Example

```xml
<agent>
  <identity>
    <role>Backend Developer</role>
    <expertise>
      <item>REST API design</item>
      <item>Database optimization</item>
    </expertise>
  </identity>

  <capabilities>
    <capability name="api-development">
      <description>Design and implement RESTful APIs</description>
      <best-practices>
        <practice>Use semantic HTTP methods</practice>
        <practice>Implement proper error handling</practice>
      </best-practices>
    </capability>
  </capabilities>

  <workflows>
    <workflow name="feature-implementation">
      <step order="1">Read requirements from task description</step>
      <step order="2">Design API endpoints</step>
      <step order="3">Implement with tests</step>
    </workflow>
  </workflows>
</agent>
```

### Migration from Markdown

All prompts in `.claude/` and `skills/taches-cc/` use XML format:

- **Before (Markdown)**:
  ```markdown
  # Agent Identity
  Role: Backend Developer

  ## Expertise
  - REST API design
  - Database optimization
  ```

- **After (XML)**:
  ```xml
  <agent>
    <identity>
      <role>Backend Developer</role>
      <expertise>
        <item>REST API design</item>
        <item>Database optimization</item>
      </expertise>
    </identity>
  </agent>
  ```

**Token Comparison**: XML version uses ~25% fewer tokens for the same semantic content.

### Compatibility

- **Legacy Prompts**: Existing markdown prompts in `prompts/roles/`, `platforms/`, and `prompts/` continue to work
- **New Features**: All new slash commands, auditors, and taches-cc skills use XML
- **Migration Tool**: Coming in v1.3.0 - automatic markdown-to-XML converter

---

## Prerequisites

- Python 3.8+ (for composition script)
- PyYAML (`pip install pyyaml`)
- Git
- LLM provider (Claude, GPT-4, etc.)

---

## FAQ

**Q: Do I need all the agents?**
A: No, start with just one developer agent and add others as needed.

**Q: Can I use this with GPT-4?**
A: Yes, the prompts work with any LLM. Just adjust model parameters in config.

**Q: How do agents avoid conflicts?**
A: Through branch isolation and resource locking managed by the project state.

**Q: What if an agent loses context?**
A: Checkpointing and multi-tier memory ensure critical info is preserved.

**Q: Can I customize the base prompts?**
A: Yes, fork the repo and modify. Better: use project context to add requirements.

**Q: How do I update to newer library versions?**
A: Update the submodule and test. Use semantic versioning to manage compatibility.

---

## Best Practices

1. **Start Simple** - Begin with one agent, add more as needed
2. **Define Interfaces First** - API contracts before implementation
3. **Choose Skills Strategically** - Assign 1-3 skills per agent based on role (see [SKILLS_GUIDE.md](SKILLS_GUIDE.md))
4. **Use Branch Isolation** - One branch per agent per task
5. **Monitor Context** - Watch for context usage warnings, especially with skills
6. **Regular Checkpoints** - Every 10 turns or at 75% context
7. **Quality Gates** - Enforce tests, reviews, coverage
8. **Structured Communication** - Use JSON message protocol
9. **Track Skill Effectiveness** - Monitor which skills are actually used and improve outcomes

---

## Roadmap

### ✅ Phase 1: Skills Integration (COMPLETE)

- [x] **Skills integration with Anthropic Skills repository** (Phase 1-5 complete!)
- [x] **Comprehensive skills documentation and guides** (45,000+ words)
- [x] **Token budget management with skills** (Automatic warnings)
- [x] **Custom skills framework and templates** (Template + 5 examples)
- [x] **Example projects showcasing skills usage** (3 complete examples)
- [x] **Parallel execution guide** (Multi-agent optimization strategies)

### ✅ Phase 1.5: Advanced Tool Use (COMPLETE)

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use):

- [x] **Deferred Skill Loading** - 85% token reduction on initial context
- [x] **Prompt Caching** - Cost reduction via `cache_control` blocks
- [x] **Programmatic Tool Calling** - 37% token reduction, single inference pass
- [x] **Tool Use Examples** - Concrete examples for 72% → 90% parameter accuracy
- [x] **Secure Sandbox Executor** - Safe code execution with restricted builtins
- [x] **Agent Schema v2.0** - `defer_loading`, `allowed_callers`, `input_examples`

### ✅ Phase 1.6: taches-cc Integration (COMPLETE)

Integration of [taches-cc-resources](https://github.com/Tachesmkp/taches-cc-resources) for enhanced workflows:

- [x] **Slash Commands** - 12 thinking model commands (`/consider:*`)
- [x] **Workflow Commands** - `/whats-next`, `/debug`, task management commands
- [x] **Quality Auditor Agents** - skill-auditor, slash-command-auditor, subagent-auditor
- [x] **XML Prompt Format** - Pure XML structure with 25% token efficiency improvement
- [x] **taches-cc Skills** - create-agent-skills, create-plans, debug-like-expert
- [x] **Thinking Frameworks** - First-principles, 5-whys, SWOT, cost-benefit, and 8 more

### ✅ Phase 1.7: Tool Selector (COMPLETE)

Cross-project tool access system:

- [x] **setup-commands.py** - Auto-generate wrapper commands for target projects
- [x] **/ai-tools router** - Discovery command for available tools
- [x] **Minimal wrappers** - ~200-300 bytes each, +60 tokens per invocation
- [x] **Token efficiency** - Negligible at-rest cost (~50 tokens for 30 commands)
- [x] **Global install** - Option to install tools globally for all projects

### 🚀 Phase 2: Platform Expansion (Near-term: 3-6 months)

#### Platform Augmentations
- [ ] **Desktop Platform** - Electron, Qt, native desktop development
- [ ] **Data Platform** - Data engineering, ML pipelines, analytics
- [ ] **DevOps Platform** - Infrastructure, CI/CD, cloud operations
- [ ] **Embedded Platform** - IoT, firmware, real-time systems

#### Skills Enhancement
- [x] **Lazy loading for skills** - On-demand activation based on task context ✅ (Phase 1.5)
- [ ] **Skill versioning system** - Semantic versioning with compatibility tracking
- [ ] **Skill composition** - Combine multiple skills into meta-skills
- [ ] **Skills marketplace/registry** - Community-contributed skills catalog

### 🔬 Phase 3: Quality & Testing (Mid-term: 6-12 months)

#### Testing & Validation
- [ ] **Automated testing for prompts** - Unit tests for agent behaviors
- [ ] **Agent performance analytics** - Track skill usage, success rates, token efficiency
- [ ] **Regression testing suite** - Ensure skills work across LLM versions
- [ ] **Prompt optimization tools** - A/B testing for agent prompts

#### Context Management
- [ ] **Advanced context compression** - Progressive summarization strategies
- [ ] **Long-term memory systems** - RAG integration with vector databases
- [ ] **Cross-session persistence** - Resume agent work across sessions
- [ ] **Memory prioritization** - Smart retention of critical context

### 🎨 Phase 4: Developer Experience (Mid-term: 6-12 months)

#### Tooling & Interfaces
- [ ] **Interactive skill builder** - CLI tool for creating custom skills with prompts
- [ ] **Visual workflow designer** - Drag-and-drop agent workflow creation
- [ ] **Web dashboard** - Visual interface for managing agents and monitoring
- [ ] **VS Code extension** - IDE integration for agent development
- [ ] **Agent templates library** - Pre-configured personas for common roles

#### Integration & Deployment
- [ ] **CI/CD integration** - GitHub Actions for agent testing and deployment
- [ ] **Docker containers** - Containerized agent deployments
- [ ] **API gateway** - RESTful API for agent orchestration
- [ ] **Webhook support** - Event-driven agent activation

### 🌐 Phase 5: Multi-LLM & Scale (Long-term: 12-18 months)

#### LLM Providers
- [ ] **OpenAI GPT integration** - Native support for GPT-4, GPT-4-turbo
- [ ] **Google Gemini integration** - Support for Gemini Pro and Ultra
- [ ] **Local model support** - LLaMA, Mistral, Phi via Ollama
- [ ] **Multi-LLM orchestration** - Heterogeneous agent teams (Claude + GPT + local)
- [ ] **Cost optimization** - Smart routing based on task complexity and cost

#### Enterprise Features
- [ ] **Team collaboration** - Multi-user agent management
- [ ] **Access control** - Role-based permissions for agents
- [ ] **Audit logging** - Track all agent actions and decisions
- [ ] **Compliance tools** - GDPR, SOC2 compliance helpers
- [ ] **SLA monitoring** - Response time and availability tracking

### 📊 Phase 6: Observability & Intelligence (Long-term: 18-24 months)

#### Analytics & Monitoring
- [ ] **Metrics dashboard** - Real-time agent performance metrics
- [ ] **Cost tracking** - Token usage and API cost analysis
- [ ] **Success rate monitoring** - Task completion and quality metrics
- [ ] **Bottleneck detection** - Identify coordination issues
- [ ] **Skill effectiveness scoring** - Which skills improve outcomes

#### Advanced Capabilities
- [ ] **Self-improving agents** - Learn from past interactions
- [ ] **Dynamic skill discovery** - Agents request new skills as needed
- [ ] **Agent specialization** - Automatic role optimization based on performance
- [ ] **Cross-project learning** - Share knowledge between agent teams
- [ ] **Predictive task routing** - ML-based agent assignment

### 🔮 Phase 7: Research & Innovation (Long-term: 24+ months)

#### Experimental Features
- [ ] **Agent swarm intelligence** - Emergent behaviors from agent collectives
- [ ] **Autonomous architecture** - Agents design their own team structures
- [ ] **Meta-learning systems** - Agents that learn how to learn
- [ ] **Natural language orchestration** - Manage teams through conversation
- [ ] **Blockchain integration** - Decentralized agent coordination

#### Research Areas
- [ ] **Prompt evolution algorithms** - Genetic algorithms for prompt optimization
- [ ] **Multi-modal agents** - Vision, audio, and text integration
- [ ] **Formal verification** - Prove agent behavior correctness
- [ ] **Causal reasoning** - Agents that understand cause-effect relationships
- [ ] **Ethical AI frameworks** - Built-in fairness and safety guardrails

---

### 🎯 Current Focus

**Q4 2024 - Q1 2025**: Platform augmentations (Desktop, Data, DevOps) and migration tooling

**What's New in v1.3.0:**
- Tool Selector system for cross-project tool access via `/command` style
- `/ai-tools` discovery command for exploring available tools
- `setup-commands.py` script for installing wrappers to other projects
- Minimal token overhead (~50 tokens at-rest, +60 per invocation)

**What's New in v1.2.0:**
- 12 thinking model slash commands for structured decision-making
- Quality auditor agents for skills, commands, and agent validation
- XML-based prompt architecture (25% token efficiency)
- taches-cc skills integration (create-agent-skills, create-plans, debug-like-expert)
- Enhanced workflow commands for context handoff and debugging

**Community Contributions Welcome!** See [Contributing](#contributing) section for how to help.

### 📝 Suggesting New Features

Have ideas for the roadmap? We'd love to hear them!
- Open an issue with the `enhancement` label
- Join discussions in GitHub Discussions
- Submit a PR with a proof-of-concept

---

---

## Contributing

Contributions welcome! Please:

1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Follow existing conventions
3. Test with example projects
4. Update documentation
5. Submit PR with clear description

---

## License

[MIT License](LICENSE)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/AI_agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/AI_agents/discussions)
- **Documentation**: This repository

---

## Credits

Built with principles from the [Context Engineering Guide](Context_Engineering.md).

---

**Ready to get started?** Check out the [examples/](examples/) directory for complete working configurations!
