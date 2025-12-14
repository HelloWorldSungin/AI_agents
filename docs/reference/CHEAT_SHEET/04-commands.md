# Slash Commands

Custom commands and thinking models for systematic decision-making.

**Version:** 1.5.0
**Last Updated:** 2025-12-14

---

## Overview

| Category | Count | Purpose |
|----------|-------|---------|
| Thinking Models | 12 | Mental models for systematic thinking |
| Workflow Commands | 4 | Task management and debugging |
| Manager Workflow | 5 | Multi-session manager coordination + project sync |
| Session Commands | 4 | State provider and session management |
| Autonomous Runner | 6 | CLI for autonomous task execution (NEW v1.5.0) |
| Discovery | 1 | Tool discovery across projects |

**Total Commands:** 32

**Location:** `.claude/commands/` (slash commands), `scripts/autonomous/` (CLI)

**Latest:** v1.5.0 - Autonomous Runner CLI (`python -m scripts.autonomous start/status/stop/logs/tasks/config`)

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

Commands for multi-session manager coordination with persistent agent roles and context awareness.

**Location:** `.claude/commands/`

| Command | Purpose | Usage | Location |
|---------|---------|-------|----------|
| `/create-manager-meta-prompt` | Generate manager prompt + create persistent agent file with context awareness | Before starting project | `.claude/commands/create-manager-meta-prompt.md` |
| `/manager-handoff` | Create session handoff with auto-numbering and agent tracking | End of session (or when user reports high context) | `.claude/commands/manager-handoff.md` |
| `/manager-resume` | Resume from latest handoff with manager agent verification | Start new session | `.claude/commands/manager-resume.md` |
| `/pull-ai-agents-submodule` | Sync latest AI_agents updates from submodule to project(s) | When updating from library | `.claude/commands/pull-ai-agents-submodule.md` |

**New in v1.2.0:**
- ✅ Manager agents ask user about context after each phase
- ✅ Runs `/manager-handoff` when user reports context > 70%
- ✅ Agent name tracked in handoff files for seamless resume
- ✅ Submodule sync command for keeping projects updated
- ✅ Recursive mode for batch updating multiple projects (v1.3.0)

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

### /pull-ai-agents-submodule

**Purpose:** Sync latest AI_agents library updates to your project(s)

**Prerequisites:**
- AI_agents installed as git submodule at `.ai-agents/library/`
- Project has `.claude/commands/`, `.claude/agents/`, `prompts/` directories

**Two Modes:**

#### Single Project Mode (Default)

Updates one project at a time.

```bash
# Update current directory
/pull-ai-agents-submodule

# Update specific project
/pull-ai-agents-submodule ./projects/trading-signal-ai

# Absolute path
/pull-ai-agents-submodule /Users/you/projects/my-app
```

**What Happens:**
1. Fetches latest updates from AI_agents origin/master
2. Shows commits and file changes
3. Pulls submodule update
4. Analyzes changed files in detail
5. Syncs to parent project (commands, agents, prompts, scripts)
6. Generates update report in `.ai-agents/update-reports/`

#### Recursive Mode (NEW v1.3.0)

**Batch update all projects** under a directory tree.

```bash
# Update all projects recursively
/pull-ai-agents-submodule --recursive

# Update all under ./projects/
/pull-ai-agents-submodule ./projects --recursive

# Short form
/pull-ai-agents-submodule -r
```

**What Happens:**
1. **Scans** directory tree for all `.ai-agents/library/` submodules
2. **Lists** found projects with current commits
3. **Prompts** for confirmation (Yes/Select/Cancel)
4. **Updates** each project independently
5. **Generates** per-project reports + batch summary

**Example Output:**

```
🔍 Recursive mode: Scanning for all projects

Found 4 project(s) with AI_agents submodules:

  1. projects/trading-signal-ai
     Current: master @ a1b2c3d
  2. projects/portfolio-tracker
     Current: master @ a1b2c3d (behind)
  3. projects/market-analyzer
     Current: master @ e4f5g6h (behind)
  4. legacy/old-app
     Current: master @ x7y8z9w

Proceed with batch update?
- Yes (update all)
- Select (choose specific projects)
- Cancel
```

**Selective Updates:**

```bash
# You chose: Select
Select projects to update (comma-separated numbers):
> 1,2,3

Updating: trading-signal-ai, portfolio-tracker, market-analyzer
Skipping: old-app
```

**Safety Features:**
- ✅ Non-destructive (shows changes before applying)
- ✅ Conflict detection (warns about local modifications)
- ✅ Independent updates (one failure doesn't stop others)
- ✅ Detailed reports (per-project + batch summary)
- ✅ Rollback support (can revert to previous commit)

**Use Cases:**

```bash
# Mono-repo: Update all apps at once
my-company/
├── apps/
│   ├── web/.ai-agents/library/
│   ├── mobile/.ai-agents/library/
│   └── api/.ai-agents/library/

cd my-company
/pull-ai-agents-submodule ./apps --recursive
```

**Batch Summary Report:**

After recursive update, generates comprehensive summary:
- Overall statistics (updated/skipped/failed)
- Per-project details (commits, files synced, conflicts)
- Next steps and recommendations
- Rollback instructions if needed

Saved to: `{scan_root}/.ai-agents/batch-update-{timestamp}.md`

**When to Use:**

| Scenario | Mode | Command |
|----------|------|---------|
| Single project update | Single | `/pull-ai-agents-submodule` |
| Multiple projects, careful review | Single (each) | Run command per project |
| Mono-repo, batch sync | Recursive | `/pull-ai-agents-submodule ./projects -r` |
| Mixed: critical + experimental | Mixed | Single mode for critical, recursive for experiments |

**See:** `.claude/commands/pull-ai-agents-submodule.md` for full documentation

---

## Session Commands (NEW v1.4.0)

Commands for external state provider integration and session management.

**Location:** `.claude/commands/`

| Command | Purpose | Usage |
|---------|---------|-------|
| `/start-project` | Initialize project with state provider | New projects with Linear/GitHub integration |
| `/continue-project` | Resume from external state | Resuming after context reset |
| `/pause-agent` | Pause session with state preservation | Mid-session pause |
| `/resume-agent` | Resume paused session | Continuing paused work |

### /start-project

**Purpose:** Initialize a new autonomous development project with external state tracking

**When to Use:**
- Starting a new project with Linear integration
- Setting up session continuity for the first time
- Migrating existing project to external state

**What It Does:**
1. Detects or creates state provider configuration
2. Creates META issue for project tracking
3. Initializes session state
4. Creates marker file for session detection
5. Provides status summary

**Usage:**
```bash
# Interactive initialization
/start-project

# With requirements file
/start-project @requirements.md
```

**Output:**
```
✓ Project initialized with Linear state provider
  Team: Arknode-AI
  META Issue: ARK-1
  Session: 20251212-093000

Ready to create tasks. Use /continue-project to resume after reset.
```

### /continue-project

**Purpose:** Resume an existing autonomous development project from last session

**When to Use:**
- After context reset
- Starting new work session
- Checking project status

**What It Does:**
1. Reads state from external provider (Linear/GitHub)
2. Loads META issue content
3. Gets pending/completed tasks
4. Provides comprehensive status summary
5. Suggests next actions

**Usage:**
```bash
# Resume with full context
/continue-project

# Status check only (no state modification)
/continue-project --status-only
```

**Output:**
```
## Project Status

**Session:** Resuming from 20251212-093000
**Provider:** Linear (AI-Agents project)

### Progress
- Total: 12 tasks
- Done: 8 (67%)
- In Progress: 2
- Blocked: 1

### Active Tasks
- ARK-5: Implement login form (in_progress)
- ARK-6: Add validation (in_progress)

### Blocked
- ARK-7: Waiting for API endpoint (blocked by ARK-5)

### Next Priority
Continue with ARK-5 (login form implementation)
```

### /pause-agent

**Purpose:** Pause the current agent session with state preservation

**When to Use:**
- Need to stop mid-task
- Switching to different work
- Preserving context for later

**What It Does:**
1. Saves current state to external provider
2. Records pause reason and context
3. Updates META issue with pause status
4. Provides resume instructions

**Usage:**
```bash
# Pause with automatic summary
/pause-agent

# Pause with custom summary
/pause-agent --summary "Completed login UI, need API review"
```

**Output:**
```
✓ Session paused

State saved to Linear META issue ARK-1
Resume with: /resume-agent

Summary:
- Completed: 3 tasks
- In Progress: 1 task (ARK-5)
- Pause reason: User requested pause
```

### /resume-agent

**Purpose:** Resume a paused agent session with full state restoration

**When to Use:**
- Continuing from `/pause-agent`
- Returning to paused work
- Checking pause state

**Usage:**
```bash
# Resume with full context
/resume-agent

# Status check only
/resume-agent --status-only
```

**Output:**
```
## Resuming Paused Session

**Paused:** 2025-12-12T15:30:00Z
**Duration:** 2 hours ago

### Context Restored
- Working on: ARK-5 (Implement login form)
- Files modified: src/auth/login.tsx, src/auth/styles.css
- Branch: feature/auth-login

### Next Steps
1. Complete login form validation
2. Add error handling
3. Write unit tests

Ready to continue.
```

---

## Autonomous Runner CLI - Two-Agent Pattern (NEW v1.5.0)

Implements Anthropic's recommended **two-agent pattern** for optimal context management:
1. **Initializer Agent** (Phase 1) - Analyzes spec and creates tasks
2. **Coding Agent** (Phase 2) - Executes tasks with fresh context

**Location:** `scripts/autonomous/`

**Prerequisites:**
```bash
# Verify Claude Code CLI (uses your subscription - no extra costs!)
claude --version
```

| Command | Purpose | Usage |
|---------|---------|-------|
| `init` | Initialize project from spec (Phase 1) | `python -m scripts.autonomous init --spec FILE [--project-name NAME]` |
| `start` | Start coding agent (Phase 2) | `python -m scripts.autonomous start [--config CONFIG] [--resume]` |
| `resume` | Show session recovery context | `python -m scripts.autonomous resume` |
| `status` | Show runner status | `python -m scripts.autonomous status` |
| `stop` | Stop runner gracefully | `python -m scripts.autonomous stop` |
| `logs` | View runner logs | `python -m scripts.autonomous logs [--tail N]` |
| `tasks` | Show tasks from state provider | `python -m scripts.autonomous tasks` |
| `config` | Validate configuration | `python -m scripts.autonomous config [--config CONFIG]` |

### init (Initializer Agent - Phase 1)

**Purpose:** Initialize a project from a requirements/spec file

**Usage:**
```bash
# Initialize from spec file
python -m scripts.autonomous init --spec requirements.md

# With custom project name
python -m scripts.autonomous init --spec spec.md --project-name "My App"

# Force re-initialization
python -m scripts.autonomous init --spec requirements.md --force
```

**What It Does:**
1. Reads the spec/requirements file
2. Analyzes with Claude to break down into tasks
3. Creates structured tasks in state provider (Linear/GitHub/File)
4. Creates META tracking task
5. Writes `.project_state.json` marker file

**Output:**
```
============================================================
INITIALIZER AGENT - Phase 1 of Two-Agent Pattern
============================================================

Spec file: requirements.md
Config: .ai-agents/config.yml
------------------------------------------------------------

Backend: claude-code
Model: opus
------------------------------------------------------------

Analyzing requirements...

============================================================
INITIALIZATION COMPLETE
============================================================

Project ID: proj-20251214150000
Tasks Created: 12
META Task ID: meta-001

Task Breakdown by Category:
  functional: 8
  infrastructure: 2
  testing: 2

Priority Distribution:
  HIGH: 4
  NORMAL: 6
  LOW: 2

------------------------------------------------------------
NEXT STEPS
------------------------------------------------------------

1. Review created tasks:
   python -m scripts.autonomous tasks

2. Start coding agent (Phase 2):
   python -m scripts.autonomous start

============================================================
```

### start (Coding Agent - Phase 2)

**Purpose:** Start the coding agent to execute tasks

**Usage:**
```bash
# Start with default config (.ai-agents/config.yml)
python -m scripts.autonomous start

# Start with custom config
python -m scripts.autonomous start --config my-config.yml

# Resume from previous session
python -m scripts.autonomous start --resume
```

**What It Does:**
1. Initializes state provider (Linear/GitHub/File)
2. Loads system prompt from `prompts/roles/software-developer.md`
3. Fetches tasks in priority order
4. Executes each task using Claude with FRESH context
5. Updates task status based on results
6. Respects checkpoints and cost limits

### resume

**Purpose:** Show session recovery context for continuing work

**Usage:**
```bash
python -m scripts.autonomous resume
```

**Output:**
```
============================================================
SESSION RECOVERY
============================================================

Project: My App
Project ID: proj-20251214150000
Provider: file
Total tasks: 12
Last session: 2

------------------------------------------------------------
CURRENT STATE
------------------------------------------------------------

Todo: 6
In Progress: 1
Done: 4
Blocked: 1
Completion: 33.3%

------------------------------------------------------------
IN PROGRESS TASKS
------------------------------------------------------------

  [task-5] Implement user dashboard
    Build the main dashboard component with...

------------------------------------------------------------
NEXT STEPS
------------------------------------------------------------

1. Continue coding with:
   python -m scripts.autonomous start --resume

2. Or view all tasks:
   python -m scripts.autonomous tasks

============================================================
```

**Output:**
```
Starting autonomous runner with config: .ai-agents/config.yml
Resume mode: False
--------------------------------------------------
Model: claude-opus-4-20250514
Execution mode: autonomous
Max tasks per session: 10
Cost limit: $10.0
--------------------------------------------------
Starting task: ARK-5 - Implement login form
...
```

### status

**Purpose:** Show current runner status and progress

**Usage:**
```bash
python -m scripts.autonomous status
```

**Output:**
```
==================================================
AUTONOMOUS RUNNER STATUS
==================================================

Runner State: RUNNING
Session ID: 20251214-103000
Tasks Completed: 3
Total Cost: $1.25
Current Turn: 47

--------------------------------------------------
PROGRESS
--------------------------------------------------

Total Tasks: 12
Completed: 8 (67%)
In Progress: 2
Blocked: 1
Session Tasks: 3
Tasks/Hour: 4.2
Regression: passing

--------------------------------------------------
RECENT EVENTS
--------------------------------------------------
  2025-12-14T10:45:00 [task_completed] ARK-5
  2025-12-14T10:30:00 [task_started] ARK-5
  2025-12-14T10:28:00 [session_start]

==================================================
```

### stop

**Purpose:** Stop the runner gracefully

**Usage:**
```bash
python -m scripts.autonomous stop
```

**What It Does:**
- Sets runner state to STOPPED
- Runner stops at next checkpoint
- State preserved for resume

### logs

**Purpose:** View runner execution logs

**Usage:**
```bash
# Show last 50 lines (default)
python -m scripts.autonomous logs

# Show last 100 lines
python -m scripts.autonomous logs --tail 100
```

**Log Location:** `.ai-agents/logs/autonomous.log`

### tasks

**Purpose:** Show tasks from configured state provider

**Usage:**
```bash
python -m scripts.autonomous tasks
```

**Output:**
```
============================================================
TASKS FROM STATE PROVIDER
============================================================

TODO (3)
----------------------------------------
  [ARK-8] Add password validation
    Priority: HIGH
  [ARK-9] Implement logout
    Priority: NORMAL
  [ARK-10] Add session timeout
    Priority: LOW

IN_PROGRESS (1)
----------------------------------------
  [ARK-7] Implement password reset
    Priority: HIGH

DONE (4)
----------------------------------------
  [ARK-5] Implement login form
  [ARK-6] Add form validation
  ... and 2 more

============================================================
```

### config

**Purpose:** Validate runner configuration

**Usage:**
```bash
# Validate default config
python -m scripts.autonomous config

# Validate specific config
python -m scripts.autonomous config --config my-config.yml
```

**Output:**
```
==================================================
RUNNER CONFIGURATION
==================================================

Config file: .ai-agents/config.yml

Model: claude-opus-4-20250514
Max tokens: 8192
API key env: ANTHROPIC_API_KEY
System prompt: prompts/roles/software-developer.md

Execution mode: autonomous
Max turns per task: 50
Max tasks per session: 10
Pause between tasks: 5s

Rate limit: 50 RPM
Cost limit: $10.0

--------------------------------------------------
VALIDATION
--------------------------------------------------

Configuration valid!

==================================================
```

### Configuration Example

```yaml
# .ai-agents/config.yml
state_provider:
  type: "linear"
  api_key_env: "LINEAR_API_KEY"
  project_name: "My Project"

autonomous:
  backend: "claude-code"  # Uses subscription - no extra API costs!
  model: "opus"
  max_tokens: 8192
  system_prompt_path: "prompts/roles/software-developer.md"
  max_turns_per_task: 50
  max_tasks_per_session: 10
  rate_limit_rpm: 50

execution:
  mode: "autonomous"
  checkpoints:
    turn_interval: 25
    on_regression_failure: true
    on_blocker: true
```

**Backends:**
- `claude-code` (default): Uses Claude Code CLI with your subscription - no extra costs!
- `anthropic-sdk`: Uses Anthropic API directly - requires API key and incurs usage costs

**See:** `scripts/autonomous/README.md` for complete documentation

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
