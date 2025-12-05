---
description: Generate optimized manager prompt from plan files with state coordination and Task tool delegation
argument-hint: ['@path/to/PLAN.md or plan description']
---

# Create Manager Meta-Prompt

Generate an optimized manager prompt for executing a plan using the AI_agents multi-agent workflow system.

## What This Command Does

1. **Analyzes your plan** (PLAN.md, phase files, or description)
2. **Generates manager prompt** optimized for:
   - Task Tool Delegation (fresh context per agent)
   - State file coordination (team-communication.json)
   - Proper agent spawning sequence
   - Progress tracking and handoffs
3. **Outputs ready-to-use prompt** you can paste into Claude

## Usage

### From Plan File
```
/create-manager-meta-prompt @.planning/PLAN-authentication.md
```

### From Description
```
/create-manager-meta-prompt "Implement authentication system with JWT tokens, user registration, login, and password reset"
```

### From Multiple Phase Files
```
/create-manager-meta-prompt @.planning/phases/01-PLAN.md @.planning/phases/02-PLAN.md
```

## Generated Prompt Includes

The manager prompt will include:

### 1. Context Setup
- Project understanding
- Plan breakdown
- Success criteria

### 2. State File Coordination
```json
// Reads from: .ai-agents/state/team-communication.json
{
  "manager_instructions": {},
  "agent_updates": [],
  "integration_requests": []
}
```

### 3. Task Tool Delegation Pattern
```
Manager spawns agents via Task tool:
- IT Specialist (SETUP-001) → validates infrastructure
- Backend Dev (AUTH-001) → implements endpoints
- Frontend Dev (AUTH-002) → builds UI
- QA Tester (TEST-001) → writes E2E tests
- Senior Engineer (REVIEW-001) → reviews and merges
```

### 4. Workflow Mode Selection
- **Simple Mode:** Manager → Task Agents → Integration Agent
- **Complex Mode:** Manager → IT Specialist → Task Agents → Senior Engineer

### 5. Session Management
- Progress tracking
- Blocker handling
- Handoff creation (/whats-next)

## Workflow Integration

This command fits into the standard workflow:

```
1. /create-plan "your project"
   └─ Generates PLAN.md with phases

2. /create-manager-meta-prompt @PLAN.md  ← YOU ARE HERE
   └─ Generates manager prompt

3. Paste manager prompt into Claude
   └─ Manager executes using Task tool delegation
```

## Example Output

The command generates a prompt like:

```markdown
# Manager: Authentication System Implementation

You are the Manager agent coordinating a multi-agent team to implement an authentication system.

## Objective
[Extracted from plan...]

## State File Setup
Ensure .ai-agents/state/team-communication.json exists:
[Setup commands...]

## Execution Plan
Phase 1: Infrastructure Validation (IT Specialist)
- Task: SETUP-001
- Spawn: IT Specialist via Task tool
- Wait for completion

Phase 2: Backend Development
- Task: AUTH-001 (Registration)
- Spawn: Backend Developer via Task tool
[etc...]

## Coordination Protocol
1. Read team-communication.json before each decision
2. Spawn agents one at a time via Task tool
3. Wait for completion before spawning next
4. Update team-communication.json with progress
5. At session end: Create handoff with /whats-next

## Success Criteria
[From plan...]
```

## Workflow Mode Options

### Simple Mode (Default)
**Use when:** 1-3 days, existing infrastructure, 3-5 agents

Generated prompt includes:
- Manager → Task Agents → Integration Agent
- team-communication.json only
- Task Tool Delegation

### Complex Mode
**Use when:** Multi-day, new infrastructure, 5+ agents, code review needed

Add `--complex` flag:
```
/create-manager-meta-prompt @PLAN.md --complex
```

Generated prompt includes:
- Manager → IT Specialist → Task Agents → Senior Engineer
- All three state files (team-communication, session-progress, feature-tracking)
- E2E testing enforcement
- Code review gates
- Session continuity

## Advanced Options

### Specify Workflow Mode
```
/create-manager-meta-prompt @PLAN.md --mode simple
/create-manager-meta-prompt @PLAN.md --mode complex
```

### Include Specific Agents
```
/create-manager-meta-prompt @PLAN.md --agents "IT Specialist, Backend Dev, Frontend Dev, QA Tester"
```

### Set State File Location
```
/create-manager-meta-prompt @PLAN.md --state-dir .ai-agents/state
```

## Tips

**Do:**
- ✅ Create plan first with `/create-plan`
- ✅ Review generated prompt before using
- ✅ Set up state files before starting
- ✅ Use Task Tool Delegation (included by default)

**Don't:**
- ❌ Skip state file setup
- ❌ Modify generated prompt heavily (defeats optimization)
- ❌ Use Complex Mode for simple 1-day tasks

## See Also

- **Planning:** `/create-plan` - Create the plan first
- **State Files:** `docs/reference/CHEAT_SHEET/01-state-files.md`
- **Workflows:** `docs/reference/CHEAT_SHEET/05-workflows.md`
- **Manager Guide:** `prompts/manager-task-delegation.md`

---

**Implementation:** This command uses the `create-meta-prompts` skill with manager-specific templates and patterns.
