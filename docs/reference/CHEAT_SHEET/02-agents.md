# Agent Prompts

Agent templates and specialized roles for multi-agent workflows.

---

## Manager Workflow

**Updated:** v1.1.0 - Dual-mode workflow support

| Prompt | Purpose | Mode | Location |
|--------|---------|------|----------|
| `manager-task-delegation.md` | Full Manager guide with dual-mode workflow | Simple/Complex | `prompts/manager-task-delegation.md` |
| `manager-quick-reference.md` | Quick-start copy-paste templates | Quick reference | `prompts/manager-quick-reference.md` |

### Workflow Modes

**Simple Mode** (90% of projects):
```
Manager → Task Agents → Integration Agent
```

**Complex Mode** (10% of projects):
```
Manager → IT Specialist → Task Agents → Senior Engineer
```

**See:** [05-workflows.md](05-workflows.md) for detailed workflow comparison

---

## Specialized Agents

**New in v1.1.0** - Infrastructure and quality assurance specialists

| Agent | Purpose | Key Features | Location |
|-------|---------|--------------|----------|
| `it-specialist-agent.md` | Infrastructure validation | 8 critical checks before development, init.sh generation | `prompts/it-specialist-agent.md` |
| `senior-engineer-agent.md` | Code review & integration | Enforces standards, reviews code, merges branches, blocks merges without E2E tests | `prompts/senior-engineer-agent.md` |

### IT Specialist

**When to Use:** Complex Mode - before any feature development

**8 Critical Infrastructure Checks:**
1. Development environment setup
2. Dependencies installed and working
3. Database migrations applied
4. Environment variables configured
5. Test infrastructure working
6. Build process verified
7. Git workflow established
8. Documentation baseline exists

**New Feature (Phase 4):** Generates project-specific `init.sh` scripts
- See: `templates/init-scripts/` for examples
- Automates environment setup for new developers

### Senior Engineer

**When to Use:** Complex Mode - before merging any feature

**Responsibilities:**
- Code review with quality standards
- E2E test verification (BLOCKS merges without tests)
- Integration and conflict resolution
- Branch merging
- Code quality gates

**Enforces:** All 5 feature completion criteria from [01-state-files.md](01-state-files.md#feature-completion-criteria)

---

## Base Agents

Core agent templates that work across all projects:

| Agent | Purpose | Best For | Location |
|-------|---------|----------|----------|
| `software-developer.md` | Universal software development | All development tasks | `prompts/roles/software-developer.md` |
| `manager.md` | Multi-agent team orchestration | Coordinating 3+ agents | `prompts/roles/manager.md` |
| `qa-tester.md` | Testing and quality assurance | Writing tests, finding bugs | `prompts/roles/qa-tester.md` |
| `architect.md` | System design and architecture | Designing systems, APIs | `prompts/roles/architect.md` |
| `scrum-master.md` | Project tracking & visibility | AppFlowy integration, sprint tracking | `prompts/roles/scrum-master.md` |

### Manager
**Updated:** Session Management section (lines 302-498)
- First session vs. resuming session protocols
- Feature completion criteria enforcement
- Prevents premature "done" declarations

### QA Tester
**Updated:** webapp-testing as primary tool (lines 219-368)
- E2E testing prioritization
- Playwright integration

### Software Developer
Universal development agent - compose with platform augmentations for specialization.

### Architect
System design and API contract definition.

### Scrum Master
**Optional** - Add for external visibility and sprint tracking:
- AppFlowy integration
- Daily standup summaries
- Sprint velocity tracking

---

## Platform Augmentations

Specialize base agents for different platforms:

| Platform | Augmentation | Best For | Location |
|----------|--------------|----------|----------|
| Web Frontend | `frontend-developer.md` | React, Vue, Angular, modern web apps | `platforms/web/frontend-developer.md` |
| Web Backend | `backend-developer.md` | Node.js, Python, Go, API services | `platforms/web/backend-developer.md` |
| Mobile | `mobile-developer.md` | React Native, Flutter, native iOS/Android | `platforms/mobile/mobile-developer.md` |

**Composition Pattern:**
```bash
# Base agent + Platform augmentation
python scripts/compose-agent.py --base software-developer --platform web/frontend
```

**Future Platforms:** Desktop (Electron, Qt), Data (ML pipelines), DevOps (CI/CD), Embedded (IoT)

---

## Quality Auditors

Agents that review other agents and ensure best practices:

| Agent | Purpose | Use When | Location |
|-------|---------|----------|----------|
| `skill-auditor` | Review skills for best practices, XML structure, token efficiency | After creating/modifying skills | `.claude/agents/skill-auditor.md` |
| `slash-command-auditor` | Review command structure, frontmatter, descriptions | After creating slash commands | `.claude/agents/slash-command-auditor.md` |
| `subagent-auditor` | Review agent configurations, role clarity, success criteria | After creating/composing agents | `.claude/agents/subagent-auditor.md` |

**Usage:**
```bash
# Invoke via Claude Code
/audit-skill path/to/skill/
/audit-slash-command path/to/command.md
/audit-subagent path/to/agent.md
```

---

## Agent Composition

### Basic Composition
```bash
# Compose all agents from config
python scripts/compose-agent.py --config ../config.yml --all

# Compose specific agent
python scripts/compose-agent.py --config ../config.yml --agent backend_dev
```

### Advanced Composition
```yaml
# config.yml example
agents:
  backend_dev:
    base: software-developer
    platform: web/backend
    skills:
      - mcp-builder
      - skill-creator
    context:
      - architecture.md
      - api-contracts.md
```

**Output:** `.ai-agents/composed/backend_dev.md`

---

## Agent Selection Guide

### For Simple Mode Projects

**Required:**
- Manager (1)
- Task Agents (2-3): Frontend Dev, Backend Dev, Mobile Dev, etc.
- Integration Agent (1) - can use basic software-developer

**Example Team:**
```
Manager → Frontend Dev → Backend Dev → Integration Agent
```

### For Complex Mode Projects

**Required:**
- Manager (1)
- IT Specialist (1) - runs first
- Task Agents (3-5): Specialized developers
- QA Tester (1) - writes E2E tests
- Senior Engineer (1) - reviews and merges

**Example Team:**
```
Manager → IT Specialist → Backend Dev → Frontend Dev → QA Tester → Senior Engineer
```

### Optional Addition

**Scrum Master:**
- Add when external stakeholders need visibility
- Provides daily summaries
- Tracks sprint velocity
- Requires AppFlowy server

---

## See Also

- **Skills for Agents:** [03-skills.md](03-skills.md)
- **Workflow Modes:** [05-workflows.md](05-workflows.md)
- **Best Practices:** [09-best-practices.md](09-best-practices.md)

---

[← Back to Index](index.md) | [Previous: State Files](01-state-files.md) | [Next: Skills →](03-skills.md)
