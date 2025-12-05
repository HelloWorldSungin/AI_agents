# Quick Start

Quick commands to get started with the AI Agents Library.

**Version:** 1.3.0
**Last Updated:** 2025-12-04

---

## Installation Options

### Option A: Generate from Starter Template (Fastest)

Best for existing projects - generates `.ai-agents/` directory with context files.

```bash
python3 starter-templates/generate-template.py --interactive
```

### Option B: Add as Git Submodule (Stays Updated)

Best for ongoing projects that want to stay synced with library updates.

```bash
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library
```

### Option C: Direct Copy (Full Control)

Best for projects that want full control and customization.

```bash
cp -r path/to/AI_agents .ai-agents/
```

---

## Compose Agents

Once installed, compose agents from your config:

```bash
cd .ai-agents/library
python scripts/compose-agent.py --config ../config.yml --all
```

**Output:** Composed agents in `.ai-agents/composed/`

---

## What's Next?

- **New Project?** → See [06-scripts-tools.md](06-scripts-tools.md#starter-templates) for starter templates
- **Existing Project?** → Read [01-state-files.md](01-state-files.md) to set up state management
- **Multi-Agent Setup?** → Check [05-workflows.md](05-workflows.md) for workflow modes
- **Need Help?** → See [Getting Help](#getting-help) below

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/HelloWorldSungin/AI_agents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HelloWorldSungin/AI_agents/discussions)
- **Documentation:** This repository
- **Start Here:** `README.md` → `Context_Engineering.md` → `ARCHITECTURE.md`

---

[← Back to Index](index.md) | [Next: State Files →](01-state-files.md)
