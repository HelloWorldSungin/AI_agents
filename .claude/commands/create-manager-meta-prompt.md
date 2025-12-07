---
description: Generate optimized manager prompt from plan files with state coordination and Task tool delegation
argument-hint: ['@path/to/PLAN.md or plan description'] [--agent-name custom-name] [--mode simple|complex|automated]
allowed-tools: [Read, Write, Bash]
---

# Implementation Instructions

**IMPORTANT: You MUST complete ALL 6 steps below. Step 6 (creating the agent file) is REQUIRED.**

When this command is invoked, you will:
1. Analyze the provided plan file or description
2. Recommend appropriate workflow mode (Simple/Complex/Automated)
3. Generate recommendation report with scoring
4. Generate an optimized manager prompt
5. Present options and next steps
6. **CREATE THE MANAGER AGENT FILE** (REQUIRED - do not skip this step)

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

**Agent Name Argument:**
- `--agent-name custom-name` → Create agent file as `.claude/agents/custom-name.md`
- If not provided → Default to `.claude/agents/project-manager.md`

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
6. **After each phase/task completion:**
   - Run `/context` to check context window usage
   - Show user the context percentage
   - **If context > 70%:** Recommend `/manager-handoff` then resume with `@{agent_name} /manager-resume`
   - **If context < 70%:** Ask if user wants to continue or handoff
7. At session end: Use `/manager-handoff` for multi-session continuity

## Context Window Management

**After completing each phase or major task:**

1. Run `/context` command to check usage
2. Display to user:
   \`\`\`
   📊 Context Status: [X]% used

   [If > 70%]
   ⚠️  Context window is getting full. Recommended workflow:

   1. Run: /manager-handoff
   2. Run: /clear
   3. Resume: @{agent_name} /manager-resume

   This will preserve all progress while starting fresh.

   [If < 70%]
   ✅ Context window healthy.

   Options:
   - Continue with next phase
   - Handoff now for fresh context (optional)
   \`\`\`

3. Wait for user decision before proceeding

**Why this matters:**
- Prevents hitting context limits mid-task
- Gives user control over session management
- Ensures clean handoffs at logical breakpoints
- Maintains state continuity across sessions

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
After completion: Check context with `/context`

**Phase 1-N: Task Execution**
Delegate to task agents after IT Specialist confirms ready.
After each phase: Check context with `/context` - handoff if needed

**Phase Final: Code Review + Integration**
Delegate to Senior Engineer for comprehensive review and integration.
After completion: Check context with `/context`

**Context Management:**
- Run `/context` after each phase completes
- If context > 70%: Use `/manager-handoff` and resume with `@{agent_name} /manager-resume`
- Complex projects may require multiple handoffs across phases

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

After generating the prompt, present the following (then proceed to Step 6):

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

**→ Now proceed to Step 6 to create the agent file (required)**

---

## Step 6: Create Manager Agent File (REQUIRED)

**CRITICAL: This step is REQUIRED. Do not skip this step.**

Now create the manager agent file so it can be loaded with @manager syntax:

### Parse Agent Name

Extract agent name from arguments:
- Check `$ARGUMENTS` for `--agent-name` flag
- If found: Use the provided custom name
- If not found: Use default "project-manager"

### Determine File Path

**File Path:** `.claude/agents/{agent-name}.md`
- Default: `.claude/agents/project-manager.md`
- Custom (if `--agent-name` provided): `.claude/agents/{custom-name}.md`

### Create Directory if Needed

Ensure the agents directory exists:

```bash
# Check if .claude/agents/ exists, create if needed
if ! [ -d ".claude/agents" ]; then
  mkdir -p .claude/agents
fi
```

### Generate YAML Frontmatter

Extract information from the plan to populate frontmatter:

**Preferred (if extractable from plan):**
```yaml
---
name: {Project Name} Manager
description: Manager for {project name} coordinating {N} agents across {M} phases
---
```

**Fallback (if extraction difficult):**
```yaml
---
name: Project Manager
description: Manager agent coordinating multi-agent development workflow
---
```

Examples:
- Plan about "Authentication System" with 5 agents, 3 phases:
  ```yaml
  ---
  name: Authentication System Manager
  description: Manager for Authentication System coordinating 5 agents across 3 phases
  ---
  ```
- Generic fallback:
  ```yaml
  ---
  name: Project Manager
  description: Manager agent coordinating multi-agent development workflow
  ---
  ```

### Write Agent File

Use Write tool to create or update the agent file:

**File Structure:**
```markdown
---
name: {Project Name} Manager
description: {Description from above}
---

{Full generated manager prompt from Step 4}
```

**Important:** The manager prompt written to the file should be the EXACT prompt generated in Step 4 (including all setup commands, execution plan, etc.)

### Output Agent File Confirmation

After creating the agent file, show this confirmation to the user:

```markdown
---

## Manager Agent File Created ✓

**File:** `.claude/agents/{agent-name}.md`

### How to Use This Manager

**In a fresh context:**
```bash
@manager  # if using default name (project-manager)
# or
@{custom-name}  # if you used --agent-name
```

**Multi-session workflow:**

Session 1:
1. `@manager` (loads your persistent manager)
2. Work as manager, delegate tasks
3. `/manager-handoff` (saves state)
4. `/clear` (clear context)

Session 2+:
1. `@manager /manager-resume` (loads manager + resumes from handoff)
2. Continue work
3. `/manager-handoff`
4. `/clear`

This workflow solves context bloat while maintaining state continuity across sessions.

---

**Next Steps:**
1. Copy the state file setup commands (shown earlier in generated prompt)
2. Run them to initialize your project state files
3. Use `@manager` to start your first manager session
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

### With Custom Agent Name
```
/create-manager-meta-prompt @PLAN.md --agent-name auth-manager
# Creates: .claude/agents/auth-manager.md
# Usage: @auth-manager
```

### Multiple Arguments
```
/create-manager-meta-prompt @PLAN.md --agent-name workflow-mgr --complex
```

## What This Does

1. Analyzes your plan (tasks, duration, infrastructure, agents, quality)
2. Scores metrics against decision criteria
3. Recommends workflow mode with full reasoning
4. Generates customized manager prompt
5. Provides state file setup commands (copy-paste ready)
6. **CREATES PERSISTENT MANAGER AGENT FILE** at `.claude/agents/{name}.md` ← AUTOMATIC
7. Outputs everything you need to start

**Key Feature:** The command automatically creates a reusable manager agent file that you can load with `@manager-name` in any session.

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
