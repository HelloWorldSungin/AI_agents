# AI Agents Library

A comprehensive, modular library for building multi-agent software development systems based on advanced context engineering principles.

**Version:** 1.0.0

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

---

## Quick Start

### For Existing Projects (Recommended - 5 Minutes)

Use our **starter templates** to quickly set up AI agents in your existing project:

```bash
# Navigate to your project
cd your-project

# Run the template generator
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive

# Or use command line directly
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

**What you get:**
- ✅ Complete `.ai-agents/` directory structure
- ✅ Pre-configured context files (architecture, API contracts, coding standards)
- ✅ Ready-to-use agent configurations
- ✅ Comprehensive documentation

**Available templates:**
- `web-app` - Full-stack web applications (React + Node.js)
- `mobile-app` - Mobile applications (React Native, Flutter, native)
- `full-stack` - Complex multi-service systems
- `api-service` - Backend API services
- `data-pipeline` - Data processing pipelines

See [starter-templates/README.md](starter-templates/README.md) for complete guide.

---

### For New Projects (Manual Setup)

### 1. Use This Library in Your Project

```bash
# Add as git submodule (recommended)
cd your-project
git submodule add https://github.com/your-org/AI_agents.git .ai-agents/library

# Or clone directly
git clone https://github.com/your-org/AI_agents.git .ai-agents/library
```

### 2. Create Project Structure

```bash
mkdir -p .ai-agents/{context,state,checkpoints,memory,workflows,composed}
```

### 3. Create Configuration

Copy an example configuration:

```bash
cp .ai-agents/library/examples/web-app-team/config.yml .ai-agents/config.yml
```

Edit `.ai-agents/config.yml` to match your project.

### 4. Create Context Files

Create these in `.ai-agents/context/`:

- `architecture.md` - Your system architecture
- `coding-standards.md` - Your team conventions
- `api-contracts.md` - Your API specifications
- `current-features.md` - Feature roadmap

See [examples/](examples/) for templates or use [starter-templates/](starter-templates/) for ready-made templates.

### 5. Compose Your Agents

```bash
cd .ai-agents/library
python scripts/compose-agent.py --config ../../config.yml --all
```

This generates complete agent prompts in `.ai-agents/composed/`.

### 6. Deploy

Use the composed prompts to initialize your AI agents with your LLM provider.

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
├── base/                    # Base agent prompts
│   ├── software-developer.md
│   ├── manager.md
│   ├── qa-tester.md
│   ├── architect.md
│   └── scrum-master.md      # Optional: Project tracking & visibility
│
├── prompts/                 # Manager & specialized agent prompts ✨ NEW
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
│   └── custom/              # Project-specific skills
│       └── appflowy-integration/  # AppFlowy task tracking (for Scrum Master)
│
├── starter-templates/       # Project templates 🚀 NEW
│   ├── generate-template.py # Template generator
│   ├── web-app/            # Web application template
│   ├── mobile-app/         # Mobile app template
│   └── README.md           # Template documentation
│
├── schemas/                 # JSON schemas
│   ├── communication-protocol.json
│   ├── state-management.json
│   ├── agent-schema.json
│   └── project-config.json
│
├── tools/                   # Tool definitions
├── workflows/               # Multi-agent patterns
├── examples/                # Example configurations
├── scripts/                 # Automation tools
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
    base: "base/manager.md"

  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "core/artifacts-builder"
      - "design/theme-factory"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/api-contracts.md"

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      - "core/mcp-builder"
```

See [examples/web-app-team/](examples/web-app-team/) for complete example.

### Mobile Application Team

See [examples/mobile-app-team/](examples/mobile-app-team/) for React Native example.

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

Agents use structured JSON messages:

- **Task assignments** - Manager → Agent
- **Status updates** - Agent → Manager
- **Blocker reports** - Agent → Manager
- **Dependency requests** - Agent → Agent (via Manager)
- **Code reviews** - Manager → Agent

See [schemas/communication-protocol.json](schemas/communication-protocol.json).

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

### 🚀 Phase 2: Platform Expansion (Near-term: 3-6 months)

#### Platform Augmentations
- [ ] **Desktop Platform** - Electron, Qt, native desktop development
- [ ] **Data Platform** - Data engineering, ML pipelines, analytics
- [ ] **DevOps Platform** - Infrastructure, CI/CD, cloud operations
- [ ] **Embedded Platform** - IoT, firmware, real-time systems

#### Skills Enhancement
- [ ] **Lazy loading for skills** - On-demand activation based on task context
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

**Q4 2025**: Platform augmentations (Desktop, Data, DevOps) and lazy loading for skills

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
