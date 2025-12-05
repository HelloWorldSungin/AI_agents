# AI Agents Library - Cheat Sheet

Quick reference for all features, commands, skills, and agents in this repository.

**Version:** 1.3.0
**Last Updated:** 2025-12-04

---

## Navigation

This cheat sheet is organized into focused components for easy reference:

### Core Concepts

1. **[Quick Start](00-quick-start.md)** - Installation, setup, getting help
2. **[State Files](01-state-files.md)** - Three-file state management system ⭐ NEW
3. **[Agents](02-agents.md)** - Agent prompts, specialists, base agents, auditors
4. **[Skills](03-skills.md)** - Skills library (Anthropic, Taches-CC, Custom)
5. **[Commands](04-commands.md)** - Slash commands, thinking models, workflows

### Implementation

6. **[Workflows](05-workflows.md)** - Workflow modes (Simple/Complex), coordination models
7. **[Scripts & Tools](06-scripts-tools.md)** - Scripts, starter templates, tool selector ⭐
8. **[Advanced](07-advanced.md)** - Token optimization, caching, programmatic tools

### Reference

9. **[Schemas](08-schemas.md)** - JSON schemas, protocols, validation ⭐ UPDATED
10. **[Best Practices](09-best-practices.md)** - Guidelines, XML structure, common pitfalls
11. **[Quick Reference](10-reference.md)** - File locations, stats, decision guides, versions

---

## What's New in This Update? 🎉

### Comprehensive Coverage
- ✅ **All new schemas documented** (session-progress, feature-tracking, security-policy)
- ✅ **All new docs referenced** (E2E_TESTING.md, LONG_RUNNING_AGENTS.md, SECURITY.md)
- ✅ **All new scripts included** (security_validator.py, init-scripts templates)
- ✅ **Session continuity examples** (examples/session-continuity/)

### Better Organization
- 📁 **Modular structure** - 11 focused components vs. 820-line monolith
- 🔍 **Easy to find** - Clear separation of concerns
- 🔗 **Cross-referenced** - Links between related topics
- 🎯 **Targeted reading** - Read only what you need

### Enhanced Navigation
- Each component is 60-150 lines (much more readable)
- Previous/Next navigation at bottom of each page
- Quick decision guides for common questions
- Complete index for fast lookup

---

## Quick Access

### By Task

| What You Want to Do | Go Here |
|---------------------|---------|
| **Get started quickly** | [00-quick-start.md](00-quick-start.md) |
| **Set up state files** | [01-state-files.md](01-state-files.md) |
| **Configure agents** | [02-agents.md](02-agents.md) |
| **Choose skills** | [03-skills.md](03-skills.md) |
| **Use thinking models** | [04-commands.md](04-commands.md#thinking-models) |
| **Decide workflow mode** | [05-workflows.md](05-workflows.md) |
| **Generate starter template** | [06-scripts-tools.md](06-scripts-tools.md#starter-templates) |
| **Optimize tokens** | [07-advanced.md](07-advanced.md) |
| **Validate state files** | [08-schemas.md](08-schemas.md) |
| **Learn best practices** | [09-best-practices.md](09-best-practices.md) |
| **Find file locations** | [10-reference.md](10-reference.md#file-locations) |

### By Role

| Your Role | Recommended Reading |
|-----------|---------------------|
| **New User** | [00-quick-start](00-quick-start.md) → [02-agents](02-agents.md) → [05-workflows](05-workflows.md) |
| **Manager Agent User** | [05-workflows](05-workflows.md) → [01-state-files](01-state-files.md) → [02-agents](02-agents.md#manager-workflow) |
| **Developer** | [02-agents](02-agents.md) → [03-skills](03-skills.md) → [09-best-practices](09-best-practices.md) |
| **QA Tester** | [02-agents](02-agents.md#base-agents) → [03-skills](03-skills.md) (webapp-testing) |
| **Advanced User** | [07-advanced](07-advanced.md) → [08-schemas](08-schemas.md) → [06-scripts-tools](06-scripts-tools.md#orchestration-scripts) |

### By Project Phase

| Phase | Start Here |
|-------|------------|
| **Planning** | [05-workflows](05-workflows.md#workflow-selection-guide) → [04-commands](04-commands.md#thinking-models) |
| **Setup** | [00-quick-start](00-quick-start.md) → [06-scripts-tools](06-scripts-tools.md#starter-templates) |
| **Development** | [02-agents](02-agents.md) → [03-skills](03-skills.md) → [01-state-files](01-state-files.md) |
| **Testing** | [08-schemas](08-schemas.md) → E2E_TESTING.md guide |
| **Optimization** | [07-advanced](07-advanced.md) → [09-best-practices](09-best-practices.md) |

---

## Quick Decision Trees

### Which Workflow Mode?

```
Do you have existing infrastructure?
├─ YES → Simple Mode
│   └─ See: 05-workflows.md#simple-mode
│
└─ NO → Complex Mode
    └─ See: 05-workflows.md#complex-mode
```

### Which State Files Do I Need?

```
Simple Mode (90% of projects)
└─ team-communication.json only
   └─ See: 01-state-files.md#simple-mode-setup

Complex Mode (10% of projects)
└─ All three files:
   ├─ team-communication.json (real-time)
   ├─ session-progress.json (continuity)
   └─ feature-tracking.json (verification)
   └─ See: 01-state-files.md#complex-mode-setup
```

### Which Coordination Model?

```
Learning or small teams (1-3 agents)
└─ Human-Coordinated
   └─ See: 05-workflows.md#1-human-coordinated-practical-today

Most production projects (3-7 agents)
└─ Task Tool Delegation (RECOMMENDED)
   └─ See: 05-workflows.md#2-task-tool-delegation-recommended---new-v110

Large-scale or CI/CD (7+ agents)
└─ Fully Automated
   └─ See: 05-workflows.md#3-fully-automated-advanced
```

---

## Featured Topics

### ⭐ Three-File State System (NEW)

The breakthrough pattern for long-running agent projects:

**[01-state-files.md](01-state-files.md)** covers:
- How the three files work together
- When to use each file
- Simple vs Complex Mode
- Setup examples
- Feature completion criteria

**Key Benefits:**
- 50% faster session resumption
- Mandatory E2E testing enforcement
- Progress metrics tracking
- Blocker documentation

### 🚀 Advanced Optimizations

Token reduction and cost efficiency patterns:

**[07-advanced.md](07-advanced.md)** covers:
- Deferred Skill Loading (85% reduction)
- Prompt Caching (cost savings)
- Programmatic Tool Calling (37% reduction)

**Impact:**
- ~85% token reduction with deferred loading
- ~37% token reduction with programmatic tools
- 50-90% API cost reduction with caching

### 🛠️ Tool Selector (NEW v1.3.0)

Access AI_agents tools from any project:

**[06-scripts-tools.md](06-scripts-tools.md#tool-selector-new-v130)** covers:
- Installation (local or global)
- Usage from other projects
- Token impact (~50 tokens at-rest)
- 30 wrapper commands available

### 🎯 Manager Workflow

Dual-mode workflow for 90% and 10% use cases:

**[02-agents.md](02-agents.md#manager-workflow)** and **[05-workflows.md](05-workflows.md)** cover:
- Simple Mode: Manager → Task Agents → Integration Agent
- Complex Mode: Manager → IT Specialist → Task Agents → Senior Engineer
- When to use each mode
- Complete workflow examples

---

## Essential External Guides

These guides complement the cheat sheet with detailed workflows:

| Guide | Purpose | When to Read |
|-------|---------|--------------|
| `docs/guides/LONG_RUNNING_AGENTS.md` | Complete long-running agent patterns | Complex Mode projects |
| `docs/guides/E2E_TESTING.md` | Comprehensive E2E testing workflow | Writing E2E tests |
| `docs/guides/SECURITY.md` | Security framework documentation | Autonomous execution |
| `docs/guides/PRACTICAL_WORKFLOW_GUIDE.md` | Human-coordinated workflows | First multi-agent project |
| `docs/guides/PARALLEL_EXECUTION_GUIDE.md` | Parallelization strategies | Scaling to 3+ agents |
| `prompts/manager-task-delegation.md` | Full Manager guide | Using Manager agent |
| `prompts/manager-quick-reference.md` | Quick-start templates | Copy-paste for speed |

---

## Search by Topic

### State Management
- Three-file system: [01-state-files.md](01-state-files.md)
- Schemas: [08-schemas.md](08-schemas.md)
- Session continuity: [01-state-files.md](01-state-files.md#2-session-progress)

### Agent Configuration
- Base agents: [02-agents.md](02-agents.md#base-agents)
- Specialized agents: [02-agents.md](02-agents.md#specialized-agents)
- Platform augments: [02-agents.md](02-agents.md#platform-augmentations)
- Quality auditors: [02-agents.md](02-agents.md#quality-auditors)

### Skills
- Anthropic skills: [03-skills.md](03-skills.md#anthropic-skills)
- Taches-CC skills: [03-skills.md](03-skills.md#taches-cc-skills)
- Custom skills: [03-skills.md](03-skills.md#custom-skills)
- Skill assignment: [03-skills.md](03-skills.md#skill-assignment-strategy)

### Commands
- Thinking models: [04-commands.md](04-commands.md#thinking-models)
- Workflow commands: [04-commands.md](04-commands.md#workflow-commands)
- Discovery: [04-commands.md](04-commands.md#discovery-command)

### Workflows
- Simple Mode: [05-workflows.md](05-workflows.md#simple-mode-90-of-projects)
- Complex Mode: [05-workflows.md](05-workflows.md#complex-mode-10-of-projects)
- Coordination: [05-workflows.md](05-workflows.md#coordination-models)

### Tools & Scripts
- Core scripts: [06-scripts-tools.md](06-scripts-tools.md#core-scripts)
- Orchestration: [06-scripts-tools.md](06-scripts-tools.md#orchestration-scripts)
- Starter templates: [06-scripts-tools.md](06-scripts-tools.md#starter-templates)
- Tool selector: [06-scripts-tools.md](06-scripts-tools.md#tool-selector-new-v130)
- Init scripts: [06-scripts-tools.md](06-scripts-tools.md#init-scripts-templates)
- Security: [06-scripts-tools.md](06-scripts-tools.md#core-scripts) (security_validator.py)

### Optimization
- Deferred loading: [07-advanced.md](07-advanced.md#1-deferred-skill-loading)
- Prompt caching: [07-advanced.md](07-advanced.md#2-prompt-caching)
- Programmatic tools: [07-advanced.md](07-advanced.md#3-programmatic-tool-calling)

### Best Practices
- General: [09-best-practices.md](09-best-practices.md#general-best-practices)
- Skills: [09-best-practices.md](09-best-practices.md#skills-best-practices)
- Advanced: [09-best-practices.md](09-best-practices.md#advanced-best-practices)
- XML: [09-best-practices.md](09-best-practices.md#xml-structure-best-practices)

---

## Component Overview

### 00-quick-start.md (50 lines)
Installation options, compose agents, getting help

### 01-state-files.md (170 lines) ⭐ NEW
Three-file state system, setup examples, feature completion criteria

### 02-agents.md (150 lines)
Manager workflow, specialized agents, base agents, platform augments, auditors

### 03-skills.md (180 lines)
Anthropic skills, Taches-CC skills, custom skills, assignment strategy

### 04-commands.md (140 lines)
Thinking models, workflow commands, discovery command, usage examples

### 05-workflows.md (180 lines)
Simple/Complex modes, coordination models, workflow selection guide

### 06-scripts-tools.md (190 lines) ⭐ UPDATED
Core scripts, orchestration, starter templates, tool selector, init scripts, security validator

### 07-advanced.md (150 lines)
Deferred loading, prompt caching, programmatic tool calling, combined patterns

### 08-schemas.md (180 lines) ⭐ UPDATED
Communication schemas, state management schemas (+ 3 new), configuration schemas, validation

### 09-best-practices.md (170 lines)
General practices, skills practices, advanced practices, XML structure, common pitfalls

### 10-reference.md (160 lines)
File locations, key documentation, repository statistics, decision guides, version history

---

## How to Use This Cheat Sheet

### First Time?
1. Start with [00-quick-start.md](00-quick-start.md)
2. Read [05-workflows.md](05-workflows.md) to choose your mode
3. Follow [02-agents.md](02-agents.md) to set up agents
4. Jump to specific topics as needed

### Looking for Something Specific?
- Use the [Quick Access](#quick-access) tables above
- Check the [Search by Topic](#search-by-topic) section
- Each component has detailed table of contents

### Learning the System?
- Follow the "By Role" reading path above
- Read components in order (00 → 10)
- Refer to external guides for deep dives

### Need Quick Answers?
- [10-reference.md](10-reference.md#quick-decision-guide) for decision trees
- [09-best-practices.md](09-best-practices.md#common-pitfalls-to-avoid) for common issues
- [00-quick-start.md](00-quick-start.md#getting-help) for support

---

## Related Documentation

- **Main README:** `../../README.md` - Project overview
- **Architecture:** `../../ARCHITECTURE.md` - System design
- **Skills Guide:** `../../SKILLS_GUIDE.md` - Complete skills documentation
- **Context Engineering:** `../../Context_Engineering.md` - Foundational principles
- **FAQ:** `FAQ.md` - Frequently asked questions

---

**Ready to dive in?** Start with [00-quick-start.md](00-quick-start.md) →

---

**Last Updated:** 2025-12-04
**Version:** 1.3.0
**Components:** 11 focused reference files
