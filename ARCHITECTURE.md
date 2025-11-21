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
