# AI Agents Library - Cheat Sheet

Quick reference for all features, commands, skills, and agents in this repository.

**Version:** 1.2.0
**Last Updated:** 2025-11-25

---

## Quick Start Commands

```bash
# Option A: Generate from starter template (fastest)
python3 starter-templates/generate-template.py --interactive

# Option B: Add as git submodule (stays updated)
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library

# Option C: Direct copy (full control)
cp -r path/to/AI_agents .ai-agents/

# Compose agents from config
cd .ai-agents/library
python scripts/compose-agent.py --config ../config.yml --all
```

---

## Slash Commands

### Thinking Models (`/consider:*`)

12 mental models for systematic thinking and decision-making:

| Command | Purpose |
|---------|---------|
| `/consider:first-principles` | Break down to fundamentals and rebuild from base truths |
| `/consider:5-whys` | Root cause analysis - ask "why" 5 times |
| `/consider:second-order` | Examine consequences of consequences |
| `/consider:inversion` | Solve by considering the opposite |
| `/consider:occams-razor` | Prefer the simplest explanation |
| `/consider:pareto` | Find the vital 20% that drives 80% of results |
| `/consider:eisenhower-matrix` | Prioritize by urgent/important |
| `/consider:opportunity-cost` | What you give up by choosing this |
| `/consider:via-negativa` | Improve by removing rather than adding |
| `/consider:swot` | Analyze strengths, weaknesses, opportunities, threats |
| `/consider:one-thing` | Identify the single most important action |
| `/consider:10-10-10` | Evaluate decisions at 10min, 10months, 10years |

**Location:** `.claude/commands/consider/`

### Workflow Commands

| Command | Purpose | Location |
|---------|---------|----------|
| `/whats-next` | Create comprehensive context handoff document for continuing work in fresh session | `.claude/commands/whats-next.md` |
| `/debug` | Apply expert debugging methodology (loads `debug-like-expert` skill) | `.claude/commands/debug.md` |
| `/add-to-todos` | Capture tasks without derailing current focus | `.claude/commands/add-to-todos.md` |
| `/check-todos` | Review pending tasks and priorities | `.claude/commands/check-todos.md` |

---

## Agent Prompts

### Manager Workflow (NEW v1.1.0)

| Prompt | Purpose | Mode | Location |
|--------|---------|------|----------|
| `manager-task-delegation.md` | Full Manager guide with dual-mode workflow | Simple/Complex | `prompts/manager-task-delegation.md` |
| `manager-quick-reference.md` | Quick-start copy-paste templates | Quick reference | `prompts/manager-quick-reference.md` |

**Workflow Modes:**
- **Simple Mode** (90% of projects): Manager → Task Agents → Integration Agent
- **Complex Mode** (10% of projects): Manager → IT Specialist → Task Agents → Senior Engineer

### Specialized Agents (NEW v1.1.0)

| Prompt | Purpose | Key Features | Location |
|--------|---------|--------------|----------|
| `it-specialist-agent.md` | Infrastructure validation specialist | 8 critical infrastructure checks before development | `prompts/it-specialist-agent.md` |
| `senior-engineer-agent.md` | Code review & integration specialist | Enforces standards, reviews code, merges branches | `prompts/senior-engineer-agent.md` |

### Base Agents

Core agent templates that work across all projects:

| Agent | Purpose | Location |
|-------|---------|----------|
| `software-developer.md` | Universal software development agent | `base/software-developer.md` |
| `manager.md` | Multi-agent team orchestration | `base/manager.md` |
| `qa-tester.md` | Testing and quality assurance | `base/qa-tester.md` |
| `architect.md` | System design and architecture | `base/architect.md` |
| `scrum-master.md` | Optional project tracking & visibility (AppFlowy integration) | `base/scrum-master.md` |

---

## Skills Library

### Anthropic Skills (`skills/anthropic/`)

13 official Anthropic skills integrated as git submodule:

#### Core Development Skills

| Skill | Purpose | Token Est. | Best For |
|-------|---------|------------|----------|
| `web-artifacts-builder` | Build interactive web components with React + Tailwind | ~3,500 | Frontend Dev |
| `webapp-testing` | End-to-end testing with Playwright | ~4,000 | QA Tester |
| `mcp-builder` | Build Model Context Protocol servers (Python/TypeScript) | ~4,500 | Backend Dev |
| `skill-creator` | Create new Claude Code skills | ~3,000 | Any agent |

#### Document Skills

| Skill | Purpose | Token Est. |
|-------|---------|------------|
| `document-skills/pdf` | PDF processing and generation | ~3,500 |
| `document-skills/docx` | Word document creation (OOXML) | ~4,000 |
| `document-skills/pptx` | PowerPoint generation | ~4,200 |
| `document-skills/xlsx` | Excel spreadsheet manipulation | ~3,800 |

#### Design & Creative Skills

| Skill | Purpose | Token Est. |
|-------|---------|------------|
| `frontend-design` | Modern UI/UX design with Tailwind + shadcn/ui | ~3,200 |
| `theme-factory` | 10 pre-built design themes (midnight-galaxy, ocean-depths, etc.) | ~2,500 |
| `canvas-design` | Interactive canvas-based design | ~3,000 |
| `algorithmic-art` | Generative art and visualizations | ~2,800 |

#### Communication Skills

| Skill | Purpose | Token Est. |
|-------|---------|------------|
| `internal-comms` | Internal communications (newsletters, updates, FAQs) | ~3,500 |
| `brand-guidelines` | Brand consistency and style guides | ~2,800 |
| `slack-gif-creator` | Create animated GIFs for Slack | ~2,200 |

**License:** Apache 2.0 (see `skills/anthropic/THIRD_PARTY_NOTICES.md`)

### Taches-CC Skills (`skills/taches-cc/`)

3 advanced workflow skills from Taches-CC community:

| Skill | Purpose | Key Features | Location |
|-------|---------|--------------|----------|
| `create-plans` | Hierarchical project planning for solo+Claude development | Atomic tasks, verification criteria, context handoffs, 50% scope control | `skills/taches-cc/create-plans/` |
| `debug-like-expert` | Expert debugging methodology | Evidence gathering, hypothesis testing, rigorous verification, domain expertise detection | `skills/taches-cc/debug-like-expert/` |
| `create-agent-skills` | Skill authoring best practices | Router pattern, XML structure, workflow organization | `skills/taches-cc/create-agent-skills/` |

**Features:**
- `create-plans`: 11 workflows, 11 references, 8 templates (briefs, roadmaps, phases, milestones)
- `debug-like-expert`: 5 references (debugging mindset, hypothesis testing, investigation techniques)
- `create-agent-skills`: 5 references (XML structure, skill structure, using templates/scripts)

### Custom Skills (`skills/custom/`)

Project-specific skills and templates:

| Skill | Purpose | Location |
|-------|---------|----------|
| `appflowy-integration` | AppFlowy task tracking for Scrum Master agent | `skills/custom/appflowy-integration/` |
| `template` | Template for creating custom skills | `skills/custom/template/` |

**Quick Start:** See `skills/custom/QUICK_START.md` for creating custom skills

---

## Quality Auditors

Agents that review other agents and ensure best practices:

| Agent | Purpose | Use When | Location |
|-------|---------|----------|----------|
| `skill-auditor` | Review skills for best practices, XML structure, token efficiency | After creating/modifying skills | `.claude/agents/skill-auditor.md` |
| `slash-command-auditor` | Review command structure, frontmatter, descriptions | After creating slash commands | `.claude/agents/slash-command-auditor.md` |
| `subagent-auditor` | Review agent configurations, role clarity, success criteria | After creating/composing agents | `.claude/agents/subagent-auditor.md` |

---

## Platform Augmentations

Specialized knowledge for different platforms:

| Platform | Files | Best For | Location |
|----------|-------|----------|----------|
| Web Frontend | `frontend-developer.md` | React, Vue, Angular, modern web apps | `platforms/web/frontend-developer.md` |
| Web Backend | `backend-developer.md` | Node.js, Python, Go, API services | `platforms/web/backend-developer.md` |
| Mobile | `mobile-developer.md` | React Native, Flutter, native iOS/Android | `platforms/mobile/mobile-developer.md` |

**Future:** Desktop (Electron, Qt), Data (ML pipelines), DevOps (CI/CD), Embedded (IoT) coming in Phase 2

---

## Workflow Modes

### Simple Mode (90% of projects)

```
Manager → Task Agents → Integration Agent
```

**Use for:**
- Established projects with existing infrastructure
- 1-3 agents
- Clear requirements
- Straightforward features

**Example flow:**
1. Manager breaks down task
2. Delegates to specialized agents (frontend, backend, QA)
3. Integration agent merges work when complete

### Complex Mode (10% of projects)

```
Manager → IT Specialist → Task Agents → Senior Engineer
```

**Use for:**
- New projects needing infrastructure setup
- 5+ agents
- Complex architecture requiring validation
- Code review required
- First features requiring infrastructure

**Example flow:**
1. Manager coordinates overall strategy
2. IT Specialist validates infrastructure (8 checks)
3. Task agents work on features
4. Senior Engineer reviews code and integrates

### Optional: With Scrum Master

Add project tracking and visibility:

```
Manager → [Scrum Master Setup] → IT Specialist → Task Agents → Senior Engineer
             ↓
    [AppFlowy Tracking + Daily Summaries]
```

**Use when:**
- External stakeholders need visibility
- Sprint velocity tracking required
- Daily standup summaries needed
- AppFlowy server available

---

## Starter Templates

Quick-start templates for existing projects (NEW v1.1.0):

| Template | Best For | Command | Location |
|----------|----------|---------|----------|
| `web-app` | Full-stack web apps (React/Vue + Node/Python) | `--type web-app` | `starter-templates/web-app/` |
| `mobile-app` | Mobile apps (React Native, Flutter, native) | `--type mobile-app` | `starter-templates/mobile-app/` |
| `full-stack` | Complete full-stack with multiple services | `--type full-stack` | `starter-templates/full-stack/` |
| `api-service` | Backend API service or microservice | `--type api-service` | `starter-templates/api-service/` |
| `data-pipeline` | Data processing or analytics project | `--type data-pipeline` | `starter-templates/data-pipeline/` |

**Interactive mode:**
```bash
cd your-project
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive
```

**Direct mode:**
```bash
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

**What you get:**
- Complete `.ai-agents/` directory structure
- Pre-configured context files (architecture, API contracts, coding standards)
- Ready-to-use agent configurations
- Example config.yml

---

## Scripts & Tools

### Core Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `compose-agent.py` | Compose agents from components (base + platform + context + skills) | `scripts/compose-agent.py` |
| `generate-template.py` | Generate starter templates for existing projects | `starter-templates/generate-template.py` |

### Orchestration Scripts (Advanced Tool Use - NEW v1.1.0)

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use):

| Script | Purpose | Token Savings | Location |
|--------|---------|---------------|----------|
| `simple_orchestrator.py` | Basic multi-agent orchestration via API | N/A | `scripts/orchestration/simple_orchestrator.py` |
| `prompt_cache.py` | Prompt caching for cost reduction | API cost savings | `scripts/orchestration/prompt_cache.py` |
| `sandbox_executor.py` | Secure code execution sandbox | 37% per workflow | `scripts/orchestration/sandbox_executor.py` |
| `programmatic_orchestrator.py` | Programmatic tool calling | 37% reduction | `scripts/orchestration/programmatic_orchestrator.py` |
| `file_based_orchestrator.py` | File-based agent coordination | N/A | `scripts/orchestration/file_based_orchestrator.py` |
| `custom_orchestrator_example.py` | Custom orchestration patterns | N/A | `scripts/orchestration/custom_orchestrator_example.py` |

**Run demos:**
```bash
# Test sandbox executor
python3 scripts/orchestration/sandbox_executor.py

# Run simple orchestrator
python3 scripts/orchestration/simple_orchestrator.py
```

---

## Advanced Tool Use (NEW v1.1.0)

Three optimization patterns from Anthropic's research:

### 1. Deferred Skill Loading (85% Token Reduction)

Skills loaded on-demand via trigger words instead of all at startup.

**Config format:**
```yaml
agents:
  developer:
    skills:
      always_loaded:
        - "core/skill-creator"
      deferred:
        - path: "testing/webapp-testing"
          triggers: ["test", "QA", "coverage"]
```

**Tool:** `tools/skill-search.md`

### 2. Prompt Caching (Cost Reduction)

Cache stable prompt components for 5 minutes, only send dynamic parts.

**Usage:**
```python
from scripts.orchestration.prompt_cache import CachedAnthropicClient

client = CachedAnthropicClient(api_key)
response, cache_info = client.call_with_cache(
    system_prompt=system_prompt,  # Cached
    messages=messages             # Fresh
)
```

**Script:** `scripts/orchestration/prompt_cache.py`

### 3. Programmatic Tool Calling (37% Token Reduction)

Claude generates Python code that executes multiple tool calls in one inference pass.

**Traditional:** N tool calls = N inference passes + N results in context
**Programmatic:** 1 inference pass → sandbox executes code → 1 summary result

**Script:** `scripts/orchestration/sandbox_executor.py`
**Guide:** `docs/PROGRAMMATIC_TOOL_CALLING.md`

---

## File Locations

| What | Where |
|------|-------|
| Slash commands | `.claude/commands/` |
| Thinking models | `.claude/commands/consider/` |
| Auditor agents | `.claude/agents/` |
| Manager prompts | `prompts/` |
| Base agents | `base/` |
| Platform augments | `platforms/` |
| Anthropic skills | `skills/anthropic/` (git submodule) |
| Taches-CC skills | `skills/taches-cc/` |
| Custom skills | `skills/custom/` |
| Starter templates | `starter-templates/` |
| Orchestration scripts | `scripts/orchestration/` |
| State files | `.ai-agents/state/` |
| Composed agents | `.ai-agents/composed/` |
| Project context | `.ai-agents/context/` |
| Examples | `examples/` |
| Schemas | `schemas/` |
| Tools | `tools/` |

---

## Key Documentation

### Essential Reading

| Doc | Purpose | Priority |
|-----|---------|----------|
| `README.md` | Quick start guide and overview | **START HERE** |
| `Context_Engineering.md` | Foundational principles (the "HOLY BIBLE") | **MUST READ** |
| `ARCHITECTURE.md` | System design and composition model | High |
| `SKILLS_GUIDE.md` | Skills selection, usage, best practices | High |

### Workflow Guides

| Doc | Purpose | When to Read |
|-----|---------|--------------|
| `PRACTICAL_WORKFLOW_GUIDE.md` | Human-coordinated multi-agent workflows | Before first multi-agent project |
| `PARALLEL_EXECUTION_GUIDE.md` | Multi-agent parallelization strategies | When scaling to 3+ agents |
| `prompts/manager-task-delegation.md` | Manager workflow (Simple/Complex modes) | When using Manager agent |
| `prompts/manager-quick-reference.md` | Quick-start Manager templates | Copy-paste for fast setup |

### Skills Documentation

| Doc | Purpose |
|-----|---------|
| `skills/README.md` | Skills integration overview |
| `skills/CATALOG.md` | Complete skills directory with descriptions |
| `skills/INTEGRATION.md` | Technical implementation guide |
| `skills/PROJECT_INTEGRATION.md` | Adding library to existing projects |
| `skills/CUSTOM_SKILLS_GUIDE.md` | Creating custom skills |
| `skills/custom/QUICK_START.md` | Quick-start for custom skills |

### Advanced Features

| Doc | Purpose |
|-----|---------|
| `docs/PROGRAMMATIC_TOOL_CALLING.md` | Programmatic orchestration guide (37% token reduction) |
| `scripts/orchestration/README.md` | Orchestration scripts overview |
| `scripts/orchestration/COMPLETE_GUIDE.md` | Complete orchestration guide |
| `starter-templates/README.md` | Starter templates guide |

### Reference

| Doc | Purpose |
|-----|---------|
| `FAQ.md` | Frequently asked questions |
| `MIGRATION_GUIDE.md` | Adding skills to existing projects |
| `TESTING_REPORT.md` | Testing results and validation |

---

## XML Structure (Best Practices)

All prompts and skills use pure XML structure for ~25% token efficiency:

```xml
<role>
Agent identity and persona
</role>

<objective>
What to accomplish
</objective>

<constraints>
<must>
- MUST follow requirement 1
- MUST NOT violate rule 2
</must>
</constraints>

<workflow>
<step number="1">Action to take</step>
<step number="2">Next action</step>
</workflow>

<quick_start>
Immediate actions when invoked
</quick_start>

<success_criteria>
- Completion condition 1
- Verification check 2
</success_criteria>
```

**Benefits:**
- ~25% token efficiency vs markdown headers
- Better parsing by LLMs
- Clear semantic structure
- Consistent across all prompts

**Tags used:**
- `<role>` - Agent identity
- `<objective>` - What to accomplish
- `<constraints>` - MUST/MUST NOT rules
- `<workflow>` - Step-by-step process
- `<quick_start>` - Immediate actions
- `<success_criteria>` - Completion conditions
- `<context>` - Background information
- `<examples>` - Usage examples
- `<output_format>` - Expected output structure

---

## Coordination Models

Three ways to implement multi-agent coordination:

### 1. Human-Coordinated (Practical Today)

**What:** You manually run agents in sequence and relay information.

**Best for:**
- 90% of users
- Learning multi-agent patterns
- Small teams (1-3 agents)
- Tools like Claude Code (one session at a time)

**Communication:** Agents write to `.ai-agents/state/team-communication.json`, you relay

**Guide:** `PRACTICAL_WORKFLOW_GUIDE.md`

### 2. Task Tool Delegation (Recommended - NEW v1.1.0)

**What:** Manager spawns agents using Claude Code's Task tool. Each agent gets fresh context.

**Best for:**
- Most users (best balance)
- Complex projects (5+ agents)
- Infrastructure setup and code review needed
- Keeping Manager context lean (15-25%)
- Zero API costs

**Communication:** Automatic via Task tool

**Guide:** `prompts/manager-task-delegation.md`

### 3. Fully Automated (Advanced)

**What:** Programmatic orchestration via LLM APIs with message queue.

**Best for:**
- Advanced users with programming experience
- Large-scale projects (5+ agents)
- CI/CD automation
- True parallel execution

**Communication:** Direct agent-to-agent via message queue

**Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`

**Quick comparison:**

| Aspect | Human-Coord | Task Tool | Automated |
|--------|-------------|-----------|-----------|
| Setup | Simple | Simple | Complex |
| Control | Full | Full | Less |
| Speed | Sequential | Sequential | Parallel |
| Context | No isolation | Fresh per agent | Fresh per agent |
| Cost | Lower | **No API costs** | Higher |
| Learning | Low | Low | High |

---

## Schemas & Protocols

JSON schemas for structured communication:

| Schema | Purpose | Location |
|--------|---------|----------|
| `communication-protocol.json` | Inter-agent messaging format | `schemas/communication-protocol.json` |
| `communication-protocol-examples.json` | Tool use examples (72% → 90% accuracy) | `schemas/communication-protocol-examples.json` |
| `state-management.json` | Project state format | `schemas/state-management.json` |
| `agent-schema.json` | Agent configuration v2.0 (deferred loading support) | `schemas/agent-schema.json` |
| `project-config.json` | Project configuration format | `schemas/project-config.json` |

**Message types:**
- Task assignments (Manager → Agent)
- Status updates (Agent → Manager)
- Blocker reports (Agent → Manager)
- Dependency requests (Agent → Agent via Manager)
- Code reviews (Manager → Agent)

---

## Best Practices

### General

1. **Start Simple** - Begin with one agent, add more as needed
2. **Define Interfaces First** - API contracts before implementation
3. **Use Branch Isolation** - One branch per agent per task
4. **Monitor Context** - Watch for context usage warnings, especially with skills
5. **Regular Checkpoints** - Every 10 turns or at 75% context
6. **Quality Gates** - Enforce tests, reviews, coverage
7. **Structured Communication** - Use JSON message protocol

### Skills

8. **Choose Skills Strategically** - Assign 1-3 skills per agent based on role
9. **Track Skill Effectiveness** - Monitor which skills improve outcomes
10. **Use Deferred Loading** - For large skill libraries (85% token reduction)
11. **Consider Token Budget** - Skills add ~2.5-4.5K tokens each

### Advanced

12. **Use Prompt Caching** - For repeated operations (cost reduction)
13. **Programmatic Tools** - For multi-step workflows (37% token reduction)
14. **Atomic Tasks** - Better 10 small plans than 3 large ones
15. **Fresh Context** - Use Task tool delegation to prevent Manager overflow

---

## Repository Statistics

- **Base Agents:** 5 (software-developer, manager, qa-tester, architect, scrum-master)
- **Manager Prompts:** 4 (task-delegation, quick-reference, it-specialist, senior-engineer)
- **Platform Augments:** 2 (web/frontend, mobile) + 3 planned (desktop, data, devops)
- **Slash Commands:** 16 total (12 thinking models + 4 workflow commands)
- **Quality Auditors:** 3 (skill-auditor, slash-command-auditor, subagent-auditor)
- **Anthropic Skills:** 13 official skills (~3-4.5K tokens each)
- **Taches-CC Skills:** 3 advanced workflow skills
- **Custom Skills:** 1 (appflowy-integration) + template
- **Starter Templates:** 5 (web-app, mobile-app, full-stack, api-service, data-pipeline)
- **Orchestration Scripts:** 6 Python scripts
- **Documentation:** 20+ markdown guides (45,000+ words)
- **Examples:** 3 complete examples (web-app-team, mobile-app-team, skills-showcase)

---

## Quick Decision Guide

### Which workflow mode?

- **Simple Mode**: Established project, 1-3 agents, clear requirements
- **Complex Mode**: New project, 5+ agents, infrastructure needs, code review required
- **With Scrum Master**: External visibility needed, sprint tracking, AppFlowy available

### Which coordination model?

- **Human-Coordinated**: Learning, small teams, Claude Code one-session-at-a-time
- **Task Tool Delegation**: Most projects, 5+ agents, need fresh context isolation
- **Fully Automated**: Advanced users, CI/CD, true parallel execution needed

### Which skills?

- **Frontend Dev**: `web-artifacts-builder`, `frontend-design`, `theme-factory`
- **Backend Dev**: `mcp-builder`, `skill-creator`
- **QA Tester**: `webapp-testing`
- **Any Agent**: `document-skills/*` for document generation
- **Manager**: `create-plans` for hierarchical planning
- **Debugging**: `debug-like-expert` skill

### Which starter template?

- **Web app** (React/Vue + Node/Python): `web-app`
- **Mobile** (React Native/Flutter): `mobile-app`
- **Multiple services**: `full-stack`
- **API only**: `api-service`
- **Data processing**: `data-pipeline`

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/HelloWorldSungin/AI_agents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HelloWorldSungin/AI_agents/discussions)
- **Documentation:** This repository
- **Start Here:** `README.md` → `Context_Engineering.md` → `ARCHITECTURE.md`

---

## Version History

- **v1.2.0** (Current): Advanced Tool Use features (deferred loading, prompt caching, programmatic tools)
- **v1.1.0**: Manager workflow dual-mode, IT Specialist, Senior Engineer, Starter Templates
- **v1.0.0**: Skills integration, base agents, platform augments, orchestration

---

**Ready to start?**

1. Choose a [starter template](#starter-templates) or integration approach
2. Read [README.md](README.md) for setup
3. Check [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) for workflows
4. Explore [examples/](examples/) for reference configurations

**Pro tip:** Bookmark this cheat sheet for quick reference during development!
