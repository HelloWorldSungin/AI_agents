# State Files System

The system uses three complementary JSON files for state management and coordination, with optional external state providers for session continuity.

**Version:** 1.4.0
**Last Updated:** 2025-12-12

---

## External State Providers (NEW v1.4.0)

Persist agent state in external systems to survive context resets.

### Why External State?

File-based state has limitations:
- ❌ Lost when agent context resets
- ❌ Not visible to humans during execution
- ❌ Multiple agents can't coordinate easily
- ❌ No integration with team workflows

External providers solve this:
- ✅ State survives context resets
- ✅ Visible in Linear/GitHub dashboards
- ✅ Multi-agent coordination
- ✅ Integrates with existing workflows

### Available Providers

| Provider | Best For | Configuration |
|----------|----------|---------------|
| **Linear** | Teams using Linear for project management | `type: "linear"` |
| **GitHub** | Projects using GitHub Issues | `type: "github"` |
| **File** | Local development, offline work | `type: "file"` |

### Linear Provider (Recommended)

```yaml
# .ai-agents/config.yml
state_provider:
  type: "linear"
  api_key_env: "LINEAR_API_KEY"
  team_id: "${LINEAR_TEAM_ID}"      # Optional, auto-detected
  project_name: "My Project"        # Auto-created if needed
  meta_issue_label: "meta"
```

**Features:**
- Tasks → Linear Issues with acceptance criteria
- Sessions → Comments on META issue
- Progress → Real-time in Linear dashboard
- Labels → Task categories and priorities

**Setup:**
```bash
# 1. Get API key from Linear Settings → API → Personal API Keys
export LINEAR_API_KEY="lin_api_xxxxx"

# 2. Initialize project
/start-project
```

### GitHub Provider

```yaml
state_provider:
  type: "github"
  api_key_env: "GITHUB_TOKEN"
  repo: "owner/repo"
  meta_issue_label: "meta"
```

### File Provider (Fallback)

```yaml
state_provider:
  type: "file"
  state_dir: ".ai-agents/state"
```

### Usage Commands

```bash
# Initialize new project with state provider
/start-project

# Resume from external state
/continue-project

# Check current state
/continue-project --status-only
```

---

## Three-File State Management

### Overview

| File | Purpose | Lifespan | Required In |
|------|---------|----------|-------------|
| `team-communication.json` | Real-time coordination | Within session (ephemeral) | Simple & Complex Mode |
| `session-progress.json` | Cross-session continuity | Persistent | Complex Mode only |
| `feature-tracking.json` | Feature verification | Persistent | Complex Mode only |

---

## 1. Real-Time Communication

**File:** `team-communication.json`
**Location:** `.ai-agents/state/team-communication.json`

### Purpose
Live coordination within a session - agents communicate in real-time.

### Structure
```json
{
  "manager_instructions": {
    "current_focus": "Implementing user authentication",
    "active_tasks": ["AUTH-001", "AUTH-002"]
  },
  "agent_updates": [
    {
      "agent_id": "backend_developer",
      "task_id": "AUTH-001",
      "status": "completed",
      "timestamp": "2025-12-04T10:30:00Z"
    }
  ],
  "integration_requests": [
    {
      "from": "backend_developer",
      "to": "integration_agent",
      "branch": "feature/auth-endpoints"
    }
  ]
}
```

### Used For
- Task assignments (Manager → Agents)
- Status updates (Agents → Manager)
- Inter-agent coordination
- Real-time communication

### Lifespan
Within session - can be cleared between sessions (ephemeral).

---

## 2. Session Progress

**File:** `session-progress.json`
**Location:** `.ai-agents/state/session-progress.json`
**Schema:** `schemas/session-progress.json`

### Purpose
Resume work across sessions WITHOUT rediscovering state (50% faster startup).

### Structure
```json
{
  "session_id": "003",
  "start_time": "2025-12-07T09:00:00Z",
  "last_session": "2025-12-03T18:00:00Z",
  "current_phase": "authentication-implementation",
  "completed_phases": ["setup", "infrastructure"],
  "completed_tasks": ["SETUP-001", "DB-001", "AUTH-001"],
  "active_tasks": [
    {
      "id": "AUTH-002",
      "description": "Password reset flow",
      "agent": "backend_developer",
      "status": "in_progress",
      "blockers": []
    }
  ],
  "blocked_tasks": [],
  "decisions_made": [],
  "next_priorities": ["AUTH-002", "TEST-001"],
  "git_baseline": "abc123def456",
  "notes": "Authentication endpoints complete, need password reset",
  "manager_agent": "@auth-manager",
  "last_handoff": {
    "session_id": "002",
    "file": ".ai-agents/handoffs/session-002.md",
    "timestamp": "2025-12-03T18:00:00Z",
    "next_session_priority": "Complete AUTH-002"
  }
}
```

### Used For
- Resume work without rediscovery
- Track project phase
- Document blockers
- Set priorities for next session
- Git baseline tracking

### Lifespan
Persistent across all sessions - never cleared.

---

## 3. Feature Tracking

**File:** `feature-tracking.json`
**Location:** `.ai-agents/state/feature-tracking.json`
**Schema:** `schemas/feature-tracking.json`

### Purpose
Detailed pass/fail status with E2E testing enforcement.

### Structure
```json
{
  "features": [
    {
      "id": "AUTH-001",
      "description": "User registration endpoint",
      "status": "passing",
      "implementation": {
        "files": ["src/auth/register.ts"],
        "completed_by": "backend_developer",
        "completed_at": "2025-12-03T16:30:00Z"
      },
      "testing": {
        "unit_tests": "tests/unit/auth/register.test.ts",
        "e2e_tests": "tests/e2e/auth/register.spec.ts",
        "test_status": "passing"
      },
      "verified_by": "senior_engineer",
      "verified_at": "2025-12-03T17:00:00Z"
    },
    {
      "id": "AUTH-002",
      "description": "Password reset flow",
      "status": "in_progress",
      "implementation": {
        "files": ["src/auth/reset.ts"],
        "completed_by": null,
        "completed_at": null
      },
      "testing": {
        "unit_tests": null,
        "e2e_tests": null,
        "test_status": "pending"
      }
    }
  ],
  "summary": {
    "total": 8,
    "passing": 1,
    "in_progress": 1,
    "failing": 0,
    "not_started": 6
  }
}
```

### Used For
- Track pass/fail status
- Prevent premature "done" declarations
- Enforce E2E testing (mandatory in Complex Mode)
- Show progress metrics
- Code review verification

### Feature Completion Criteria

Features can ONLY be marked "passing" when ALL of these are met:
1. ✅ Code implemented
2. ✅ Unit tests written and passing
3. ✅ E2E tests written and passing (MANDATORY)
4. ✅ Code reviewed by Senior Engineer
5. ✅ Integration verified

**Note:** Senior Engineer blocks merges if E2E tests are missing.

### Lifespan
Persistent through project lifecycle - updated as features progress.

---

## Quick Reference: Which File When?

| Action | File | When |
|--------|------|------|
| Assign task to agent | `team-communication.json` | During session |
| Agent reports status | `team-communication.json` | During session |
| Inter-agent coordination | `team-communication.json` | During session |
| End session | Update `session-progress.json` + `feature-tracking.json` | End of day |
| Resume work next day | Read `session-progress.json` first | Start of new session |
| Mark feature complete | Update `feature-tracking.json` | After E2E tests pass + code review |
| Check progress metrics | Read `feature-tracking.json` summary | Anytime |
| Document blockers | Update `session-progress.json` | When blocked |

---

## Mode Usage

### Simple Mode
**Uses:** `team-communication.json` only

**Best for:**
- Quick features (1-3 days)
- Single session work
- 3-5 agents
- Established projects

### Complex Mode
**Uses:** All three files

**Best for:**
- Multi-day/multi-session work
- New projects needing infrastructure
- 5+ agents
- Rigorous code review required
- Session continuity needed

---

## How They Work Together

```
Session Start (Day 1)
└─ Manager reads: session-progress.json (if resuming)
   └─ Creates tasks in: team-communication.json
      └─ Agents work using: team-communication.json
         └─ Manager updates: feature-tracking.json
            └─ Session end: Update both persistent files

Session Start (Day 2)
└─ Manager reads: session-progress.json ← 50% faster startup!
   └─ Knows exactly what's done, what's next
      └─ No need to rediscover state
```

**Key Insight:** The three files are **complementary, not replacements**:
- `team-communication.json` = Live coordination (ephemeral)
- `session-progress.json` = Continuity (persistent)
- `feature-tracking.json` = Verification (persistent)

---

## Setup Examples

### Simple Mode Setup
```bash
# Only need team-communication.json
mkdir -p .ai-agents/state
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {},
  "agent_updates": [],
  "integration_requests": []
}
EOF
```

### Complex Mode Setup
```bash
# Need all three files
mkdir -p .ai-agents/state

# 1. Real-time communication
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {},
  "agent_updates": [],
  "integration_requests": []
}
EOF

# 2. Session progress
cat > .ai-agents/state/session-progress.json << 'EOF'
{
  "session_id": "001",
  "start_time": null,
  "last_session": null,
  "current_phase": "initial-setup",
  "completed_phases": [],
  "completed_tasks": [],
  "active_tasks": [],
  "blocked_tasks": [],
  "decisions_made": [],
  "next_priorities": [],
  "git_baseline": null,
  "notes": "",
  "manager_agent": "@project-manager",
  "last_handoff": null
}
EOF

# 3. Feature tracking
cat > .ai-agents/state/feature-tracking.json << 'EOF'
{
  "features": [],
  "summary": {
    "total": 0,
    "passing": 0,
    "in_progress": 0,
    "failing": 0,
    "not_started": 0
  }
}
EOF
```

---

## See Also

- **External State Pattern:** `prompts/patterns/external-state-provider.md`
- **Session Continuity Pattern:** `prompts/patterns/session-continuity.md`
- **Complete Guide:** [docs/guides/LONG_RUNNING_AGENTS.md](../guides/LONG_RUNNING_AGENTS.md)
- **Workflow Examples:** [05-workflows.md](05-workflows.md)
- **Schemas:** [08-schemas.md](08-schemas.md)

---

[← Back to Index](index.md) | [Previous: Quick Start](00-quick-start.md) | [Next: Agents →](02-agents.md)
