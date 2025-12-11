# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

AI_agents is a modular library for building multi-agent software development systems. It provides composable AI agent prompts, skills, and infrastructure for teams of AI agents working together on software projects.

## Key Commands

### Agent Composition
```bash
# Compose a specific agent from config
python scripts/compose-agent.py --config .ai-agents/config.yml --agent frontend_developer

# Compose all agents defined in config
python scripts/compose-agent.py --config .ai-agents/config.yml --all

# Generate starter template for a new project
python starter-templates/generate-template.py --type web-app --name "ProjectName" --output /path/to/project
```

### Testing
```bash
# Run tests with pytest
python -m pytest tests/test_compose_agent.py -v

# Run tests with unittest (no pytest required)
python tests/test_compose_agent.py
```

### Tool Selector Setup (for other projects)
```bash
# Install AI_agents tools to another project
python scripts/setup-commands.py /path/to/project

# Install globally
python scripts/setup-commands.py --global

# List available tools
python scripts/setup-commands.py --list
```

### State Management Scripts
```bash
# Validate team communication file
python scripts/validate-team-communication.py

# Clean up team communication state
python scripts/cleanup-team-communication.py
```

## Architecture Overview

### Layered Composition Model
Agents are composed by layering:
1. **Base prompts** (`prompts/roles/`) - Universal agent capabilities
2. **Platform augmentations** (`platforms/`) - Platform-specific expertise (web, mobile)
3. **Skills** - Specialized capabilities via Anthropic Skills integration
4. **Project context** - User's project-specific documentation

### Directory Structure

- **prompts/roles/** - Base agent prompts (software-developer.md, manager.md, architect.md, etc.)
- **platforms/** - Platform specializations (web/frontend-developer.md, mobile/mobile-developer.md)
- **skills/** - Skills integration (custom/, anthropic/ submodule)
- **.claude/commands/** - Slash commands (create-prompt, debug, consider/*, etc.)
- **.claude/agents/** - Subagent definitions (skill-auditor, session-handoff)
- **.claude/skills/** - Symlinks to taches-cc-resources skills
- **external/** - Git submodules (anthropic-skills, taches-cc-resources)
- **schemas/** - JSON schemas for communication protocol, state management
- **scripts/** - Python tools (compose-agent.py, setup-commands.py)
- **starter-templates/** - Project template generator
- **examples/** - Example configurations (web-app-team/, mobile-app-team/)

### Agent Communication

Agents coordinate via three state files in `.ai-agents/state/`:
- **team-communication.json** - Real-time within-session coordination
- **session-progress.json** - Cross-session task tracking
- **feature-tracking.json** - Feature verification status

### Dual-Mode Workflow

- **Simple Mode** (default): Manager → Task Agents → Integration Agent
- **Complex Mode**: Manager → IT Specialist → Task Agents → Senior Engineer

## Configuration Format

Agent configs use YAML (see `examples/web-app-team/config.yml`):
```yaml
agents:
  frontend_developer:
    base: "prompts/roles/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "core/web-artifacts-builder"
    project_context:
      - ".ai-agents/context/architecture.md"
```

### Deferred Skill Loading

Skills can be loaded on-demand to reduce initial context:
```yaml
skills:
  always_loaded:
    - "core/skill-creator"
  deferred:
    - path: "testing/webapp-testing"
      triggers: ["test", "QA", "coverage"]
```

## Key Files

- **prompts/manager-task-delegation.md** - Comprehensive Manager workflow guide
- **prompts/manager-quick-reference.md** - Quick-start Manager template
- **schemas/communication-protocol.json** - Agent message format specification
- **scripts/compose_agent.py** - Core composition logic (AgentComposer class)

## Dependencies

- Python 3.8+
- PyYAML (`pip install pyyaml`)

## Slash Commands Available

The `/consider:*` commands provide thinking frameworks:
- `/consider:first-principles` - Break down to fundamentals
- `/consider:5-whys` - Root cause analysis
- `/consider:swot` - Strategic analysis
- `/consider:eisenhower-matrix` - Priority matrix

Workflow commands:
- `/debug` - Systematic debugging methodology
- `/whats-next` - Context handoff between sessions
- `/create-plan` - Hierarchical project planning
- `/manager-handoff` - Manager session state preservation
