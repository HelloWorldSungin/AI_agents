# AI Agents Library

A comprehensive, modular library for building multi-agent software development systems based on advanced context engineering principles.

**Version:** 1.0.0

---

## What is This?

This library provides reusable, composable AI agent prompts and infrastructure for teams of AI agents working together on software projects. Instead of manually crafting prompts for each project, you can compose specialized agents from modular components.

### Key Features

✨ **Modular Design**: Base prompts + platform augmentations + project context
🤝 **Multi-Agent Coordination**: Manager-led team collaboration
🧠 **Advanced Context Management**: Never lose critical information
🌲 **Git-Based Workflow**: Branch isolation prevents conflicts
📡 **Structured Communication**: JSON-based inter-agent messaging
🎯 **Platform Agnostic**: Web, mobile, desktop, and more

---

## Quick Start

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
- `type-definitions.md` - Shared types

See [examples/](examples/) for templates.

### 5. Compose Your Agents

```bash
cd .ai-agents/library
python scripts/compose-agent.py --config ../../config.yml --all
```

This generates complete agent prompts in `.ai-agents/composed/`.

### 6. Deploy

Use the composed prompts to initialize your AI agents with your LLM provider.

---

## Architecture

### Layered Composition

```
┌─────────────────────────────────────────┐
│   Project Context (Your Requirements)  │
│   • Business logic                      │
│   • API contracts                       │
│   • Team conventions                    │
├─────────────────────────────────────────┤
│   Platform Augmentation (Specialized)   │
│   • Web/Mobile/Desktop expertise        │
│   • Framework knowledge                 │
│   • Platform best practices             │
├─────────────────────────────────────────┤
│   Base Agent (Universal)                │
│   • Core software engineering           │
│   • Testing, debugging, git             │
│   • Security, performance               │
└─────────────────────────────────────────┘
```

### Multi-Agent Team

```
┌──────────────┐
│   Manager    │ ← Orchestrates the team
└──────┬───────┘
       │
   ┌───┴───┬──────────┬─────────┐
   │       │          │         │
┌──▼───┐ ┌▼──────┐ ┌─▼─────┐ ┌─▼──┐
│Archi-│ │Frontend│ │Backend│ │ QA │
│tect  │ │  Dev   │ │  Dev  │ │Test│
└──────┘ └────────┘ └───────┘ └────┘
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
│   └── architect.md
│
├── platforms/               # Platform specializations
│   ├── web/
│   │   ├── frontend-developer.md
│   │   └── backend-developer.md
│   ├── mobile/
│   │   └── mobile-developer.md
│   └── ...
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

### Web Application Team

```yaml
# .ai-agents/config.yml
agents:
  team_manager:
    base: "base/manager.md"

  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/api-contracts.md"

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
```

See [examples/web-app-team/](examples/web-app-team/) for complete example.

### Mobile Application Team

See [examples/mobile-app-team/](examples/mobile-app-team/) for React Native example.

---

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - quick start guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed system architecture |
| [Context_Engineering.md](Context_Engineering.md) | Foundational principles (the "HOLY BIBLE") |
| [examples/](examples/) | Reference implementations |

---

## How It Works

### 1. User Makes a Request

```
User: "Implement user authentication"
```

### 2. Manager Breaks Down the Task

```
Manager creates:
├── TASK-001: Design auth architecture (Architect)
├── TASK-002: Implement JWT service (Backend Dev)
├── TASK-003: Create auth API (Backend Dev)
├── TASK-004: Build login form (Frontend Dev)
└── TASK-005: Write tests (QA Tester)
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
3. **Use Branch Isolation** - One branch per agent per task
4. **Monitor Context** - Watch for context usage warnings
5. **Regular Checkpoints** - Every 10 turns or at 75% context
6. **Quality Gates** - Enforce tests, reviews, coverage
7. **Structured Communication** - Use JSON message protocol

---

## Roadmap

- [ ] Additional platform augmentations (Desktop, Data, DevOps)
- [ ] More example projects
- [ ] Automated testing for prompts
- [ ] Visual workflow designer
- [ ] Metrics dashboard
- [ ] Integration with popular LLM providers

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
