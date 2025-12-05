# Quick Reference

File locations, statistics, decision guides, and version history.

---

## File Locations

Where to find everything in the repository.

| What | Where |
|------|-------|
| **Commands** |
| Slash commands | `.claude/commands/` |
| Thinking models | `.claude/commands/consider/` |
| **Agents** |
| Auditor agents | `.claude/agents/` |
| Manager prompts | `prompts/` |
| Base agents | `prompts/roles/` |
| Platform augments | `platforms/` |
| Composed agents | `.ai-agents/composed/` |
| **Skills** |
| Anthropic skills | `skills/anthropic/` or `external/anthropic-skills/` (git submodule) |
| Taches-CC skills | `skills/taches-cc/` or `external/taches-cc-resources/skills/` |
| Custom skills | `skills/custom/` |
| **Scripts & Tools** |
| Core scripts | `scripts/` |
| Orchestration | `scripts/orchestration/` |
| Starter templates | `starter-templates/` |
| Security validator | `scripts/security_validator.py` |
| **State & Config** |
| State files | `.ai-agents/state/` |
| Project context | `.ai-agents/context/` |
| Agent config | `.ai-agents/config.yml` |
| **Schemas** |
| All schemas | `schemas/` |
| Session progress | `schemas/session-progress.json` |
| Feature tracking | `schemas/feature-tracking.json` |
| Security policy | `schemas/security-policy.json` |
| **Documentation** |
| Main docs | `docs/` |
| Guides | `docs/guides/` |
| Reference | `docs/reference/` |
| **Examples** |
| All examples | `examples/` |
| Session continuity | `examples/session-continuity/` |
| **Templates** |
| Init scripts | `templates/init-scripts/` |
| **Tools** |
| Tool selector | `tools/` |

---

## Key Documentation

Essential documentation files and guides.

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
| `docs/guides/PRACTICAL_WORKFLOW_GUIDE.md` | Human-coordinated multi-agent workflows | Before first multi-agent project |
| `docs/guides/PARALLEL_EXECUTION_GUIDE.md` | Multi-agent parallelization strategies | When scaling to 3+ agents |
| `docs/guides/LONG_RUNNING_AGENTS.md` | Complete long-running agent patterns guide | Complex Mode projects |
| `docs/guides/E2E_TESTING.md` | Comprehensive E2E testing workflow | When writing E2E tests |
| `docs/guides/SECURITY.md` | Security framework documentation | Autonomous execution mode |
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
| `docs/reference/FAQ.md` | Frequently asked questions |
| `docs/reference/CHEAT_SHEET/index.md` | This cheat sheet (navigation hub) |
| `MIGRATION_GUIDE.md` | Adding skills to existing projects |
| `TESTING_REPORT.md` | Testing results and validation |

---

## Repository Statistics

Current state of the repository.

### Agents & Prompts

- **Base Agents:** 5 (software-developer, manager, qa-tester, architect, scrum-master)
- **Manager Prompts:** 4 (manager-task-delegation, manager-quick-reference, it-specialist, senior-engineer)
- **Platform Augments:** 3 active (web/frontend, web/backend, mobile)
- **Platform Planned:** 3 (desktop, data, devops)
- **Quality Auditors:** 3 (skill-auditor, slash-command-auditor, subagent-auditor)

### Commands & Tools

- **Slash Commands:** 17 total
  - 12 thinking models (`/consider:*`)
  - 4 workflow commands (`/debug`, `/whats-next`, `/add-to-todos`, `/check-todos`)
  - 1 discovery command (`/ai-tools`)
- **Tool Selector Commands:** 30 wrapper commands

### Skills

- **Anthropic Skills:** 13 official skills (~2,200-4,500 tokens each)
  - 4 core development
  - 4 document skills
  - 4 design & creative
  - 1 communication skill (internal-comms, + brand-guidelines, slack-gif-creator = 3 total)
- **Taches-CC Skills:** 3 advanced workflow skills
- **Custom Skills:** 1 (appflowy-integration) + template

### Scripts & Templates

- **Orchestration Scripts:** 6 Python scripts
- **Core Scripts:** 4 (compose-agent, generate-template, setup-commands, security-validator)
- **Starter Templates:** 5 (web-app, mobile-app, full-stack, api-service, data-pipeline)
- **Init Script Templates:** 3 (nodejs-react, python-django, fullstack)

### Schemas

- **Total Schemas:** 7
  - 2 communication schemas
  - 3 state management schemas (NEW: session-progress, feature-tracking, security-policy)
  - 2 configuration schemas

### Documentation

- **Documentation Files:** 20+ markdown guides
- **Total Word Count:** 45,000+ words
- **Examples:** 4 complete examples
  - web-app-team
  - mobile-app-team
  - skills-showcase
  - session-continuity (NEW)

### State System (NEW v1.2.0)

- **State Files:** 3 (team-communication, session-progress, feature-tracking)
- **Security Framework:** security-policy.json + security_validator.py
- **Examples:** 1 complete 3-session example

---

## Quick Decision Guide

Fast answers to common questions.

### Which Workflow Mode?

| Scenario | Mode | Reason |
|----------|------|--------|
| Established project, clear requirements | **Simple** | Fast, minimal overhead |
| New project, need infrastructure setup | **Complex** | IT Specialist validates first |
| 1-3 agents | **Simple** | Don't overcomplicate |
| 5+ agents | **Complex** | Need coordination and review |
| Code review required | **Complex** | Senior Engineer enforces quality |
| Multi-day work with sessions | **Complex** | session-progress.json for continuity |
| External stakeholders need visibility | **Either + Scrum Master** | AppFlowy tracking |

### Which Coordination Model?

| Scenario | Model | Reason |
|----------|-------|--------|
| Learning multi-agent patterns | **Human-Coordinated** | Full control, easy to understand |
| Claude Code (one session at a time) | **Human-Coordinated** | Tool limitation |
| Small teams (1-3 agents) | **Human-Coordinated** | Simplest approach |
| Most production projects (3-7 agents) | **Task Tool Delegation** | Best balance, zero API costs |
| Need fresh context per agent | **Task Tool Delegation** | Prevents Manager bloat |
| Large-scale (7+ agents) | **Fully Automated** | True parallel execution |
| CI/CD automation | **Fully Automated** | Production-ready pipelines |

### Which Skills?

| Agent Role | Recommended Skills | Priority |
|------------|-------------------|----------|
| **Frontend Dev** | `web-artifacts-builder`, `frontend-design`, `theme-factory` | High |
| **Backend Dev** | `mcp-builder`, `skill-creator` | High |
| **QA Tester** | `webapp-testing` | Critical |
| **Manager** | `create-plans`, `internal-comms` | Medium |
| **Architect** | None (use base reasoning) | N/A |
| **Any Agent** | `document-skills/*` for doc generation | Low |

**By Task Type:**

| Task | Skills |
|------|--------|
| Building UI components | `web-artifacts-builder`, `frontend-design` |
| E2E Testing | `webapp-testing` |
| Building APIs | `mcp-builder` |
| Project Planning | `create-plans` |
| Debugging | `debug-like-expert` |
| Document Generation | `document-skills/pdf`, `document-skills/docx` |
| Creating Tools | `skill-creator`, `mcp-builder` |

### Which Starter Template?

| Project Type | Template | Reason |
|--------------|----------|--------|
| React/Vue + Node/Python | **web-app** | Full-stack web standard |
| React Native/Flutter | **mobile-app** | Mobile-specific patterns |
| Microservices | **full-stack** | Multiple services |
| REST/GraphQL API only | **api-service** | Backend focus |
| ETL/Analytics | **data-pipeline** | Data processing patterns |

### Which Documentation?

| Need | Read This | Why |
|------|-----------|-----|
| Getting started | `README.md` | Quick start guide |
| Core principles | `Context_Engineering.md` | Foundational understanding |
| Understanding architecture | `ARCHITECTURE.md` | System design |
| Setting up Manager | `prompts/manager-task-delegation.md` | Complete workflow guide |
| Quick Manager setup | `prompts/manager-quick-reference.md` | Copy-paste templates |
| Multi-agent workflows | `docs/guides/PRACTICAL_WORKFLOW_GUIDE.md` | Step-by-step examples |
| Long-running projects | `docs/guides/LONG_RUNNING_AGENTS.md` | Session continuity patterns |
| E2E testing | `docs/guides/E2E_TESTING.md` | Testing workflows |
| Token optimization | [07-advanced.md](07-advanced.md) | Advanced patterns |
| State files | [01-state-files.md](01-state-files.md) | Three-file system |
| Quick reference | This cheat sheet | Fast lookups |

---

## Version History

Notable releases and features.

### v1.3.0 (Current)
**Released:** 2025-11-25

**New Features:**
- Tool Selector system for cross-project tool access
- `/ai-tools` discovery command
- 30 wrapper commands (~200-300 bytes each)
- Minimal token footprint (~50 tokens at-rest)

**Impact:**
- Access AI_agents tools from any project
- Centralized updates
- Clean separation of concerns

---

### v1.2.0
**Released:** 2025-11-20

**New Features:**
- Autonomous agent integration (long-running patterns)
- Three-file state system (team-communication, session-progress, feature-tracking)
- Security framework (security-policy.json + security_validator.py)
- Advanced Tool Use features:
  - Deferred skill loading (85% token reduction)
  - Prompt caching (API cost savings)
  - Programmatic tool calling (37% token reduction)
- E2E testing guide
- Long-running agents guide
- Security guide
- Session continuity examples
- Init scripts templates

**Schemas Added:**
- `schemas/session-progress.json`
- `schemas/feature-tracking.json`
- `schemas/security-policy.json`

**Agent Updates:**
- Manager: Session Management section
- Senior Engineer: E2E test enforcement
- QA Tester: webapp-testing as primary tool
- IT Specialist: init.sh generation (Phase 4)

**Impact:**
- 50% faster session resumption (session-progress.json)
- Mandatory E2E testing in Complex Mode
- 85% token reduction with deferred loading
- 37% token reduction with programmatic tools

---

### v1.1.0
**Released:** 2025-11-10

**New Features:**
- Manager workflow dual-mode (Simple/Complex)
- IT Specialist agent (infrastructure validation)
- Senior Engineer agent (code review and integration)
- Starter Templates (5 templates for existing projects)
- Task Tool Delegation coordination model
- Orchestration scripts (6 scripts)

**Documentation:**
- `prompts/manager-task-delegation.md`
- `prompts/manager-quick-reference.md`
- `prompts/it-specialist-agent.md`
- `prompts/senior-engineer-agent.md`
- `scripts/orchestration/COMPLETE_GUIDE.md`

**Impact:**
- Clear workflow modes (90% Simple, 10% Complex)
- Infrastructure validation before development
- Code quality enforcement
- Quick-start templates for existing projects
- Zero API costs with Task Tool

---

### v1.0.0
**Released:** 2025-11-01

**Initial Release:**
- Skills integration (13 Anthropic + 3 Taches-CC)
- Base agents (5 agents)
- Platform augments (web frontend/backend, mobile)
- Orchestration scripts (basic)
- Communication protocol
- Human-coordinated workflows

**Core Components:**
- Base agent library
- Skills composition system
- Platform specializations
- Communication schemas
- Quality auditors

---

## Roadmap

### Planned Features

**Phase 2 Platforms:**
- Desktop (Electron, Qt)
- Data (ML pipelines, ETL)
- DevOps (CI/CD)
- Embedded (IoT)

**Enhanced Features:**
- More starter templates
- Additional custom skills
- Advanced orchestration patterns
- CI/CD integration examples

### Contributing

- **Issues:** [GitHub Issues](https://github.com/HelloWorldSungin/AI_agents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HelloWorldSungin/AI_agents/discussions)
- **Pull Requests:** Welcome!

---

## Getting Help

### Support Channels

- **Documentation:** This repository (start with `README.md`)
- **Issues:** [GitHub Issues](https://github.com/HelloWorldSungin/AI_agents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HelloWorldSungin/AI_agents/discussions)
- **Examples:** `examples/` directory

### Common Questions

See `docs/reference/FAQ.md` for frequently asked questions.

### Reporting Issues

When reporting issues, include:
1. Your setup (Simple/Complex Mode, coordination model)
2. Agents involved
3. Steps to reproduce
4. Expected vs. actual behavior
5. Relevant logs or state files

---

## Next Steps

Ready to start using the AI Agents Library?

### For New Users

1. **Read** `README.md` for overview
2. **Study** `Context_Engineering.md` for principles
3. **Choose** a [starter template](#which-starter-template)
4. **Follow** [00-quick-start.md](00-quick-start.md) for setup
5. **Try** Simple Mode first

### For Existing Users

1. **Review** [01-state-files.md](01-state-files.md) for three-file system
2. **Upgrade** to Complex Mode if needed
3. **Optimize** with [07-advanced.md](07-advanced.md) patterns
4. **Explore** Tool Selector for cross-project tools

### For Advanced Users

1. **Implement** Fully Automated coordination
2. **Customize** orchestration scripts
3. **Create** custom skills and templates
4. **Contribute** improvements back

---

**Pro tip:** Bookmark this cheat sheet for quick reference during development!

---

[← Back to Index](index.md) | [Previous: Best Practices](09-best-practices.md)
