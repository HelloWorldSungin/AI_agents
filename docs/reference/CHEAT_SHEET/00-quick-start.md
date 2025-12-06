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

## Recommended Workflow

The most effective workflow for multi-agent projects:

### 1. Plan Your Project

Use the planning skill to research, make decisions, and break work into phases:

```bash
/create-plan "your project description"
```

**Example:**
```bash
/create-plan "Build authentication system with JWT, user registration, login, and password reset"
```

**Output:** `.planning/PLAN-[project].md` with:
- Research findings
- Decision rationale
- Phase breakdown
- Success criteria

### 2. Generate Manager Prompt

Create an optimized manager prompt from your plan:

```bash
/create-manager-meta-prompt @.planning/PLAN-[project].md
```

**What this does:**
- Analyzes your plan
- Generates manager prompt with:
  - Task Tool Delegation pattern
  - State file coordination
  - Agent spawning sequence
  - Progress tracking
  - Handoff instructions

**Output:** Ready-to-use manager prompt (copy and paste into Claude)

### 3. Set Up State Files

Create the coordination file:

```bash
mkdir -p .ai-agents/state
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {},
  "agent_updates": [],
  "integration_requests": []
}
EOF
```

**For Complex Mode** (multi-day, 5+ agents):
```bash
# Add session continuity
cat > .ai-agents/state/session-progress.json << 'EOF'
{
  "last_session": null,
  "current_phase": "initial-setup",
  "completed_tasks": [],
  "active_tasks": [],
  "blockers": [],
  "next_priorities": [],
  "git_baseline": null
}
EOF

# Add feature tracking
cat > .ai-agents/state/feature-tracking.json << 'EOF'
{
  "features": [],
  "summary": {"total": 0, "passing": 0, "in_progress": 0, "failing": 0}
}
EOF
```

### 4. Execute with Manager

Paste the generated manager prompt into Claude and let it coordinate:

```
Manager (stays lean at 15-25% context)
  ↓ spawns via Task tool
Agent 1 (fresh context) → completes → reports back
  ↓ Manager spawns next
Agent 2 (fresh context) → completes → reports back
  ↓ Manager spawns next
Agent 3 (fresh context) → completes → reports back
```

**Benefits:**
- ✅ Manager never accumulates context (stays lean)
- ✅ Each agent gets fresh context (15,000+ tokens working memory)
- ✅ Structured coordination via state files
- ✅ Clear progress tracking
- ✅ Easy to resume across sessions (Complex Mode)

### Workflow Summary

```
1. /create-plan "project"
   └─ Generates: .planning/PLAN-[project].md

2. /create-manager-meta-prompt @.planning/PLAN-[project].md
   └─ Generates: Optimized manager prompt

3. Set up state files (one-time)
   └─ Creates: .ai-agents/state/*.json

4. Paste manager prompt into Claude
   └─ Manager coordinates via Task tool delegation
   └─ Agents work with fresh context
   └─ State files track progress
```

**Time Investment:**
- Initial setup: 5 minutes (steps 1-3)
- Ongoing: Just step 1-2 per new project
- Benefit: 50% faster execution, scalable to any team size

### Workflow Modes

**Simple Mode** (default - 90% of projects):
- Use for: 1-3 days, existing infrastructure, 3-5 agents
- State files: `team-communication.json` only
- Pattern: Manager → Task Agents → Integration Agent
- Coordination: Human-coordinated or Task Tool Delegation

**Complex Mode** (10% of projects):
- Use for: Multi-day, new infrastructure, 5+ agents, code review required
- State files: All three (team-communication, session-progress, feature-tracking)
- Pattern: Manager → IT Specialist → Task Agents → Senior Engineer
- Coordination: Task Tool Delegation
- Add `--complex` flag: `/create-manager-meta-prompt @PLAN.md --complex`

**Multi-Session Manager Workflow** (for long projects):
```bash
# Session 1
/create-manager-meta-prompt @PLAN.md  # Creates @manager agent
@manager                               # Work as manager
/manager-handoff                       # Save state
/clear                                 # Clear context

# Session 2+
@manager /manager-resume               # Load + resume
# ... continue work ...
/manager-handoff                       # Save state
/clear                                 # Clear context
```
See: `05-workflows.md` > Multi-Session Manager Workflow

**Fully Automated** (advanced users):
- Use for: Large-scale (7+ agents), CI/CD automation, production deployments
- State files: All three + message queue
- Pattern: Programmatic orchestration via LLM APIs
- Coordination: Fully automated, true parallel execution
- Requires: Programming experience, API keys, orchestration scripts

**How Fully Automated Works:**
```python
# Orchestrator script reads config and spawns agents via API
orchestrator.py
  ├─ Spawns agents in parallel via Anthropic API
  ├─ Agents communicate via message queue (not through human)
  ├─ Monitors progress and handles failures
  └─ True concurrent execution
```

**Setup:**
1. Configure orchestrator: `scripts/orchestration/programmatic_orchestrator.py`
2. Set API keys: `export ANTHROPIC_API_KEY=...`
3. Define agent config: `orchestration-config.yml`
4. Run: `python scripts/orchestration/programmatic_orchestrator.py`

**Benefits:**
- ✅ True parallel execution (not sequential)
- ✅ Scales to many agents (10+)
- ✅ CI/CD integration ready
- ✅ Automatic retry and error handling
- ✅ Production-grade reliability

**Trade-offs:**
- ❌ Complex setup (requires programming)
- ❌ API costs (multiple concurrent calls)
- ❌ Less human control
- ❌ Harder to debug

**When to Use:**
- Production CI/CD pipelines
- Large enterprise systems (10+ agents)
- Automated testing workflows
- High-frequency operations
- When speed > human oversight

**See:**
- Detailed comparison: [05-workflows.md](05-workflows.md)
- Orchestration guide: `scripts/orchestration/COMPLETE_GUIDE.md`
- Advanced patterns: [07-advanced.md](07-advanced.md)

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
