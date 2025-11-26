# AI Agents Library Architecture

**Version:** 1.0.0
**Last Updated:** 2025-11-20
**Foundation:** Based on [Context Engineering Guide](Context_Engineering.md)

---

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [System Architecture](#system-architecture)
- [Agent Composition Model](#agent-composition-model)
- [Multi-Agent Collaboration](#multi-agent-collaboration)
- [Context Management](#context-management)
- [Skills Integration](#skills-integration)
- [Repository Structure](#repository-structure)
- [Integration Guide](#integration-guide)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The AI Agents Library is a comprehensive framework for building multi-agent software development systems. It provides a modular, composable approach to creating specialized AI agents that can work together on complex software projects.

### Key Features

- **Modular Agent Design**: Base prompts + platform augmentations + project context
- **Multi-Agent Coordination**: Manager-led team collaboration
- **Context Engineering**: Advanced memory and context management
- **Git-Based Workflow**: Branch isolation prevents agent conflicts
- **Structured Communication**: JSON-based inter-agent messaging
- **Flexible Deployment**: Works with web, mobile, desktop, and other platforms

### Design Goals

1. **Reusability**: Write once, use across multiple projects
2. **Maintainability**: Update base capabilities, all agents benefit
3. **Scalability**: Easy to add new platforms and specializations
4. **Quality**: Built-in best practices and quality gates
5. **Collaboration**: Agents work together without conflicts

---

## Design Principles

Based on the Context Engineering Guide, this library follows these core principles:

### 1. Holistic Design
All context elements (system prompts, instructions, tools, memory) work together as interconnected components.

### 2. Layered Specialization
```
┌─────────────────────────────────────────┐
│   Project-Specific Context (Layer 3)   │
│   • Business logic                      │
│   • API contracts                       │
│   • Team conventions                    │
├─────────────────────────────────────────┤
│   Platform Augmentation (Layer 2)      │
│   • Web/Mobile/Desktop expertise        │
│   • Framework knowledge                 │
│   • Platform best practices             │
├─────────────────────────────────────────┤
│   Base Agent Foundation (Layer 1)       │
│   • Core software engineering           │
│   • Testing, debugging, git             │
│   • Universal best practices            │
└─────────────────────────────────────────┘
```

### 3. Separation of Concerns
- **Base Layer**: What all developers need
- **Platform Layer**: Platform-specific knowledge
- **Project Layer**: Your specific requirements

### 4. Composition Over Inheritance
Agents are composed from multiple modular components rather than inheriting from a single monolithic template.

### 5. Context Preservation
Multi-tier memory architecture ensures critical information is never lost during context compaction.

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│              USER / PRODUCT OWNER                        │
└────────────────────┬─────────────────────────────────────┘
                     │ Requirements
                     ▼
        ┌─────────────────────────┐
        │   MANAGER AGENT         │
        │  (Orchestrator)         │
        └────────┬────────────────┘
                 │
       ┌─────────┼─────────┬──────────┬──────────┐
       │         │         │          │          │
       ▼         ▼         ▼          ▼          ▼
   ┌──────┐ ┌──────┐ ┌──────┐  ┌────────┐ ┌───────┐
   │ ARCH │ │FRONT │ │BACK  │  │ MOBILE │ │  QA   │
   │ITECT │ │ END  │ │ END  │  │  DEV   │ │TESTER │
   └──┬───┘ └──┬───┘ └──┬───┘  └───┬────┘ └───┬───┘
      │        │        │          │          │
      └────────┴────────┴──────────┴──────────┘
                        │
                        ▼
             ┌────────────────────┐
             │  PROJECT STATE     │
             │  • Tasks           │
             │  • Agent states    │
             │  • Resources       │
             │  • Metrics         │
             └────────────────────┘
```

### Component Breakdown

#### 1. Agent Library (This Repository)
Contains reusable agent prompts, augmentations, tools, and schemas.

**Components:**
- Base agent prompts (developer, manager, tester, architect)
- Platform augmentations (web, mobile, desktop, etc.)
- Tool definitions (git, testing, communication, etc.)
- JSON schemas (communication, state, configuration)
- Memory management templates
- Workflow patterns

#### 2. Project Configuration
Each project using the library defines:
- Which agents to deploy
- Project-specific context
- Tech stack and coding standards
- Quality gates
- CI/CD configuration

#### 3. Composition Engine
`scripts/compose-agent.py` assembles complete agent prompts by:
1. Loading base agent
2. Merging platform augmentations
3. Injecting project context
4. Configuring tools and memory
5. Adding coordination information

#### 4. State Management
Central state file (`.ai-agents/state/project-state.json`) tracks:
- Active tasks and assignments
- Agent status and activity
- Resource locks
- Integration points
- Project metrics

#### 5. Communication Protocol
Standardized JSON messages for:
- Task assignments
- Status updates
- Blocker reports
- Dependency requests
- Conflict notifications
- Code review feedback

---

## Agent Composition Model

### Composition Process

```python
# Pseudocode for agent composition

def compose_agent(agent_config, project_config):
    agent_prompt = []

    # 1. Load base foundation
    base = load_markdown(agent_config.base)
    agent_prompt.append(base)

    # 2. Merge platform augmentations
    for platform in agent_config.platforms:
        platform_content = load_markdown(platform)
        agent_prompt.append(platform_content)

    # 3. Inject project context
    for context_file in agent_config.project_context:
        context = load_markdown(context_file)
        agent_prompt.append(context)

    # 4. Add tool definitions
    for tool in agent_config.tools:
        tool_def = load_markdown(tool)
        agent_prompt.append(tool_def)

    # 5. Generate project-specific instructions
    project_info = generate_project_info(project_config)
    agent_prompt.append(project_info)

    # 6. Add coordination info
    coordination = generate_coordination_info(agent_config)
    agent_prompt.append(coordination)

    # 7. Configure memory
    memory_config = generate_memory_config(agent_config)
    agent_prompt.append(memory_config)

    return merge_sections(agent_prompt)
```

### Example: Frontend Developer Composition

```yaml
# From config.yml
frontend_developer:
  base: "base/software-developer.md"          # 3000 tokens
  platforms:
    - "platforms/web/frontend-developer.md"    # 2500 tokens
  project_context:
    - ".ai-agents/context/architecture.md"     # 500 tokens
    - ".ai-agents/context/coding-standards.md" # 300 tokens
    - ".ai-agents/context/api-contracts.md"    # 400 tokens
  tools:
    - "tools/git-tools.md"                     # 600 tokens
    - "tools/testing-tools.md"                 # 500 tokens

# Total: ~7800 tokens (base prompt)
# Leaves ~192k tokens for conversation (200k total context)
```

---

## Multi-Agent Collaboration

### Git Workflow Strategy

Agents work in isolated branches to prevent conflicts:

```
Repository Structure:

main (protected)
├── develop (integration)
│   ├── feature/user-authentication
│   │   ├── agent/architect/design          ← Architect's work
│   │   ├── agent/backend-dev/jwt-service   ← Backend's work
│   │   ├── agent/backend-dev/auth-api      ← Backend's work
│   │   ├── agent/frontend-dev/login-form   ← Frontend's work
│   │   └── agent/mobile-dev/login-screen   ← Mobile's work
│   │
│   └── feature/payment-integration
│       ├── agent/backend-dev/stripe-integration
│       └── agent/frontend-dev/checkout-ui
```

**Branch Naming Convention:**
```
<type>/<feature-name>/agent/<agent-role>/<specific-task>

Examples:
✓ feature/user-auth/agent/frontend-dev/login-form
✓ feature/user-auth/agent/backend-dev/jwt-service
✓ bugfix/memory-leak/agent/mobile-dev/profile-fix
```

### Coordination Workflow

```
1. User Request
   └─> Manager Agent

2. Manager: Task Decomposition
   ├─> TASK-001: Design auth architecture (Architect)
   ├─> TASK-002: Implement JWT service (Backend)
   ├─> TASK-003: Create auth API (Backend, depends on 002)
   ├─> TASK-004: Build login form (Frontend, depends on 003)
   └─> TASK-005: Write tests (QA, depends on 004)

3. Parallel Execution
   ├─> Architect works on TASK-001
   ├─> Backend starts TASK-002 after TASK-001
   └─> Frontend starts TASK-004 (uses API contract, not implementation)

4. Integration
   ├─> Manager coordinates API contract definition
   ├─> Agents implement against contract
   └─> Integration testing when all complete

5. Merge & Deploy
   ├─> QA approves
   ├─> Manager merges agent branches → feature branch
   ├─> Feature branch → develop
   └─> CI/CD deploys to staging
```

### Communication Protocol

Agents communicate using structured JSON messages:

```json
// Status Update
{
  "type": "status_update",
  "agent_id": "frontend-dev-001",
  "task_id": "TASK-004",
  "status": "in_progress",
  "progress": 65,
  "completed_items": ["Form UI", "Validation"],
  "next_items": ["Error handling", "Integration"],
  "estimated_completion": "2025-11-21T16:00:00Z",
  "blockers": [],
  "timestamp": "2025-11-20T15:30:00Z"
}

// Blocker Report
{
  "type": "blocker",
  "agent_id": "frontend-dev-001",
  "task_id": "TASK-004",
  "blocker_description": "API endpoint /api/auth/login returns 404",
  "severity": "high",
  "blocking_agent": "backend-dev-001",
  "can_proceed_with_workaround": true,
  "workaround": "Using mock API for now",
  "needs_resolution_by": "2025-11-21T12:00:00Z",
  "timestamp": "2025-11-20T15:45:00Z"
}
```

### Resource Locking

Prevent conflicts through soft file locking:

```json
// In .ai-agents/state/project-state.json
{
  "shared_resources": {
    "src/types/User.ts": {
      "owner": "backend-dev-001",
      "lock_status": "locked",
      "locked_at": "2025-11-20T15:00:00Z",
      "pending_requests": [
        {
          "agent_id": "frontend-dev-001",
          "requested_at": "2025-11-20T15:30:00Z",
          "priority": "medium"
        }
      ]
    }
  }
}
```

---

## Context Management

### Multi-Tier Memory Architecture

```
┌────────────────────────────────────────────────┐
│  Pinned Context (15%) - NEVER EVICTED         │
│  • System prompt                               │
│  • Current task details                        │
│  • Critical constraints                        │
│  • Active file context                         │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Working Memory (50%) - LRU with Priority      │
│  • Recent conversation (full detail)           │
│  • Relevant code snippets                      │
│  • Retrieved memories                          │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Cached Context (30%) - Relevance Scored       │
│  • Project documentation                       │
│  • Coding standards                            │
│  • API references                              │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Buffer (5%) - Safety Margin                   │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Long-Term Memory (Vector DB)                  │
│  • Architectural decisions (ADRs)              │
│  • Code patterns                               │
│  • Troubleshooting solutions                   │
│  • Requirements                                │
└────────────────────────────────────────────────┘
```

### Progressive Compression

```
Turn 1-5: Full Detail (Recent)
├─ Complete messages
├─ Full code snippets
└─ Detailed reasoning

Turn 6-20: Summarized (Medium Age)
├─ Key points extracted
├─ Code references (not full snippets)
└─ Decisions and outcomes only

Turn 21+: Indexed (Old)
├─ One-line summaries
├─ Pointers to memory
└─ Major decisions only
```

### Checkpoint Strategy

**Automatic Checkpoints:**
- Every 10 turns
- At 75% context usage
- Before major operations
- On request

**Checkpoint Contents:**
```json
{
  "checkpoint_id": "ckpt-20251120-1530",
  "timestamp": "2025-11-20T15:30:00Z",
  "agent_id": "frontend-dev-001",
  "critical_state": {
    "current_task": { /* full task details */ },
    "active_context": { /* working files, decisions */ },
    "decisions_made": [ /* recent decisions */ ]
  },
  "conversation_summary": { /* compressed history */ },
  "memory_pointers": { /* links to vector DB */ }
}
```

### Warning System

```
Context Usage Thresholds:

60% ─┬─> Yellow Alert
     │   • Begin progressive summarization
     │   • Log to project state
     │
75% ─┼─> Orange Alert
     │   • Compress conversation history
     │   • Create checkpoint
     │   • Move old context to vector DB
     │   • Notify manager
     │
85% ─┼─> Red Alert
     │   • Aggressive compression
     │   • Emergency checkpoint
     │   • Alert manager and user
     │   • Request task completion & restart
     │
95% ─┼─> Emergency
     │   • Force compression to essentials
     │   • Final checkpoint
     │   • Pause operations
     │   • Immediate session restart required
```

---

## Skills Integration

### What Are Skills?

**Skills** are modular instruction packages that extend AI agent capabilities with specialized knowledge, workflows, and tool integrations. They transform general-purpose agents into domain experts by providing focused guidance for specific tasks and technologies.

#### Skills vs Tools vs Platform Augmentations

Understanding the distinctions between these three concepts is crucial for effective agent composition:

| Aspect | Skills | Tools | Platform Augmentations |
|--------|--------|-------|------------------------|
| **Purpose** | Domain expertise & workflows | Actions & operations | Platform-specific knowledge |
| **Content** | Instructions, procedures, best practices | Function definitions, APIs | Framework expertise, patterns |
| **Loading** | Composed into agent prompt | Available as callable functions | Merged into base agent |
| **Structure** | Markdown + resources (scripts, docs) | JSON schemas, function signatures | Markdown augmentation layers |
| **Usage** | Guides agent behavior | Executed explicitly by agent | Always active for platform |
| **Scope** | Task-specific (e.g., PDF creation) | Action-specific (e.g., file read) | Platform-wide (e.g., React expertise) |
| **Token Impact** | 2-5k tokens per skill | Minimal (schema only) | 2-3k tokens per platform |

**When to Use Each:**

- **Skills**: When you need specialized workflows, domain expertise, or tool integration guidance
  - Example: `artifacts-builder` for React component creation, `mcp-builder` for API integration

- **Tools**: When you need agents to perform specific actions
  - Example: Git operations, file manipulation, API calls

- **Platform Augmentations**: When you need platform-specific development knowledge
  - Example: `frontend-developer.md` for React/web expertise, `mobile-developer.md` for React Native

**How They Work Together:**

```
Complete Agent = Base + Platform + Tools + Skills + Project Context

Example Frontend Developer:
├── Base: software-developer.md (universal engineering)
├── Platform: web/frontend-developer.md (React, web APIs)
├── Tools: git-tools.md, testing-tools.md (actions available)
├── Skills: artifacts-builder, theme-factory (specialized workflows)
└── Context: architecture.md, coding-standards.md (project specifics)
```

### Skills Architecture

The skills layer sits between platform augmentations and project context in the composition model:

```
┌─────────────────────────────────────────┐
│   Project Context (Layer 4)             │
│   • Your specific requirements          │
│   • Business logic                      │
│   • API contracts                       │
│   • Team conventions                    │
├─────────────────────────────────────────┤
│   Skills (Layer 3) ✨ NEW               │
│   • Domain expertise                    │
│   • Specialized workflows               │
│   • Tool integrations                   │
│   • Reusable procedures                 │
├─────────────────────────────────────────┤
│   Platform Augmentation (Layer 2)       │
│   • Web/Mobile/Desktop expertise        │
│   • Framework knowledge                 │
│   • Platform best practices             │
├─────────────────────────────────────────┤
│   Base Agent Foundation (Layer 1)       │
│   • Core software engineering           │
│   • Testing, debugging, git             │
│   • Universal best practices            │
└─────────────────────────────────────────┘

Updated Composition Model:
Base Agent → Platform → Skills → Tools → Project Context
```

**Why This Order?**

1. **Base** provides universal software engineering capabilities
2. **Platform** adds platform-specific knowledge (React, Node.js, etc.)
3. **Skills** provide specialized workflows that build on platform knowledge
4. **Tools** define actions that skills can reference in their workflows
5. **Project Context** applies everything to your specific requirements

### Skills Directory Structure

```
skills/
├── README.md                # Skills overview
├── CATALOG.md              # Complete skills directory
├── INTEGRATION.md          # Technical integration guide
├── QUICK_START.md          # 5-minute getting started
│
├── core/                   # Development & technical skills
│   ├── artifacts-builder/  # React component creation
│   ├── webapp-testing/     # Playwright-based testing
│   ├── mcp-builder/        # MCP server development
│   ├── skill-creator/      # Custom skill creation
│   └── .gitkeep
│
├── communication/          # Communication & documentation
│   ├── internal-comms/     # Team communications
│   └── .gitkeep
│
├── design/                 # Design & creative skills
│   ├── theme-factory/      # UI theming
│   ├── algorithmic-art/    # Generative art with p5.js
│   ├── canvas-design/      # Visual asset generation
│   └── .gitkeep
│
├── documents/              # Document manipulation
│   ├── docx/              # Word documents
│   ├── pdf/               # PDF manipulation
│   ├── xlsx/              # Excel spreadsheets
│   ├── pptx/              # PowerPoint presentations
│   └── .gitkeep
│
└── custom/                 # Project-specific skills
    ├── template/           # Skill creation template
    │   ├── README.md
    │   └── SKILL.md
    └── .gitkeep
```

**Anthropic Skills vs Custom Skills:**

- **Anthropic Skills** (in `core/`, `communication/`, `design/`, `documents/`)
  - Professional skills from Anthropic's curated collection
  - Production-tested and well-documented
  - Referenced as submodule or copied into repository
  - Licensed under Apache 2.0 or source-available

- **Custom Skills** (in `custom/`)
  - Project-specific or organization-specific skills
  - Created using the template in `custom/template/`
  - Tailored to your unique workflows and requirements
  - Your choice of license

**Project-Specific Skills Location:**

Projects can define their own skills in `.ai-agents/skills/` which override library skills:

```
your-project/
└── .ai-agents/
    └── skills/
        └── custom/
            └── my-workflow/
                └── SKILL.md
```

### Skill Composition Process

The `compose-agent.py` script handles skill loading automatically:

```python
# Skill resolution process
def resolve_skill_path(skill_name):
    # 1. Check if skill includes category (e.g., "design/theme-factory")
    if '/' in skill_name:
        skill_path = f"skills/{skill_name}.md"
    else:
        # 2. Default to core category (e.g., "artifacts-builder" → "skills/core/artifacts-builder.md")
        skill_path = f"skills/core/{skill_name}.md"

    # 3. Check library skills directory first
    library_skill = library_path / skill_path
    if library_skill.exists():
        return library_skill

    # 4. Check project-specific skills directory
    project_skill = project_path / ".ai-agents" / skill_path
    if project_skill.exists():
        return project_skill

    # 5. Skill not found - warning issued
    return None
```

**Resolution Order:**

1. **Explicit category**: If skill specified as `"category/skill-name"`, look only in that category
2. **Default category**: If skill specified as `"skill-name"`, default to `core/` category
3. **Library first**: Check library's `skills/` directory
4. **Project override**: Check project's `.ai-agents/skills/` directory
5. **Not found**: Issue warning and continue (agent still usable)

**Token Budget Considerations:**

Each skill adds to the agent's base token count:

| Skill Category | Avg Tokens | Example |
|----------------|------------|---------|
| Core Development | 3,000-5,000 | artifacts-builder: ~3,500 |
| Communication | 2,500-3,500 | internal-comms: ~3,000 |
| Design | 2,000-3,000 | theme-factory: ~2,500 |
| Documents | 3,000-4,000 | docx: ~3,500 |
| Custom | Varies | Depends on complexity |

**Recommended Token Budget by Agent:**

- **Minimal** (0 skills): 3,000-5,000 tokens (base only)
- **Standard** (1-2 skills): 6,000-10,000 tokens
- **Advanced** (3-4 skills): 10,000-15,000 tokens
- **Specialized** (5+ skills): 15,000+ tokens (⚠️ monitor carefully)

### Skills by Agent Type

Recommended skill assignments based on agent roles:

| Agent Type | Primary Skills | Optional Skills | Token Budget |
|------------|---------------|-----------------|--------------|
| **Manager** | internal-comms, xlsx | docx, pptx, pdf | 8,000-12,000 |
| **Frontend Dev** | artifacts-builder, theme-factory | webapp-testing, canvas-design | 9,000-15,000 |
| **Backend Dev** | mcp-builder | webapp-testing, xlsx | 7,000-11,000 |
| **QA Tester** | webapp-testing | docx, xlsx | 6,000-10,000 |
| **Architect** | skill-creator, mcp-builder | docx, pptx | 7,000-12,000 |
| **Mobile Dev** | theme-factory | artifacts-builder | 8,000-13,000 |

**Example Configurations:**

**Frontend Developer (Standard)**:
```yaml
frontend_developer:
  base: "base/software-developer.md"        # ~3,000 tokens
  platforms:
    - "platforms/web/frontend-developer.md" # ~2,500 tokens
  skills:
    - "core/artifacts-builder"              # ~3,500 tokens
    - "design/theme-factory"                # ~2,500 tokens
  # Total: ~11,500 tokens (within budget)
```

**Backend Developer (Minimal)**:
```yaml
backend_developer:
  base: "base/software-developer.md"        # ~3,000 tokens
  platforms:
    - "platforms/web/backend-developer.md"  # ~2,500 tokens
  skills:
    - "core/mcp-builder"                    # ~4,500 tokens
  # Total: ~10,000 tokens (within budget)
```

**Manager (Advanced)**:
```yaml
team_manager:
  base: "base/manager.md"                   # ~3,500 tokens
  skills:
    - "communication/internal-comms"        # ~3,000 tokens
    - "documents/xlsx"                      # ~4,000 tokens
    - "documents/docx"                      # ~3,500 tokens
  # Total: ~14,000 tokens (approaching limit)
```

### Custom Skills

#### Creating Project-Specific Skills

Projects can create custom skills tailored to their specific workflows:

**Step 1: Use the Template**
```bash
cp -r skills/custom/template skills/custom/my-workflow
cd skills/custom/my-workflow
```

**Step 2: Edit SKILL.md**
```markdown
---
name: my-workflow
description: Custom workflow for our project's specific needs
license: MIT
---

# My Workflow Skill

Instructions for this specialized workflow...
```

**Step 3: Add Supporting Resources** (optional)
```
my-workflow/
├── SKILL.md              # Main instructions
├── scripts/              # Automation scripts
│   └── helper.py
├── references/           # Documentation
│   └── api-guide.md
└── assets/              # Templates, configs
    └── template.json
```

**Step 4: Reference in Configuration**
```yaml
agents:
  backend_developer:
    skills:
      - "custom/my-workflow"  # Automatically resolves to custom/my-workflow/SKILL.md
```

#### Best Practices for Custom Skills

1. **Keep Skills Focused**: One skill = one clear purpose
2. **Use Progressive Disclosure**: Organize from high-level to detailed
3. **Include Examples**: Show concrete usage patterns
4. **Bundle Resources**: Scripts for deterministic operations
5. **Document Prerequisites**: Required libraries, tools, knowledge
6. **Test Thoroughly**: Verify with target agents before deployment
7. **Version Control**: Track changes and maintain compatibility

#### Advanced: Skill Creator Skill

For sophisticated skill development, use the `skill-creator` skill:

```yaml
architect:
  skills:
    - "core/skill-creator"  # Provides comprehensive skill development guidance
```

This skill provides:
- Systematic design methodology
- Progressive disclosure patterns
- Resource bundling strategies
- Testing and iteration workflows
- Packaging for distribution

### Token Budget Management with Skills

#### Updated Guidelines

With skills integrated, token budget management becomes more critical:

**Budget Allocation:**

```
Claude Sonnet 4.5: 200,000 tokens total
├── Agent Prompt: 6,000-12,000 (3-6%)
│   ├── Base: 3,000-4,000
│   ├── Platform: 2,000-3,000
│   ├── Skills: 0-6,000 (0-3 skills)
│   └── Project Context: 1,000-2,000
│
└── Conversation: 188,000-194,000 (94-97%)
    ├── Working Memory: 50%
    ├── Cached Context: 30%
    └── Buffer: ~17%
```

**Warning Thresholds:**

| Threshold | Agent Prompt Size | Action Required |
|-----------|-------------------|-----------------|
| **Green** | < 9,000 tokens | No action |
| **Yellow** | 9,000-10,500 tokens | Review skills, consider removing non-essential |
| **Orange** | 10,500-12,000 tokens | Remove 1-2 skills or reduce context |
| **Red** | > 12,000 tokens | ⚠️ Immediate reduction required |

**Automatic Warnings:**

The composition script automatically warns when approaching limits:

```bash
$ python compose-agent.py --config config.yml --agent frontend_developer

✓ Saved: frontend_developer.md
  Tokens: 11,200 / 12,000 recommended
  Context usage: 5.60%
  ⚠️  Approaching token budget limit
  Remaining budget: 800 tokens
```

**Over-Budget Suggestions:**

When over budget, the script suggests reductions:

```bash
  ⚠️  WARNING: Agent prompt exceeds recommended size!
  Recommendation: 1,500 tokens over budget

  Suggestions to reduce token usage:
  - Consider removing 3 skill(s)
    Skills: artifacts-builder, theme-factory, webapp-testing
  - Review 4 project context files
```

#### Optimization Strategies

**Strategy 1: Skill Prioritization**
```yaml
# Before (15,000 tokens - too much)
frontend_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"
    - "core/webapp-testing"
    - "design/canvas-design"

# After (11,500 tokens - optimized)
frontend_developer:
  skills:
    - "core/artifacts-builder"      # Essential
    - "design/theme-factory"        # Essential
  # Move webapp-testing to QA tester
  # Remove canvas-design (rarely used)
```

**Strategy 2: Context Consolidation**
```yaml
# Before (many small files)
project_context:
  - ".ai-agents/context/architecture.md"
  - ".ai-agents/context/coding-standards.md"
  - ".ai-agents/context/api-contracts.md"
  - ".ai-agents/context/type-definitions.md"
  - ".ai-agents/context/deployment.md"

# After (consolidated)
project_context:
  - ".ai-agents/context/core-knowledge.md"  # Combined essential info
  - ".ai-agents/context/api-contracts.md"   # Keep separate (frequently updated)
```

**Strategy 3: Specialized Agents**
```yaml
# Instead of one agent with all skills
super_developer:
  skills: [artifacts-builder, mcp-builder, webapp-testing, theme-factory]

# Create focused agents
frontend_developer:
  skills: [artifacts-builder, theme-factory]

backend_developer:
  skills: [mcp-builder]

qa_tester:
  skills: [webapp-testing]
```

**Strategy 4: Project-Specific Overrides**

Move rarely-used information out of base prompt:

```yaml
# Keep in prompt (always needed)
project_context:
  - ".ai-agents/context/architecture.md"
  - ".ai-agents/context/api-contracts.md"

# Move to RAG/vector DB (reference when needed)
# - coding-standards.md
# - troubleshooting-guide.md
# - deployment-procedures.md
```

### Best Practices

#### 1. Strategic Skill Selection

**Do:**
- Assign 1-3 skills per agent based on primary function
- Choose skills that align with agent's platform augmentation
- Test agents with skills before adding more
- Monitor actual skill usage in conversations

**Don't:**
- Add all available skills to every agent
- Assign skills that overlap with platform augmentation
- Include skills "just in case" - add when needed
- Ignore token budget warnings

#### 2. Skill Composition Strategies

**Layered Approach:**
```yaml
# Phase 1: Start minimal
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  # No skills yet - validate base functionality

# Phase 2: Add essential skills
frontend_developer:
  skills:
    - "core/artifacts-builder"  # Primary need identified

# Phase 3: Add complementary skills
frontend_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"    # Improves UI quality
```

**Role-Based Assignment:**
```yaml
# Manager: Communication & documentation focus
team_manager:
  skills:
    - "communication/internal-comms"
    - "documents/xlsx"

# Frontend: UI development focus
frontend_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"

# Backend: Integration focus
backend_developer:
  skills:
    - "core/mcp-builder"

# QA: Testing focus
qa_tester:
  skills:
    - "core/webapp-testing"
```

#### 3. Monitoring Skill Effectiveness

Track whether skills are actually being used:

**Metrics to Monitor:**
- **Usage frequency**: How often is each skill referenced?
- **Success rate**: Do tasks succeed when skills are available?
- **Token efficiency**: Is the skill worth its token cost?
- **Agent feedback**: Does agent report skills as helpful?

**Example Tracking:**
```yaml
# In project documentation
skill_usage_log:
  artifacts-builder:
    used_in_sessions: 45
    successful_tasks: 42
    avg_tokens: 3500
    value_rating: "high"
    decision: "keep"

  canvas-design:
    used_in_sessions: 2
    successful_tasks: 2
    avg_tokens: 2000
    value_rating: "low"
    decision: "remove - rarely used"
```

#### 4. Version Management

**Library Version Pinning:**
```yaml
agent_library:
  version: "1.0.0"  # Pin to specific version
  update_strategy: "manual"  # Explicit updates only
```

**Skills Version Tracking:**
```markdown
# In composed agent prompt
# Skills loaded:
# - artifacts-builder (v1.2.0, 3500 tokens)
# - theme-factory (v1.0.0, 2500 tokens)
# Total skills: 6000 tokens
```

#### 5. Testing New Skills

Before adding a skill to production:

1. **Compose in test environment**
```bash
python compose-agent.py --config test-config.yml --agent test_developer
```

2. **Review token impact**
```
✓ Tokens: 9,800 / 12,000 recommended
  Context usage: 4.90%
```

3. **Test with sample tasks**
- Verify skill is loaded correctly
- Confirm agent references skill appropriately
- Validate skill improves performance

4. **Deploy to production**
- Update production config
- Recompose production agents
- Monitor usage in real sessions

---

## Repository Structure

```
AI_agents/
├── README.md                    # Overview and quick start
├── ARCHITECTURE.md              # This file
├── Context_Engineering.md       # Foundational guide
│
├── base/                        # Base agent prompts
│   ├── software-developer.md
│   ├── manager.md
│   ├── qa-tester.md
│   └── architect.md
│
├── platforms/                   # Platform specializations
│   ├── web/
│   │   ├── frontend-developer.md
│   │   └── backend-developer.md
│   ├── mobile/
│   │   └── mobile-developer.md
│   └── desktop/
│       └── desktop-developer.md
│
├── tools/                       # Tool definitions
│   ├── git-tools.md
│   ├── testing-tools.md
│   ├── build-tools.md
│   ├── communication-tools.md
│   └── analysis-tools.md
│
├── schemas/                     # JSON schemas
│   ├── communication-protocol.json
│   ├── state-management.json
│   ├── agent-schema.json
│   └── project-config.json
│
├── memory/                      # RAG and memory
│   ├── knowledge-base/
│   │   ├── best-practices/
│   │   ├── common-patterns/
│   │   └── troubleshooting/
│   └── vector-db-schemas/
│
├── workflows/                   # Multi-agent patterns
│   ├── feature-development.md
│   ├── bug-fixing.md
│   └── code-review.md
│
├── templates/                   # Reusable templates
│   ├── system-prompts/
│   ├── instruction-sets/
│   └── output-formats/
│
├── examples/                    # Example projects
│   ├── web-app-team/
│   │   ├── config.yml
│   │   └── README.md
│   └── mobile-app-team/
│       ├── config.yml
│       └── README.md
│
└── scripts/                     # Automation tools
    ├── compose-agent.py         # Agent composition
    ├── validate-prompts.py      # Prompt validation
    └── deploy-agents.sh         # Agent deployment
```

---

## Integration Guide

### Step 1: Add Library to Your Project

**Option A: Git Submodule (Recommended)**
```bash
cd your-project
git submodule add git@github.com:org/AI_agents.git .ai-agents/library
git submodule update --init --recursive
```

**Option B: Clone**
```bash
cd your-project
git clone git@github.com:org/AI_agents.git .ai-agents/library
```

### Step 2: Create Project Structure

```bash
mkdir -p .ai-agents/{context,state,checkpoints,memory,workflows}
```

### Step 3: Create Configuration

Create `.ai-agents/config.yml`:

```yaml
project_id: "your-project"
project_name: "Your Project Name"

agent_library:
  repo: "git@github.com:org/AI_agents.git"
  version: "1.0.0"

agents:
  team_manager:
    base: "base/manager.md"
    # ... configuration

  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    # ... configuration
```

### Step 4: Create Context Files

Create these files in `.ai-agents/context/`:

- `architecture.md` - System architecture
- `coding-standards.md` - Team conventions
- `api-contracts.md` - API specifications
- `type-definitions.md` - Shared types

### Step 5: Compose Agents

```bash
cd .ai-agents/library
python scripts/compose-agent.py \
  --config ../../config.yml \
  --all \
  --output ../../composed
```

### Step 6: Deploy Agents

Use the composed prompts to initialize your AI agents with your LLM provider.

---

## Best Practices

### 1. Start Simple, Add Complexity

```
Phase 1: One agent (developer)
Phase 2: Add manager
Phase 3: Add specialists (QA, architect)
Phase 4: Add platform-specific agents
```

### 2. Define Interfaces First

Before implementation:
- Define API contracts
- Define type definitions
- Define data models
- Document in `.ai-agents/context/`

### 3. Use Branch Isolation

```
✓ feature/auth/agent/backend-dev/jwt-service
✗ feature/auth  (multiple agents on same branch)
```

### 4. Monitor Context Usage

```python
# Implement context monitoring
if context_usage > 0.75:
    create_checkpoint()
    compress_old_messages()

if context_usage > 0.85:
    alert_manager()
    request_guidance()
```

### 5. Regular Checkpoints

- Every 10 turns
- Before large operations
- At context warning thresholds
- Before session end

### 6. Quality Gates

Enforce before merging:
- All tests passing
- Code review approved
- Coverage > threshold
- No linting errors
- CI pipeline passing

### 7. Communication Discipline

- Use structured JSON messages
- Report progress regularly (25%, 50%, 75%, 100%)
- Immediately report blockers
- Request coordination when needed

### 8. Version Control

- Lock to specific library version
- Test before upgrading
- Use semantic versioning
- Maintain changelog

---

## Troubleshooting

### Issue: Agent Conflicts

**Symptoms:**
- Merge conflicts
- Agents modifying same files

**Solutions:**
1. Use branch isolation
2. Implement resource locking
3. Define clear ownership
4. Manager coordinates shared resources

### Issue: Context Overflow

**Symptoms:**
- Agent reports context at 90%+
- Information being lost
- Agent confused about task

**Solutions:**
1. Create immediate checkpoint
2. Compress conversation history
3. Move details to vector DB
4. Start fresh session with checkpoint

### Issue: Blocker Delays

**Symptoms:**
- Agent waiting on dependency
- Work stalled

**Solutions:**
1. Use interface-first development
2. Implement mocks/stubs
3. Continue with workaround
4. Manager reprioritizes blocking task

### Issue: Communication Breakdown

**Symptoms:**
- Agents not coordinating
- Duplicate work
- Incompatible interfaces

**Solutions:**
1. Enforce communication protocol
2. Manager facilitates coordination
3. Define interfaces before implementation
4. Regular sync meetings (manager-led)

### Issue: Quality Degradation

**Symptoms:**
- Tests failing
- Bugs increasing
- Code quality dropping

**Solutions:**
1. Enforce quality gates
2. Require code reviews
3. Increase test coverage requirements
4. Add automated quality checks

---

## Version History

- **1.0.0** (2025-11-20): Initial architecture documentation

---

## References

- [Context Engineering Guide](Context_Engineering.md) - Foundational principles
- [Communication Protocol Schema](schemas/communication-protocol.json) - Message formats
- [State Management Schema](schemas/state-management.json) - State structure
- [Project Config Schema](schemas/project-config.json) - Configuration format
- [Examples](examples/) - Reference implementations

---

## Contributing

When adding new agents, augmentations, or tools:

1. Follow existing structure and conventions
2. Include version in file header
3. Document usage notes
4. Provide examples
5. Update this ARCHITECTURE.md
6. Test with example projects
7. Submit PR with detailed description

---

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: This repository's docs/
- **Examples**: examples/ directory

---

**Remember**: This architecture is based on the Context Engineering Guide. When in doubt, refer back to those principles for guidance.
