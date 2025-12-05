# Skills Library

Skills are reusable prompt components that give agents specialized capabilities.

---

## Overview

| Skill Source | Count | Purpose | Token Range |
|--------------|-------|---------|-------------|
| Anthropic Official | 13 | Core development, documents, design, communication | 2,200-4,500 |
| Taches-CC Community | 3 | Advanced workflows (planning, debugging, skill creation) | Variable |
| Custom | Variable | Project-specific functionality | Variable |

**Total Skills Available:** 16+ skills

---

## Anthropic Skills

13 official Anthropic skills integrated as git submodule.

**Location:** `skills/anthropic/` (git submodule)
**License:** Apache 2.0 (see `skills/anthropic/THIRD_PARTY_NOTICES.md`)

### Core Development Skills

| Skill | Purpose | Token Est. | Best For |
|-------|---------|------------|----------|
| `web-artifacts-builder` | Build interactive web components with React + Tailwind | ~3,500 | Frontend Dev |
| `webapp-testing` | End-to-end testing with Playwright | ~4,000 | QA Tester |
| `mcp-builder` | Build Model Context Protocol servers (Python/TypeScript) | ~4,500 | Backend Dev |
| `skill-creator` | Create new Claude Code skills | ~3,000 | Any agent |

**Recommended Assignment:**
- **Frontend Developer:** `web-artifacts-builder`, `frontend-design`
- **QA Tester:** `webapp-testing` (primary tool)
- **Backend Developer:** `mcp-builder`, `skill-creator`

### Document Skills

| Skill | Purpose | Token Est. | Best For |
|-------|---------|------------|----------|
| `document-skills/pdf` | PDF processing and generation | ~3,500 | Reports, invoices |
| `document-skills/docx` | Word document creation (OOXML) | ~4,000 | Documentation |
| `document-skills/pptx` | PowerPoint generation | ~4,200 | Presentations |
| `document-skills/xlsx` | Excel spreadsheet manipulation | ~3,800 | Data exports |

**Use Cases:**
- Generate project documentation
- Create reports from data
- Export data to spreadsheets
- Build presentation decks

### Design & Creative Skills

| Skill | Purpose | Token Est. | Best For |
|-------|---------|------------|----------|
| `frontend-design` | Modern UI/UX design with Tailwind + shadcn/ui | ~3,200 | Frontend Dev |
| `theme-factory` | 10 pre-built design themes (midnight-galaxy, ocean-depths, etc.) | ~2,500 | Frontend Dev |
| `canvas-design` | Interactive canvas-based design | ~3,000 | Design tasks |
| `algorithmic-art` | Generative art and visualizations | ~2,800 | Creative work |

**Themes Available in theme-factory:**
- midnight-galaxy
- ocean-depths
- forest-canopy
- desert-sunset
- arctic-aurora
- tokyo-neon
- retro-80s
- minimal-mono
- warm-earth
- cool-corporate

### Communication Skills

| Skill | Purpose | Token Est. | Best For |
|-------|---------|------------|----------|
| `internal-comms` | Internal communications (newsletters, updates, FAQs) | ~3,500 | Manager |
| `brand-guidelines` | Brand consistency and style guides | ~2,800 | Design |
| `slack-gif-creator` | Create animated GIFs for Slack | ~2,200 | Fun comms |

---

## Taches-CC Skills

3 advanced workflow skills from Taches-CC community.

**Location:** `skills/taches-cc/` or `external/taches-cc-resources/skills/`

### Available Skills

| Skill | Purpose | Key Features | Location |
|-------|---------|--------------|----------|
| `create-plans` | Hierarchical project planning for solo+Claude development | Atomic tasks, verification criteria, context handoffs, 50% scope control | `skills/taches-cc/create-plans/` |
| `debug-like-expert` | Expert debugging methodology | Evidence gathering, hypothesis testing, rigorous verification, domain expertise detection | `skills/taches-cc/debug-like-expert/` |
| `create-agent-skills` | Skill authoring best practices | Router pattern, XML structure, workflow organization | `skills/taches-cc/create-agent-skills/` |

### create-plans

**Best For:** Manager agent

**Features:**
- 11 workflows for different planning scenarios
- 11 references for best practices
- 8 templates (briefs, roadmaps, phases, milestones)
- Progressive disclosure for complex planning
- Atomic task breakdown

**Token Impact:** Variable (loads on-demand)

**Usage:**
```bash
# Via Claude Code
/create-plan "Implement user authentication system"
```

### debug-like-expert

**Best For:** Any developer agent encountering bugs

**Features:**
- 5 references (debugging mindset, hypothesis testing, investigation techniques)
- Methodical investigation protocol
- Evidence gathering workflows
- Hypothesis testing framework
- Domain expertise detection

**Usage:**
```bash
# Via Claude Code
/debug "Users can't log in after password reset"
```

### create-agent-skills

**Best For:** When creating custom skills

**Features:**
- 5 references (XML structure, skill structure, using templates/scripts)
- Router pattern for skill navigation
- XML best practices
- Progressive disclosure patterns
- Example skill structures

**Usage:**
```bash
# Via Claude Code
/create-agent-skill "database migration skill"
```

---

## Custom Skills

Project-specific skills and templates.

**Location:** `skills/custom/`

### Available Custom Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| `appflowy-integration` | AppFlowy task tracking for Scrum Master agent | `skills/custom/appflowy-integration/` |
| `template` | Template for creating custom skills | `skills/custom/template/` |

### Creating Custom Skills

**Quick Start:** See `skills/custom/QUICK_START.md`

**Basic Structure:**
```
skills/custom/my-skill/
├── SKILL.md              # Main skill prompt
├── examples/             # Usage examples
│   └── example-01.md
├── references/           # Supporting documentation
│   └── api-reference.md
└── templates/            # Reusable templates
    └── template-01.md
```

**Template Usage:**
```bash
# Copy template
cp -r skills/custom/template skills/custom/my-new-skill

# Edit SKILL.md with your skill logic
# Add examples, references, templates as needed
```

---

## Skill Assignment Strategy

### Token Budget Considerations

**Per Agent Token Budget:** ~20,000-30,000 tokens recommended
**Average Skill Cost:** ~2,500-4,500 tokens

**Rule of Thumb:** Assign 1-3 skills per agent

### Assignment Patterns

#### Frontend Developer
```yaml
skills:
  always_loaded:
    - web-artifacts-builder     # ~3,500 tokens
    - frontend-design           # ~3,200 tokens
  deferred:
    - path: theme-factory       # Load when "theme" mentioned
      triggers: ["theme", "style", "design system"]
```

**Total at-rest:** ~6,700 tokens (33% of budget)

#### Backend Developer
```yaml
skills:
  always_loaded:
    - mcp-builder              # ~4,500 tokens
  deferred:
    - path: skill-creator      # Load when creating tools
      triggers: ["skill", "tool", "create"]
```

**Total at-rest:** ~4,500 tokens (22% of budget)

#### QA Tester
```yaml
skills:
  always_loaded:
    - webapp-testing           # ~4,000 tokens (primary tool)
```

**Total at-rest:** ~4,000 tokens (20% of budget)

#### Manager
```yaml
skills:
  deferred:
    - path: create-plans       # Load when planning
      triggers: ["plan", "roadmap", "project"]
    - path: internal-comms     # Load when communicating
      triggers: ["announce", "update", "communication"]
```

**Total at-rest:** ~0 tokens (100% deferred)

### Deferred Loading (85% Token Reduction)

**See:** [07-advanced.md](07-advanced.md#deferred-skill-loading) for complete guide

**Config Format:**
```yaml
agents:
  developer:
    skills:
      always_loaded:
        - "core/skill-creator"
      deferred:
        - path: "testing/webapp-testing"
          triggers: ["test", "QA", "coverage", "playwright"]
```

**Benefits:**
- Skills load on-demand via trigger words
- 85% token reduction vs. loading all skills
- Scales to large skill libraries (10+ skills)

---

## Skill Selection Guide

### By Role

| Role | Recommended Skills | Priority |
|------|-------------------|----------|
| **Frontend Dev** | `web-artifacts-builder`, `frontend-design`, `theme-factory` | High |
| **Backend Dev** | `mcp-builder`, `skill-creator` | High |
| **QA Tester** | `webapp-testing` | Critical |
| **Manager** | `create-plans`, `internal-comms` | Medium |
| **Architect** | None (use base reasoning) | N/A |
| **Any Agent** | `document-skills/*` for doc generation | Low |

### By Task Type

| Task Type | Recommended Skills |
|-----------|-------------------|
| Building UI components | `web-artifacts-builder`, `frontend-design` |
| E2E Testing | `webapp-testing` |
| Building APIs | `mcp-builder` |
| Project Planning | `create-plans` |
| Debugging | `debug-like-expert` |
| Document Generation | `document-skills/pdf`, `document-skills/docx` |
| Creating Tools | `skill-creator`, `mcp-builder` |

### By Project Phase

| Phase | Recommended Skills |
|-------|-------------------|
| **Planning** | `create-plans` (Manager) |
| **Development** | Role-specific skills (see above) |
| **Testing** | `webapp-testing` (QA) |
| **Documentation** | `document-skills/*` (any agent) |
| **Debugging** | `debug-like-expert` (any agent) |

---

## Best Practices

### Do's ✅

1. **Assign strategically** - 1-3 skills per agent based on role
2. **Use deferred loading** - For large skill libraries (10+ skills)
3. **Monitor effectiveness** - Track which skills improve outcomes
4. **Match to tasks** - Assign skills relevant to agent's work
5. **Consider token budget** - Keep total prompt under 30K tokens

### Don'ts ❌

1. **Don't overload** - Avoid assigning 5+ skills to one agent
2. **Don't load unused skills** - Use deferred loading if uncertain
3. **Don't assign irrelevant skills** - Frontend dev doesn't need MCP builder
4. **Don't ignore token costs** - Each skill = 2.5-4.5K tokens

---

## See Also

- **Complete Skills Guide:** `SKILLS_GUIDE.md`
- **Skills Catalog:** `skills/CATALOG.md`
- **Integration Guide:** `skills/INTEGRATION.md`
- **Custom Skills:** `skills/custom/QUICK_START.md`
- **Advanced Features:** [07-advanced.md](07-advanced.md)

---

[← Back to Index](index.md) | [Previous: Agents](02-agents.md) | [Next: Commands →](04-commands.md)
