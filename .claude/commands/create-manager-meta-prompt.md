---
description: Generate optimized manager prompt from plan files with state coordination and Task tool delegation
argument-hint: ['@path/to/PLAN.md or plan description']
---

# Implementation Instructions

When this command is invoked, you will:
1. Analyze the provided plan file or description
2. Recommend appropriate workflow mode (Simple/Complex/Automated)
3. Generate an optimized manager prompt
4. Output setup instructions

## Step 1: Analyze the Plan

### If plan file provided (@path/to/PLAN.md):

Read the plan file and extract:

**Task Metrics:**
- Count all numbered items, subtasks, and action items
- Count phases/sections (each phase might have multiple tasks)
- Look for task lists with checkboxes `- [ ]` or numbered lists

**Duration Signals:**
- Look for explicit time estimates: "1 day", "3 days", "2 weeks"
- Look for multi-session indicators: "multi-session", "across multiple days"
- Count phases (3+ phases usually indicates multi-day work)

**Infrastructure Keywords:**
- Setup indicators: "setup", "infrastructure", "configure", "initialize", "install"
- New project indicators: "new project", "from scratch", "bootstrap"
- Existing project indicators: "existing", "current", "add to"

**Agent Count Signals:**
- Count distinct roles mentioned: Backend, Frontend, QA, IT Specialist, DevOps, etc.
- Look for parallel work mentions: "parallel", "concurrent", "simultaneously"

**Quality Requirements:**
- Code review: "review", "code review", "peer review", "senior engineer"
- Testing: "E2E", "integration tests", "test coverage"
- CI/CD: "pipeline", "deployment", "automation", "CI/CD"

### If description provided (no @ file):

Extract same signals from the text description.

## Step 2: Score and Recommend

Apply decision criteria to metrics:

### Simple Mode Criteria (Score 0-3 points):
- Tasks: 1-10 (0 points)
- Duration: 1-3 days (0 points)
- Infrastructure: Existing/none (0 points)
- Agents: 2-5 (0 points)
- Quality: Basic/optional (0 points)

### Complex Mode Criteria (Score 4-8 points):
- Tasks: 10-20 (1 point)
- Duration: 3-7 days (1 point)
- Infrastructure: New setup needed (2 points)
- Agents: 5-10 (1 point)
- Quality: Code review + E2E tests (2 points)
- Multi-phase: 3+ phases (1 point)

### Fully Automated Criteria (Score 9+ points):
- Tasks: 20+ (3 points)
- Duration: 7+ days / multi-week (2 points)
- Infrastructure: Production/enterprise (3 points)
- Agents: 10+ (3 points)
- Quality: CI/CD + automation (3 points)

**Scoring Logic:**
```
Total Score:
  0-3:  Simple Mode
  4-8:  Complex Mode
  9+:   Fully Automated
```

**Override Flags:**
- `--mode simple` or `--simple` → Force Simple
- `--mode complex` or `--complex` → Force Complex
- `--mode automated` or `--automated` → Force Automated

## Step 3: Generate Recommendation Report

Output this analysis:

```markdown
# Workflow Mode Analysis

## Plan Overview
- **Source:** [file path or "description"]
- **Total Tasks:** [number]
- **Estimated Duration:** [X days/weeks]
- **Phases:** [number]

## Metrics Analysis

### Task Breakdown
- Total tasks identified: [number]
- Tasks per phase: [breakdown]

### Infrastructure Assessment
- Type: [Existing | New Setup | Production]
- Keywords found: [list]

### Team Size Estimation
- Estimated agents: [number]
- Roles needed: [list]

### Quality Requirements
- Code review: [Yes/No]
- E2E testing: [Yes/No]
- CI/CD: [Yes/No]

## Scoring

| Criteria | Value | Points |
|----------|-------|--------|
| Tasks | [number] | [points] |
| Duration | [estimate] | [points] |
| Infrastructure | [type] | [points] |
| Agents | [number] | [points] |
| Quality | [requirements] | [points] |
| **TOTAL** | | **[total]** |

## Recommendation

**Recommended Mode:** [Simple Mode | Complex Mode | Fully Automated]

**Reasoning:**
[2-3 sentences explaining why this mode fits the project based on the metrics]

**State Files Required:**

[If Simple Mode:]
- `.ai-agents/state/team-communication.json` (coordination)

[If Complex Mode:]
- `.ai-agents/state/team-communication.json` (coordination)
- `.ai-agents/state/session-progress.json` (continuity)
- `.ai-agents/state/feature-tracking.json` (verification)

[If Fully Automated:]
- Use programmatic orchestration: `scripts/orchestration/programmatic_orchestrator.py`
- See: `docs/guides/ORCHESTRATION.md`

```

## Step 4: Generate Manager Prompt

Based on the recommended mode, generate the manager prompt:

### For Simple Mode:

```markdown
# Manager: [Project Name]

You are the Manager agent coordinating a team to [objective from plan].

## Mode
**Simple Mode** - Direct task delegation

## Objective
[Extract and summarize the main objective from the plan]

## Plan Summary
[Summarize the plan in 3-5 bullet points]

## State File Setup

Before starting, ensure state files exist:

\`\`\`bash
# Create state directory
mkdir -p .ai-agents/state

# Initialize team communication file
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {
    "project": "[project name]",
    "objective": "[objective]",
    "mode": "simple",
    "tasks": []
  },
  "agent_updates": [],
  "integration_requests": []
}
EOF
\`\`\`

## Your Role

Read the manager guide: `@prompts/manager-task-delegation.md`

**Your workflow:**
1. Break down features into 2-4 concrete tasks
2. Use Task tool to spawn specialized agents
3. Monitor progress via team-communication.json
4. Coordinate integration

**Your constraints:**
- DO: Plan, delegate, monitor, decide, coordinate
- DON'T: Implement code, review details, read code files, commit changes

## Execution Plan

[Generate task breakdown from the plan with specific Task tool delegation instructions]

### Task 1: [Task Name]
**Agent:** [Role]
**Delegation:**
\`\`\`
description: "[3-5 word summary]"
subagent_type: "general-purpose"
prompt: "You are a [Role] working on [project].

Your Task: [Specific instructions]

Read team-communication.json for context.
Update your status when complete.

[Specific requirements from plan]"
\`\`\`

[Repeat for each task...]

## Coordination Protocol

1. Read team-communication.json before each decision
2. Spawn agents ONE AT A TIME via Task tool
3. Wait for completion before spawning next
4. Check agent_updates for progress
5. Make decisions on questions_for_manager
6. At session end: Use /whats-next for handoff

## Success Criteria

[Extract success criteria from plan]

```

### For Complex Mode:

Same structure as Simple Mode, but add:

```markdown
## Mode
**Complex Mode** - Infrastructure validation + code review

## State File Setup

\`\`\`bash
# Create state directory
mkdir -p .ai-agents/state

# Initialize all three state files
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {
    "project": "[project name]",
    "objective": "[objective]",
    "mode": "complex",
    "tasks": []
  },
  "agent_updates": [],
  "integration_requests": []
}
EOF

cat > .ai-agents/state/session-progress.json << 'EOF'
{
  "session_id": "001",
  "start_time": "[current timestamp]",
  "current_phase": "setup",
  "completed_phases": [],
  "active_tasks": [],
  "completed_tasks": [],
  "blocked_tasks": [],
  "decisions_made": [],
  "next_session_priority": ""
}
EOF

cat > .ai-agents/state/feature-tracking.json << 'EOF'
{
  "feature": "[feature name]",
  "status": "in_progress",
  "verification_checklist": [],
  "integration_status": "pending",
  "review_status": "pending"
}
EOF
\`\`\`

## Your Workflow

**Phase 0: Infrastructure Validation**
Delegate to IT Specialist FIRST to validate infrastructure setup.

**Phase 1-N: Task Execution**
Delegate to task agents after IT Specialist confirms ready.

**Phase Final: Code Review + Integration**
Delegate to Senior Engineer for comprehensive review and integration.

## Execution Plan

### Phase 0: Infrastructure Validation
[IT Specialist delegation with infrastructure checks]

### Phase 1: [Phase Name]
[Task delegations...]

### Phase N: Code Review + Integration
[Senior Engineer delegation with review requirements]
```

### For Fully Automated Mode:

```markdown
# Manager: [Project Name]

## Recommendation: Use Programmatic Orchestration

Your project requires **Fully Automated** workflow with 10+ agents and production deployment.

**Instead of manual manager coordination, use:**

\`\`\`bash
# Set up orchestrator
cd scripts/orchestration/

# Configure agents
python programmatic_orchestrator.py setup --plan @[path/to/plan]

# Run workflow
python programmatic_orchestrator.py run --parallel

# Monitor progress
python programmatic_orchestrator.py status
\`\`\`

## Resources

- **Setup Guide:** `docs/guides/ORCHESTRATION.md`
- **API Configuration:** `docs/guides/API_SETUP.md`
- **Example Config:** `scripts/orchestration/example-config.yaml`

## Why Programmatic?

Your project requires:
- [List reasons based on analysis: 10+ agents, production deployment, etc.]

**Manual coordination becomes inefficient at this scale.**

## Manual Alternative (Not Recommended)

If you prefer manual coordination despite the scale, use Complex Mode:

\`\`\`
/create-manager-meta-prompt @[plan] --mode complex
\`\`\`

But be aware:
- Context management becomes challenging
- Session continuity requires careful handoffs
- Integration complexity increases
- Recommend programmatic approach instead
```

## Step 5: Present Options

After generating the prompt, present:

```markdown
---

## Generated Manager Prompt

[Show the generated prompt above]

---

## Next Steps

1. **Review the generated prompt** - Make any adjustments needed
2. **Copy the state file setup commands** - Run them in your project
3. **Copy the manager prompt** - Paste into a new Claude Code session
4. **Start execution** - The manager will coordinate the team

## Override Options

If you want to use a different mode:

\`\`\`bash
# Force Simple Mode
/create-manager-meta-prompt @[plan] --mode simple

# Force Complex Mode
/create-manager-meta-prompt @[plan] --mode complex

# Force Fully Automated
/create-manager-meta-prompt @[plan] --mode automated
\`\`\`

## Resources

- **Manager Guide:** `prompts/manager-task-delegation.md`
- **Quick Reference:** `prompts/manager-quick-reference.md`
- **State Files:** `docs/reference/CHEAT_SHEET/01-state-files.md`
- **Workflows:** `docs/reference/CHEAT_SHEET/05-workflows.md`

```

---

# Command Reference

## Usage

### From Plan File
```
/create-manager-meta-prompt @.planning/PLAN-authentication.md
```

### From Description
```
/create-manager-meta-prompt "Implement authentication system with JWT"
```

### With Override
```
/create-manager-meta-prompt @PLAN.md --mode complex
/create-manager-meta-prompt @PLAN.md --complex  # shorthand
```

## What This Does

1. Analyzes your plan (tasks, duration, infrastructure, agents, quality)
2. Scores metrics against decision criteria
3. Recommends workflow mode with full reasoning
4. Generates customized manager prompt
5. Provides state file setup commands (copy-paste ready)
6. Outputs everything you need to start

## Workflow Modes

### Simple Mode (Score 0-3)
- **Use for:** 1-10 tasks, 1-3 days, existing infrastructure
- **Workflow:** Manager → Task Agents → Integration
- **State Files:** team-communication.json only
- **Best for:** 90% of projects

### Complex Mode (Score 4-8)
- **Use for:** 10-20 tasks, 3-7 days, new infrastructure, code review
- **Workflow:** Manager → IT Specialist → Task Agents → Senior Engineer
- **State Files:** team-communication + session-progress + feature-tracking
- **Best for:** 10% of projects, first features, multi-session work

### Fully Automated (Score 9+)
- **Use for:** 20+ tasks, multi-week, production, 10+ agents, CI/CD
- **Approach:** Use programmatic orchestration scripts
- **State Files:** Managed by orchestrator
- **Best for:** Enterprise scale, production pipelines

## Decision Criteria

| Metric | Simple | Complex | Automated |
|--------|--------|---------|-----------|
| Tasks | 1-10 | 10-20 | 20+ |
| Duration | 1-3 days | 3-7 days | 7+ days |
| Infrastructure | Existing | New setup | Production |
| Agents | 2-5 | 5-10 | 10+ |
| Quality | Basic | Review + E2E | CI/CD |

## Examples

**Simple:** "Add login form with validation"
- 3 tasks, 1 day, existing infrastructure
- Score: 0 → Simple Mode

**Complex:** "Build authentication system from scratch"
- 15 tasks, 5 days, new database + email setup
- Score: 6 → Complex Mode

**Automated:** "Enterprise CI/CD pipeline for microservices"
- 50+ tasks, multi-week, 15+ agents
- Score: 12 → Fully Automated

## Tips

**Do:**
- ✅ Create plan first with `/create-plan`
- ✅ Review generated prompt before using
- ✅ Run state file setup commands
- ✅ Trust the recommendation (but can override)

**Don't:**
- ❌ Skip state file setup
- ❌ Use Complex Mode for simple 1-day tasks
- ❌ Modify generated prompt heavily

---

**Implementation Note:** This command analyzes your plan and generates an optimized manager prompt following the Task tool delegation pattern documented in `prompts/manager-task-delegation.md`.
