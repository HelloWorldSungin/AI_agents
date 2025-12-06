# Slash Commands

Custom commands and thinking models for systematic decision-making.

---

## Overview

| Category | Count | Purpose |
|----------|-------|---------|
| Thinking Models | 12 | Mental models for systematic thinking |
| Workflow Commands | 4 | Task management and debugging |
| Discovery | 1 | Tool discovery across projects |

**Total Commands:** 17

**Location:** `.claude/commands/`

---

## Thinking Models

12 mental models for systematic thinking and decision-making.

**Location:** `.claude/commands/consider/`

### Available Models

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/consider:first-principles` | Break down to fundamentals and rebuild from base truths | Complex problems with assumptions |
| `/consider:5-whys` | Root cause analysis - ask "why" 5 times | Debugging, finding root causes |
| `/consider:second-order` | Examine consequences of consequences | Long-term planning, impact analysis |
| `/consider:inversion` | Solve by considering the opposite | Risk analysis, failure prevention |
| `/consider:occams-razor` | Prefer the simplest explanation | Debugging, architecture decisions |
| `/consider:pareto` | Find the vital 20% that drives 80% of results | Prioritization, optimization |
| `/consider:eisenhower-matrix` | Prioritize by urgent/important | Task prioritization, time management |
| `/consider:opportunity-cost` | What you give up by choosing this | Trade-off decisions, resource allocation |
| `/consider:via-negativa` | Improve by removing rather than adding | Simplification, technical debt |
| `/consider:swot` | Analyze strengths, weaknesses, opportunities, threats | Strategic planning, risk assessment |
| `/consider:one-thing` | Identify the single most important action | Focus, priority setting |
| `/consider:10-10-10` | Evaluate decisions at 10min, 10months, 10years | Long-term decisions, career choices |

### Usage Examples

#### Problem Solving
```bash
# Breaking down complex problem
/consider:first-principles "How should we architect this microservices system?"

# Finding root cause
/consider:5-whys "Why are API response times slow?"

# Understanding consequences
/consider:second-order "What happens if we add caching?"
```

#### Decision Making
```bash
# Choosing between options
/consider:opportunity-cost "Should we build in-house or use SaaS?"

# Simplifying architecture
/consider:occams-razor "What's the simplest solution to this authentication problem?"

# Risk prevention
/consider:inversion "What would make this deployment fail?"
```

#### Prioritization
```bash
# Finding high-impact work
/consider:pareto "Which features drive 80% of user value?"

# Prioritizing tasks
/consider:eisenhower-matrix "Review my current task list"

# Finding the one thing
/consider:one-thing "What's the single highest-leverage action for this sprint?"
```

#### Strategic Planning
```bash
# Analyzing situation
/consider:swot "Our current authentication system"

# Evaluating long-term impact
/consider:10-10-10 "Should we migrate to microservices?"

# Simplifying by removing
/consider:via-negativa "How can we improve this codebase by removing code?"
```

### Thinking Model Best Practices

**Do's:**
- Use at decision points
- Combine multiple models (e.g., first-principles + inversion)
- Apply early in planning phase
- Use for complex, non-obvious problems

**Don'ts:**
- Don't use for simple, obvious decisions
- Don't overthink straightforward tasks
- Don't apply too many models at once

---

## Workflow Commands

Commands for task management, debugging, and handoffs.

**Location:** `.claude/commands/`

| Command | Purpose | Usage | Location |
|---------|---------|-------|----------|
| `/whats-next` | Create comprehensive context handoff document for continuing work in fresh session | At session end, context limit | `.claude/commands/whats-next.md` |
| `/debug` | Apply expert debugging methodology (loads `debug-like-expert` skill) | When troubleshooting bugs | `.claude/commands/debug.md` |
| `/add-to-todos` | Capture tasks without derailing current focus | During work, new task comes up | `.claude/commands/add-to-todos.md` |
| `/check-todos` | Review pending tasks and priorities | Start of session, checking status | `.claude/commands/check-todos.md` |

---

## Manager Workflow Commands

Commands for multi-session manager coordination with persistent agent roles.

**Location:** `.claude/commands/`

| Command | Purpose | Usage | Location |
|---------|---------|-------|----------|
| `/create-sub-task` | Create and spawn sub-task agent with standardized prompt | Manager delegation | `.claude/commands/create-sub-task.md` |
| `/create-manager-meta-prompt` | Generate manager prompt and create persistent agent file | Before complex projects | `.claude/commands/create-manager-meta-prompt.md` |
| `/manager-handoff` | Create session handoff with auto-numbering | End of manager session | `.claude/commands/manager-handoff.md` |
| `/manager-resume` | Resume from latest handoff with full context | Start new manager session | `.claude/commands/manager-resume.md` |

### /whats-next

**Purpose:** Create handoff document for session continuity

**When to Use:**
- Approaching context limit (75%+)
- End of work session
- Need to pause and resume later
- Switching between projects

**What it Creates:**
- Summary of work completed
- Outstanding work remaining
- Critical context to preserve
- Attempted approaches (successes and failures)
- Current state snapshot

**Output:** `whats-next.md` in project root

**Example:**
```bash
# At 75% context usage
/whats-next

# Claude generates comprehensive handoff document
# Resume next session by reading whats-next.md
```

### /debug

**Purpose:** Apply expert debugging methodology

**When to Use:**
- Complex bugs with unclear root cause
- Standard troubleshooting fails
- Need systematic investigation
- Multiple potential causes

**What it Does:**
- Loads `debug-like-expert` skill
- Applies methodical investigation protocol
- Evidence gathering
- Hypothesis testing
- Rigorous verification

**Example:**
```bash
/debug "Users can't log in after password reset"

# Claude applies systematic debugging:
# 1. Gather evidence (logs, reproduction steps)
# 2. Form hypotheses
# 3. Test each hypothesis
# 4. Verify root cause
# 5. Implement fix
```

### /add-to-todos

**Purpose:** Capture tasks without context switching

**When to Use:**
- Working on task A, task B comes up
- Code review reveals additional work
- During implementation, discover tech debt
- Planning future work

**What it Does:**
- Adds task to TO-DOS.md
- Preserves context from conversation
- Doesn't derail current focus
- Can be reviewed later with /check-todos

**Example:**
```bash
# While implementing auth
/add-to-todos "Add rate limiting to login endpoint"

# Task captured, continue with auth implementation
```

**Optional Parameter:**
```bash
# Explicit description
/add-to-todos <todo-description>

# Infers from conversation if omitted
/add-to-todos
```

### /check-todos

**Purpose:** Review pending tasks and select next work

**When to Use:**
- Start of work session
- Finished current task
- Planning next sprint
- Checking backlog

**What it Does:**
- Lists all todos from TO-DOS.md
- Shows priorities
- Helps select next task
- Updates status

**Example:**
```bash
/check-todos

# Claude shows:
# 1. [ ] Add rate limiting to login endpoint (Priority: High)
# 2. [ ] Refactor database connection pooling (Priority: Medium)
# 3. [ ] Update API documentation (Priority: Low)
#
# Which would you like to work on?
```

---

### /create-sub-task

**Purpose:** Create and spawn a sub-task agent with standardized prompt

**When to Use:**
- Manager agents delegating work to specialized agents
- Need consistent prompt structure across tasks
- Want automatic state file reading instructions
- Tracking tasks with IDs

**Usage:**
```bash
/create-sub-task "task description" [--role "Role"] [--phase "Phase X"] [--requirements "..."] [--preview]
```

**Arguments:**
- `task` (required): What the agent should accomplish
- `--role` (optional): Agent role (Backend Developer, QA Tester, IT Specialist, Frontend Developer, etc.)
- `--phase` (optional): Which phase this task belongs to
- `--requirements` (optional): Specific requirements or steps (multiline supported)
- `--preview` (optional): Show generated prompt before spawning

**What It Does:**
1. Generates standardized agent prompt with:
   - Role setup
   - Task objective
   - Auto state file reading instructions
   - Requirements (if provided)
   - Update protocol
2. Spawns agent via Task tool (or shows preview)

**Examples:**
```bash
# Simple task
/create-sub-task "Run all unit tests" --role "QA Tester"

# Detailed with requirements
/create-sub-task "Validate infrastructure" --role "IT Specialist" --requirements "Check all 8 infrastructure points from it-specialist-agent.md"

# Preview before spawning
/create-sub-task "Complex migration" --role "Backend Developer" --preview

# With phase context
/create-sub-task "Implement login form" --role "Frontend Developer" --phase "Phase 2: Authentication UI"
```

**Output:**
```
✓ Agent spawned successfully

Task ID: TASK-001
Role: QA Tester
Agent will report back when complete.

Monitor progress in: .ai-agents/state/team-communication.json (agent_updates section)
```

---

### /create-manager-meta-prompt

**Purpose:** Generate manager agent prompt from PLAN.md and create persistent agent file

**When to Use:**
- Starting complex multi-agent projects
- Need persistent manager role across sessions
- Want optimized workflow mode (Simple/Complex/Automated)
- Creating reusable manager agents

**Usage:**
```bash
/create-manager-meta-prompt @path/to/PLAN.md [--agent-name custom-name]
/create-manager-meta-prompt "project description" [--agent-name custom-name]
```

**Arguments:**
- Plan file path OR project description (required)
- `--agent-name` (optional): Custom name for agent file (default: project-manager)

**What It Does:**
1. Analyzes plan file or description
2. Determines workflow mode (Simple vs Complex vs Automated)
3. Generates comprehensive manager prompt
4. **Creates agent file** at `.claude/agents/{name}.md` with YAML frontmatter
5. Shows usage instructions for multi-session workflow

**Examples:**
```bash
# From plan file (default naming)
/create-manager-meta-prompt @.planning/PLAN-auth.md
# Creates: .claude/agents/project-manager.md

# From plan file (custom naming)
/create-manager-meta-prompt @.planning/PLAN-api.md --agent-name api-manager
# Creates: .claude/agents/api-manager.md

# From description
/create-manager-meta-prompt "Build user authentication system with JWT"
```

**Multi-Session Usage:**
```bash
# Session 1: Generate manager
/create-manager-meta-prompt @PLAN.md

# Use manager in fresh context
@manager

# Work, then handoff
/manager-handoff

# Session 2: Resume
@manager /manager-resume
```

**Output:**
```
---

## Manager Agent File Created ✓

**File:** `.claude/agents/project-manager.md`

### How to Use This Manager

**In a fresh context:**
```bash
@manager  # if using default name (project-manager)
# or
@api-manager  # if you used --agent-name
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
```

---

### /manager-handoff

**Purpose:** Create manager session handoff with auto-numbering and resume instructions

**When to Use:**
- End of manager work session
- Before clearing context
- Approaching context limits
- After completing major milestones

**Usage:**
```bash
/manager-handoff
```

**Arguments:** None

**What It Does:**
1. Auto-discovers existing handoffs and increments session number
2. Reads all 3 state files (team-communication, session-progress, feature-tracking)
3. Creates comprehensive handoff at `.ai-agents/handoffs/session-XXX.md`
4. Includes Quick Resume section with `/manager-resume` command
5. Updates session-progress.json with handoff reference

**Handoff Includes:**
- Session summary (ID, timestamps, duration)
- What was accomplished
- Current status (phase, tasks, blockers)
- Decisions made
- State files snapshot
- Next session priority
- Resume instructions

**Examples:**
```bash
# First handoff (creates session-001.md)
/manager-handoff

# Second handoff (auto-creates session-002.md)
/manager-handoff

# Third handoff (auto-creates session-003.md)
/manager-handoff
```

**Output:**
```
Manager handoff created:
- Handoff: .ai-agents/handoffs/session-001.md
- Communication file: .ai-agents/state/team-communication.json (~8,500 tokens)
- Session progress: .ai-agents/state/session-progress.json
- Feature tracking: .ai-agents/state/feature-tracking.json
- README.md updated with session progress

To resume: Start new manager session and run:
  @manager /manager-resume
```

---

### /manager-resume

**Purpose:** Resume manager session from latest handoff with full context

**When to Use:**
- Starting new manager session after handoff
- Resuming work after context clear
- Getting quick status update mid-project

**Usage:**
```bash
/manager-resume
```

**Arguments:** None

**What It Does:**
1. Auto-discovers latest handoff file (session-XXX.md)
2. Reads all 3 state files
3. Generates comprehensive status summary with:
   - Last session summary
   - Completed work
   - Current phase and progress
   - Recent agent updates (last 3-5)
   - Active/blocked tasks
   - Pending questions
   - Verification checklist progress
   - Next recommended steps

**Example:**
```bash
# Resume from latest handoff
@manager /manager-resume

# Shows comprehensive summary, then:
# "Ready to continue? Options:
#  - Continue with next phase
#  - Review specific agent updates
#  - Address blocked tasks
#  - Answer pending questions"
```

**Output:**
```markdown
# Resuming Manager Session

## Last Session Summary

**Session:** 001
**Ended:** 2025-12-06T12:15:00Z

### Completed

✓ INFRA-001: Infrastructure Planning & Analysis
✓ TASK-001: /create-sub-task Command Implementation
✓ TASK-002: /create-manager-meta-prompt Enhancement
✓ TASK-003: /manager-handoff Enhancement

### Current Status

**Phase:** Phase 5: Documentation Updates
**Progress:** 4 of 6 phases complete

## Recent Agent Updates

Most recent:
- **backend-dev-TASK-004** (2025-12-06T12:15:00Z): Implemented /manager-resume command
- **backend-dev-TASK-003** (2025-12-06T11:55:00Z): Enhanced /manager-handoff
- **backend-dev-TASK-002** (2025-12-06T03:15:00Z): Enhanced /create-manager-meta-prompt

## Current State

### Active Tasks

⏳ Active:
- TASK-005: Update CHEAT_SHEET documentation (assigned to technical-writer)

### Blocked Tasks

✅ No blockers

### Questions Pending

✅ No pending questions

## Next Priority

Continue with Phase 5: Documentation Updates

**Recommended Next Steps:**
1. Complete TASK-005 documentation updates
2. Move to Phase 6: Integration Testing & Review
3. Verify all workflows with test cases

---

**Ready to continue?**

Options:
- Continue with next phase
- Review specific agent updates
- Address blocked tasks (if any)
- Answer pending questions (if any)
```

**Error Handling:**
- No handoffs: Shows message to create one with `/manager-handoff`
- Missing state files: Shows warning but continues with available data

---

## Discovery Command

**New in v1.3.0** - Tool discovery across projects

| Command | Purpose | Usage |
|---------|---------|-------|
| `/ai-tools` | Discover available tools from AI_agents library | In any project with tool selector installed |

### /ai-tools

**Purpose:** Discover AI_agents tools from other projects

**Prerequisites:** Tool selector installed via `setup-commands.py`

**What it Shows:**
- Available slash commands
- Thinking models (`/consider:*`)
- Workflow commands
- Skills and subagents
- Quick usage examples

**Example:**
```bash
# From any project
/ai-tools

# Claude shows:
# Available Tools from AI_agents Library:
#
# Thinking Models:
# - /consider:first-principles
# - /consider:5-whys
# ... etc
#
# Workflow Commands:
# - /create-plan
# - /debug
# ... etc
```

**See:** [06-scripts-tools.md](06-scripts-tools.md#tool-selector) for setup instructions

---

## Command Best Practices

### General Guidelines

1. **Use thinking models early** - Apply during planning and design
2. **Combine models** - Use multiple perspectives for complex decisions
3. **Debug systematically** - Use /debug for non-obvious bugs
4. **Maintain handoffs** - Use /whats-next at 75% context
5. **Track todos** - Use /add-to-todos to capture work without switching

### Token Efficiency

**Thinking Models:**
- ~60 tokens per invocation (~1.5% overhead)
- Use selectively for complex decisions
- Don't use for simple, obvious choices

**Workflow Commands:**
- Minimal token overhead (command names only)
- /debug loads skill dynamically (~4K tokens)
- /whats-next creates file, no ongoing cost

### When NOT to Use Commands

**Skip thinking models for:**
- Simple, straightforward decisions
- Obvious technical choices
- Implementation details
- Routine development tasks

**Skip /debug for:**
- Simple bugs with obvious cause
- Typos and syntax errors
- Clear error messages with solutions

**Skip /whats-next if:**
- Context usage below 50%
- Session just started
- No meaningful work to preserve

---

## Creating Custom Commands

Custom slash commands can be created in `.claude/commands/`

**Basic Structure:**
```markdown
---
description: "Brief description of command"
args:
  - name: "argument_name"
    description: "What this argument does"
    required: true
---

# Command implementation
Your prompt content here...
```

**See:** `taches-cc-resources` for advanced command patterns

---

## See Also

- **Tool Selector Setup:** [06-scripts-tools.md](06-scripts-tools.md#tool-selector)
- **Debugging Guide:** `docs/guides/E2E_TESTING.md`
- **Skills Library:** [03-skills.md](03-skills.md)

---

[← Back to Index](index.md) | [Previous: Skills](03-skills.md) | [Next: Workflows →](05-workflows.md)
