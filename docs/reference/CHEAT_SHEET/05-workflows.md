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
