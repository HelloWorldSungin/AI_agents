# Workflows & Coordination

Workflow modes and coordination models for multi-agent development.

---

## Workflow Modes

Two primary modes for organizing agent workflows.

### Simple Mode (90% of projects)

```
Manager → Task Agents → Integration Agent
```

**Use for:**
- Established projects with existing infrastructure
- 1-3 agents
- Clear requirements
- Straightforward features
- 1-3 day tasks
- You want speed over rigor

**State Files:**
- `team-communication.json` only

**Example Flow:**
1. Manager breaks down task into subtasks
2. Delegates to specialized agents (frontend, backend, QA)
3. Agents work independently on branches
4. Integration agent merges work when complete
5. Manager verifies and closes task

**Example Team:**
```
Manager
  ↓
  ├→ Frontend Developer (AUTH-001: Login UI)
  ├→ Backend Developer (AUTH-002: Login API)
  └→ QA Tester (AUTH-003: Login Tests)
  ↓
Integration Agent (merges all branches)
```

**Benefits:**
- Fast setup
- Minimal overhead
- Works for most features
- Easy to understand

---

### Complex Mode (10% of projects)

```
Manager → IT Specialist → Task Agents → Senior Engineer
```

**Use for:**
- New projects needing infrastructure setup
- 5+ agents
- Complex architecture requiring validation
- Code review required
- First features requiring infrastructure
- Multi-day/multi-session work
- Quality gates needed
- Session continuity desired

**State Files:**
- `team-communication.json` (real-time)
- `session-progress.json` (cross-session)
- `feature-tracking.json` (verification)

**Example Flow:**
1. Manager coordinates overall strategy
2. IT Specialist validates infrastructure (8 checks)
3. Task agents work on features in parallel
4. QA Tester writes E2E tests (mandatory)
5. Senior Engineer reviews code
6. Senior Engineer blocks merge if E2E tests missing
7. Senior Engineer integrates after approval
8. Manager updates feature-tracking.json
9. Manager updates session-progress.json for next session

**Example Team:**
```
Manager
  ↓
IT Specialist (validates: DB, env, tests, build)
  ↓
  ├→ Backend Developer (AUTH-001: Registration API)
  ├→ Backend Developer (AUTH-002: Login API)
  ├→ Frontend Developer (AUTH-003: Auth Forms)
  └→ QA Tester (AUTH-004: E2E Tests) ← MANDATORY
  ↓
Senior Engineer (reviews, enforces E2E tests, merges)
  ↓
Manager (updates feature-tracking.json, session-progress.json)
```

**Benefits:**
- Infrastructure validated before work
- Code quality enforced
- E2E testing mandatory
- Session continuity (50% faster resumption)
- Progress metrics tracked
- Blockers documented

**Required Features:**
- All 5 completion criteria must be met (see [01-state-files.md](01-state-files.md#feature-completion-criteria))
- E2E tests mandatory (Senior Engineer blocks without them)
- Code review required
- Feature tracking enforced

---

### Optional: With Scrum Master

Add project tracking and visibility to either mode:

```
Manager → [Scrum Master Setup] → IT Specialist → Task Agents → Senior Engineer
             ↓
    [AppFlowy Tracking + Daily Summaries]
```

**Use when:**
- External stakeholders need visibility
- Sprint velocity tracking required
- Daily standup summaries needed
- AppFlowy server available

**Scrum Master Responsibilities:**
- Create AppFlowy workspace
- Create tasks from feature list
- Update task status from team-communication.json
- Generate daily summaries
- Track sprint velocity
- Report blockers to stakeholders

**See:** `prompts/roles/scrum-master.md` for details

---

## Coordination Models

Three ways to implement multi-agent coordination.

### 1. Human-Coordinated (Practical Today)

**What:** You manually run agents in sequence and relay information.

**Best for:**
- 90% of users
- Learning multi-agent patterns
- Small teams (1-3 agents)
- Tools like Claude Code (one session at a time)
- When you want full control
- Quick iterations

**How it Works:**
1. Manager writes instructions to `team-communication.json`
2. You read the file
3. You invoke appropriate agent
4. Agent reads file, does work, writes updates
5. You relay updates back to Manager
6. Repeat until complete

**Communication:** Agents write to `.ai-agents/state/team-communication.json`, you relay

**Pros:**
- Simple to understand
- Full control at each step
- Easy to debug
- No API costs
- Works with any tool

**Cons:**
- Sequential execution (not parallel)
- Manual relay required
- Can be tedious for large teams

**Guide:** `PRACTICAL_WORKFLOW_GUIDE.md`

---

### 2. Task Tool Delegation (Recommended - NEW v1.1.0)

**What:** Manager spawns agents using Claude Code's Task tool. Each agent gets fresh context.

**Best for:**
- Most users (best balance)
- Complex projects (5+ agents)
- Infrastructure setup and code review needed
- Keeping Manager context lean (15-25%)
- Zero API costs
- When you want automation but keep control

**How it Works:**
1. Manager creates execution plan
2. Manager spawns agents via Task tool
3. Each agent gets fresh context (no Manager bloat)
4. Agents complete tasks autonomously
5. Agents report back to Manager
6. Manager coordinates next steps

**Communication:** Automatic via Task tool

**Pros:**
- Fresh context per agent (no bloat)
- Manager stays lean
- Zero API costs
- Automatic coordination
- Still human oversight
- Works in Claude Code

**Cons:**
- Sequential execution (not parallel)
- Requires Claude Code or API access
- Manager must orchestrate carefully

**Guide:** `prompts/manager-task-delegation.md`

**Example:**
```markdown
# Manager spawns IT Specialist
<task>
  <agent>it-specialist</agent>
  <task-id>SETUP-001</task-id>
  <description>Validate infrastructure and generate init.sh</description>
</task>

# IT Specialist gets fresh context, completes work, reports back
# Manager then spawns next agents based on results
```

---

### 3. Fully Automated (Advanced)

**What:** Programmatic orchestration via LLM APIs with message queue.

**Best for:**
- Advanced users with programming experience
- Large-scale projects (5+ agents)
- CI/CD automation
- True parallel execution
- Production deployments
- When you want full automation

**How it Works:**
1. Orchestrator script reads config
2. Spawns agents via API
3. Agents communicate via message queue
4. True parallel execution
5. Orchestrator monitors progress
6. Handles failures and retries

**Communication:** Direct agent-to-agent via message queue

**Pros:**
- True parallel execution
- Scales to many agents
- Fully automated
- CI/CD integration
- Production-ready

**Cons:**
- Complex setup
- Requires programming
- API costs
- Less human control
- Harder to debug

**Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`

**Scripts:**
- `simple_orchestrator.py` - Basic orchestration
- `file_based_orchestrator.py` - File-based coordination
- `programmatic_orchestrator.py` - Programmatic tool calling

---

### 4. Autonomous Runner - Two-Agent Pattern (NEW v1.5.0)

**What:** Implements Anthropic's recommended two-agent pattern for optimal context management.

**Best for:**
- Fully autonomous task execution
- Projects with clear requirements/specs
- Integration with issue trackers (Linear, GitHub)
- Multi-session projects with context recovery
- CI/CD automation

**How it Works:**
```
┌─────────────────────────────────────────────────────────────┐
│                    INITIALIZER AGENT                         │
│  (Phase 1 - `python -m scripts.autonomous init`)            │
│                                                             │
│  1. Read spec file → 2. Analyze with Claude                 │
│  3. Create tasks in provider → 4. Write .project_state.json │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CODING AGENT(S)                           │
│  (Phase 2 - `python -m scripts.autonomous start`)           │
│                                                             │
│  1. Get TODO task → 2. Implement with FRESH context         │
│  3. Test/verify → 4. Update status → 5. Next task           │
└─────────────────────────────────────────────────────────────┘
```

**Communication:** External state provider (Linear, GitHub, or File)

**Pros:**
- Optimal context management (each agent starts fresh)
- Fully autonomous (no human relay required)
- Session continuity via state provider
- Uses Claude Code subscription (no extra API costs)
- Resume capability across sessions

**Cons:**
- Requires clear spec/requirements document
- Less human oversight during execution
- Requires state provider setup

**Quick Start:**
```bash
# Phase 1: Initialize project from spec
python -m scripts.autonomous init --spec requirements.md

# Phase 2: Run coding agent
python -m scripts.autonomous start

# Resume later
python -m scripts.autonomous resume
python -m scripts.autonomous start --resume
```

**Guide:** `scripts/autonomous/README.md`

**See:** [06-scripts-tools.md](06-scripts-tools.md#autonomous-runner-two-agent-pattern) for complete documentation

---

## Multi-Session Manager Workflow

For projects spanning multiple sessions, use this workflow to maintain state continuity while managing context limits.

### Overview

**Problem:** Long projects exhaust Claude's context window
**Solution:** Session handoffs with persistent manager role and automatic context monitoring

**Key Components:**
- Persistent manager agent file (`.claude/agents/project-manager.md`)
- Session handoffs (`.ai-agents/handoffs/session-XXX.md`)
- State files (team-communication, session-progress, feature-tracking)
- Context monitoring (manager asks user after each phase)
- Resume command (`/manager-resume`)

**New Features (v1.2.0):**
- ✅ Manager asks user about context usage after each phase
- ✅ Auto-runs `/manager-handoff` when user reports > 70%
- ✅ Manager agent name tracked in handoff files
- ✅ Seamless resume with `@manager-name /manager-resume`

### Workflow Pattern

#### Session 1: Initial Setup

```bash
# 1. Create project plan
/create-plan "Build authentication system with JWT, OAuth, and MFA"

# 2. Generate manager agent (creates persistent agent file)
/create-manager-meta-prompt @.planning/PLAN-auth.md
# Output: Created .claude/agents/project-manager.md

# 3. Set up state files (run commands from output)
mkdir -p .ai-agents/state
# ... initialize JSON files ...

# 4. Load manager and work
@project-manager

# Manager delegates tasks via Task tool
# Agents complete work, update state files

# 5. After each phase/task, manager asks about context
# Manager: "📊 Phase complete! How full is your context window?"
# You: "About 45%"
# Manager: "✅ Context window healthy. Continue with next phase?"
# You: "Yes"

# [Continue working...]

# 6. User reports context > 70%
# Manager: "📊 Phase complete! How full is your context window?"
# You: "Around 72%"
# Manager: "⚠️ Context window is getting full. Creating handoff now..."
# Manager runs: /manager-handoff
# Manager: "✅ Handoff created successfully.
#          To continue with fresh context:
#          1. Run: /clear
#          2. Resume: @project-manager /manager-resume"

# 7. Clear context for next session
/clear
```

#### Session 2+: Resume and Continue

```bash
# 1. Load manager and resume from latest handoff
@project-manager /manager-resume

# Shows comprehensive summary:
# - Manager Agent: @project-manager ✓
# - Last session: session-001 (ended 2025-12-06T18:00:00Z)
# - Completed: TASK-001, TASK-002, TASK-003
# - Current phase: Phase 4
# - Active tasks: TASK-004
# - Next: Continue with Phase 4

# 2. Continue delegating work
# Manager picks up where it left off
# Spawns agents via Task tool

# 3. Manager asks about context after each phase
# Manager: "📊 Phase complete! How full is your context window?"
# You: "About 55%"
# Manager: "✅ Continue with next phase?"
# You: "Yes"

# [Work continues...]

# 4. User reports context > 70%, manager creates handoff
# Manager: "📊 Phase complete! How full is your context window?"
# You: "Around 74%"
# Manager: "⚠️ Creating handoff now..."
# Manager runs /manager-handoff
# Output: Created .ai-agents/handoffs/session-002.md

# 5. Clear context
/clear
```

#### Session N: Repeat Pattern

Same pattern repeats for any number of sessions:
1. `@{manager-name} /manager-resume`
2. Work (delegate, monitor, coordinate)
3. Manager asks about context after each phase
4. Manager runs `/manager-handoff` when you report > 70%
5. You run `/clear` and resume in next session

### Benefits

✅ **Solves context bloat**: Clear context between sessions
✅ **Persistent manager role**: `@manager-name` loads same agent every time
✅ **State continuity**: State files preserve all project information
✅ **Clear handoff docs**: Each handoff documents progress
✅ **Auto-numbering**: Session files auto-increment (001, 002, 003...)
✅ **Quick resume**: `/manager-resume` provides instant status update
✅ **Context monitoring**: Manager asks user about context after each phase
✅ **Handoff workflow**: Manager runs `/manager-handoff` when you report > 70%
✅ **Agent tracking**: Handoff remembers which manager to resume

### State Files

**team-communication.json**:
- Manager instructions and active tasks
- Agent updates and status
- Integration requests
- Questions for manager

**session-progress.json**:
- Current phase and session ID
- Completed phases and tasks
- Blocked tasks
- Decisions made
- Manager agent name (`@project-manager`)
- Last handoff reference

**feature-tracking.json**:
- Feature verification checklist
- Integration status
- Review status

### When to Use

**Use multi-session workflow when:**
- Project will take multiple days
- Context usage approaching 60-70% (manager will auto-detect)
- Natural breaking points (phase completion)
- Multiple complex features in sequence

**Don't use when:**
- Single feature, one session
- Quick fixes or small changes
- Context usage under 40%

**Note:** Manager automatically monitors context and will recommend handoff at 70% usage

### Best Practices

1. **Trust context monitoring**: Manager checks usage after each phase automatically
2. **Follow handoff recommendations**: When manager says > 70%, do the handoff
3. **Keep state files updated**: Agents update after each task
4. **Use meaningful agent names**: `--agent-name auth-manager` for clarity
5. **Review resume summary**: Check active/blocked tasks before continuing
6. **Commit state files**: Include in git commits for history
7. **Let manager auto-handoff**: Manager runs `/manager-handoff` when needed

### Troubleshooting

**Problem**: `/manager-resume` shows "No handoff files found"
**Solution**: Run `/manager-handoff` to create first handoff

**Problem**: State files show stale data
**Solution**: Agents should update team-communication.json after completing tasks

**Problem**: Context still filling up despite monitoring
**Solution**: Manager should be asking user about context after each phase. If not, remind manager to ask "How full is your context window?"

**Problem**: Manager agent name not showing in resume
**Solution**: Ensure using updated `/manager-handoff` command (v1.2.0+). Older handoffs won't have agent name tracking

---

## Mono-Repo Project Sync Workflow

**New in v1.3.0** - For projects using AI_agents as a git submodule across multiple workspaces.

### Overview

**Problem:** Multiple projects using AI_agents library need to stay updated
**Solution:** Recursive batch updates with selective control

**Use Cases:**
- Mono-repo with multiple apps/services
- Multiple client projects using same agent library
- Development + staging + production environments
- Team with multiple projects per developer

### Workflow Pattern

#### Setup: Install AI_agents as Submodule

For each project:

```bash
cd /path/to/project
git submodule add https://github.com/HelloWorldSungin/AI_agents.git .ai-agents/library
git submodule update --init --recursive

# Set up symlinks for Claude Code discovery
mkdir -p .claude/skills
cd .claude/skills
ln -s ../../.ai-agents/library/external/taches-cc-resources/skills/* .
```

#### Scenario 1: Single Project Update

Update one project with careful review:

```bash
cd /path/to/critical-production-app
/pull-ai-agents-submodule

# Claude shows:
# - New commits available
# - Files changed (commands, agents, prompts)
# - Detailed analysis of each change
#
# Proceed with update? Yes/Show details/Cancel
```

**Workflow:**
1. Review changes carefully
2. Pull update
3. Sync to parent project
4. Review update report
5. Test changes
6. Commit to project repo

**When to use:**
- Production/critical apps
- Need detailed change review
- Want fine-grained control

#### Scenario 2: Batch Update (Recursive Mode)

Update all projects under a directory:

```bash
# Mono-repo structure
my-company/
├── apps/
│   ├── web/.ai-agents/library/
│   ├── mobile/.ai-agents/library/
│   ├── api/.ai-agents/library/
│   └── admin/.ai-agents/library/

cd my-company
/pull-ai-agents-submodule ./apps --recursive
```

**Output:**

```
🔍 Recursive mode: Scanning for all projects under apps/

Found 4 project(s) with AI_agents submodules:

  1. apps/web
     Current: master @ a1b2c3d (behind 3 commits)
  2. apps/mobile
     Current: master @ a1b2c3d (behind 3 commits)
  3. apps/api
     Current: master @ e4f5g6h (already up to date)
  4. apps/admin
     Current: master @ x7y8z9w (behind 1 commit)

─────────────────────────────────────────

Proceed with batch update?
- Yes (update all 4 projects)
- Select (choose specific projects)
- Cancel
```

**You choose:** Select → `1,2,4`

**Processing:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Project 1/3: apps/web
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fetching updates...
New commits: a1b2c3d → f9e8d7c
Files changed: 5
- Commands: 2 files
- Prompts: 1 file
- Docs: 2 files

Syncing to parent project...
✓ Updated 3 files
⚠️  1 conflict detected (review required)

Report: apps/web/.ai-agents/update-reports/update-20251207-143022.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Project 2/3: apps/mobile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... similar output ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Project 3/3: apps/admin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... similar output ...]
```

**Batch Summary:**

```markdown
# Batch Update Summary

**Projects processed:** 3
**Updated:** 2 (web, mobile)
**Skipped:** 1 (api - already up to date)
**Failed:** 0

## Statistics
- Total commits pulled: 4
- Total files synced: 8
- Conflicts detected: 1 (apps/web)

## Next Steps
1. Review individual reports in each project
2. Resolve conflict in apps/web
3. Test each updated project
4. Commit changes to project repos

📊 Full report: my-company/.ai-agents/batch-update-20251207-143022.md
```

**When to use:**
- Development environments
- Multiple experimental projects
- Staging servers
- Regular maintenance updates

#### Scenario 3: Mixed Strategy

Critical apps individually, experiments in batch:

```bash
# Update production app with careful review
/pull-ai-agents-submodule ./apps/production
# ... review carefully, test thoroughly, commit ...

# Batch update development/experimental apps
/pull-ai-agents-submodule ./apps/dev --recursive
# ... quick review of batch summary ...

# Batch update staging
/pull-ai-agents-submodule ./apps/staging --recursive
```

**When to use:**
- Mixed environment (prod + dev + staging)
- Some projects critical, others experimental
- Want speed for low-risk, care for high-risk

### Benefits

✅ **Time Savings:** Update 10 projects in one command vs 10 separate runs
✅ **Consistency:** All projects get same updates simultaneously
✅ **Visibility:** Batch summary shows overall state across projects
✅ **Selective Control:** Choose which projects to update (Yes/Select/Cancel)
✅ **Independent Updates:** One project failure doesn't stop others
✅ **Detailed Reports:** Per-project + batch summary for audit trail

### Best Practices

1. **Group by risk level:**
   ```bash
   # Critical apps: individual updates
   /pull-ai-agents-submodule ./apps/production

   # Low-risk apps: batch updates
   /pull-ai-agents-submodule ./apps/internal-tools --recursive
   ```

2. **Test before wide deployment:**
   ```bash
   # Update dev first
   /pull-ai-agents-submodule ./envs/dev --recursive

   # Test thoroughly, then staging
   /pull-ai-agents-submodule ./envs/staging --recursive

   # Finally production (individually)
   /pull-ai-agents-submodule ./envs/production/app1
   /pull-ai-agents-submodule ./envs/production/app2
   ```

3. **Review batch summary:**
   - Check for conflicts across projects
   - Note breaking changes
   - Identify common issues

4. **Commit strategy:**
   ```bash
   # Each project commits independently
   cd apps/web && git add . && git commit -m "chore: sync AI_agents updates"
   cd apps/mobile && git add . && git commit -m "chore: sync AI_agents updates"
   # etc.
   ```

5. **Schedule regular syncs:**
   - Weekly: Development projects (batch mode)
   - Bi-weekly: Staging projects (batch mode)
   - Monthly: Production projects (individual mode)

### Troubleshooting

**Problem**: Too many projects found
**Solution**: Use more specific path
```bash
# Instead of root
/pull-ai-agents-submodule --recursive  # Finds 50 projects!

# Use specific directory
/pull-ai-agents-submodule ./apps --recursive  # Finds 4 projects
```

**Problem**: Want to skip certain projects permanently
**Solution**: Use parent directory or selective mode
```bash
# Scenario: Skip legacy/ directory
my-company/
├── apps/         ← Update these
├── services/     ← Update these
└── legacy/       ← Skip these

# Update apps and services separately
/pull-ai-agents-submodule ./apps --recursive
/pull-ai-agents-submodule ./services --recursive
# Don't run on legacy/
```

**Problem**: One project has conflicts, need to handle separately
**Solution**: Projects are independent - handle conflict manually
```bash
# Batch update completed, apps/web has conflict
# Other projects (apps/mobile, apps/api) updated successfully

# Handle conflict in apps/web
cd apps/web
# Review conflict in update report
# Manually merge or choose version
# Test and commit

# Other projects already done!
```

**Problem**: Want different update cadence per project
**Solution**: Update different directories at different times
```bash
# Weekly for dev
/pull-ai-agents-submodule ./envs/dev --recursive

# Bi-weekly for staging (run every 2 weeks)
/pull-ai-agents-submodule ./envs/staging --recursive

# Monthly for production (run monthly, individually)
/pull-ai-agents-submodule ./envs/production/app1
```

---

## Coordination Model Comparison

| Aspect | Human-Coord | Task Tool | Automated |
|--------|-------------|-----------|-----------|
| **Setup** | Simple | Simple | Complex |
| **Control** | Full | Full | Less |
| **Speed** | Sequential | Sequential | Parallel |
| **Context** | No isolation | Fresh per agent | Fresh per agent |
| **Cost** | Lower | **Zero API costs** | Higher (API) |
| **Learning Curve** | Low | Low | High |
| **Scalability** | 1-3 agents | 3-7 agents | 5+ agents |
| **Automation** | Manual | Semi-automated | Fully automated |
| **Best For** | Learning | Production | CI/CD |

---

## Workflow Selection Guide

### Decision Tree

```
Do you have existing infrastructure?
├─ YES → Simple Mode
│   └─ 1-3 agents? → Human-Coordinated
│   └─ 3-5 agents? → Task Tool Delegation
│
└─ NO → Complex Mode
    ├─ Learning? → Human-Coordinated with IT Specialist
    ├─ Production? → Task Tool Delegation with full team
    └─ CI/CD? → Fully Automated
```

### By Project Type

| Project Type | Recommended Mode | Coordination |
|--------------|------------------|--------------|
| Small feature on existing app | Simple | Human-Coord |
| Medium feature on existing app | Simple | Task Tool |
| New greenfield project | Complex | Task Tool |
| Enterprise system | Complex | Task Tool or Automated |
| CI/CD pipeline | Complex | Fully Automated |
| Learning/experimenting | Simple | Human-Coord |

### By Team Size

| Team Size | Mode | Coordination |
|-----------|------|--------------|
| 1-3 agents | Simple | Human-Coord |
| 3-5 agents | Simple or Complex | Task Tool |
| 5-7 agents | Complex | Task Tool |
| 7+ agents | Complex | Fully Automated |

### By Project Phase

| Phase | Mode | Coordination |
|-------|------|--------------|
| **MVP/Prototype** | Simple | Human-Coord |
| **Feature Development** | Simple | Task Tool |
| **New Product** | Complex | Task Tool |
| **Production Scale** | Complex | Automated |

---

## Best Practices

### Workflow Design

1. **Start Simple** - Begin with Simple Mode, upgrade if needed
2. **Define Interfaces** - API contracts before implementation
3. **Branch Isolation** - One branch per agent per task
4. **Quality Gates** - Enforce tests, reviews, coverage (Complex Mode)
5. **Session Handoffs** - Use session-progress.json (Complex Mode)

### Coordination

6. **Fresh Context** - Use Task tool to prevent Manager bloat
7. **Structured Messages** - Use JSON protocol for clarity
8. **Monitor Context** - Watch for context warnings
9. **Regular Checkpoints** - Every 10 turns or at 75% context
10. **Document Blockers** - Track in session-progress.json

### Scaling

11. **Parallel When Possible** - Identify independent work
12. **Sequential When Needed** - Respect dependencies
13. **Limit Scope** - Better 10 small tasks than 3 large ones
14. **Measure Progress** - Use feature-tracking.json metrics
15. **Resume Efficiently** - Read session-progress.json first

---

## See Also

- **State Files:** [01-state-files.md](01-state-files.md)
- **Agent Setup:** [02-agents.md](02-agents.md)
- **Practical Guide:** `PRACTICAL_WORKFLOW_GUIDE.md`
- **Manager Guide:** `prompts/manager-task-delegation.md`
- **Orchestration:** `scripts/orchestration/COMPLETE_GUIDE.md`

---

[← Back to Index](index.md) | [Previous: Commands](04-commands.md) | [Next: Scripts & Tools →](06-scripts-tools.md)
