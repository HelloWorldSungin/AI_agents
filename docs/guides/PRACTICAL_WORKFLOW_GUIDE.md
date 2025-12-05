# Practical Multi-Agent Workflow Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-21
**Purpose:** Step-by-step guide for human-coordinated multi-agent workflows

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Communication Protocol](#communication-protocol)
- [Complete Workflow Example](#complete-workflow-example)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)
- [Advanced Techniques](#advanced-techniques)

---

## Overview

### What is Human-Coordinated Multi-Agent?

**Human-coordinated multi-agent** is a practical approach where **you** orchestrate multiple AI agents working together on a project. Instead of agents automatically communicating, you act as the coordinator, running agents in sequence and relaying information between them.

### Why This Approach?

✅ **Works with any LLM tool** (Claude Code, ChatGPT, etc.)
✅ **No programming required** - just use your LLM interface
✅ **Full control** - you see and approve everything
✅ **Cost-effective** - one agent at a time
✅ **Easy to learn** - start immediately
✅ **Practical for 90% of use cases**

### How It Works

```
┌─────────┐
│   YOU   │  ← The Coordinator
└────┬────┘
     │
     ├──> 📋 Manager Agent (creates plan)
     ├──> 💻 Backend Agent (implements API)
     ├──> 🎨 Frontend Agent (builds UI)
     └──> 🧪 QA Agent (tests everything)
```

**You relay information between agents using a shared communication file.**

---

## Quick Start

### Step 1: Set Up Communication Infrastructure

In your project directory, create the communication file:

```bash
# Navigate to your project
cd your-project

# Create state directory if it doesn't exist
mkdir -p .ai-agents/state

# Create communication file
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "last_updated": "2025-11-21T00:00:00Z",
  "project_name": "My Project",
  "current_feature": "",

  "manager_instructions": {
    "current_focus": "",
    "active_tasks": [],
    "completed_tasks": [],
    "blocked_tasks": []
  },

  "agent_updates": [],

  "shared_resources": {
    "api_contracts": [],
    "type_definitions": [],
    "documentation": []
  }
}
EOF
```

### Step 2: Add Communication Protocol to Agent Context

Create `.ai-agents/context/communication-protocol.md`:

```markdown
# Agent Communication Protocol

## Overview
All agents communicate through `.ai-agents/state/team-communication.json`.

## Instructions for All Agents

### At Session Start
1. Read `.ai-agents/state/team-communication.json`
2. Review sections relevant to your role
3. Note your assigned tasks, blockers, and questions

### During Work
- Update your status when you make significant progress (25%, 50%, 75%, 100%)
- Report blockers immediately
- Ask questions by adding them to your update

### Session End
- Write final status update to the communication file
- List completed items
- Note any questions for next session
- Mention files you created/modified

## Update Format

When updating the communication file, add an entry to `agent_updates` array:

```json
{
  "timestamp": "2025-11-21T10:30:00Z",
  "agent_id": "backend-dev",
  "task_id": "TASK-001",
  "status": "in_progress",
  "progress": 60,
  "message": "JWT service implemented, working on auth middleware",
  "completed_items": [
    "Created src/services/jwt.ts",
    "Added JWT types in src/types/auth.ts"
  ],
  "blockers": [],
  "questions_for_manager": []
}
```

## Status Values
- `not_started` - Task assigned but not yet begun
- `in_progress` - Actively working on task
- `blocked` - Cannot proceed without resolution
- `ready_for_review` - Work complete, needs review
- `completed` - Fully done and merged
```

### Step 3: Update Agent Configurations

Add this to each agent's context in your config.yml:

```yaml
agents:
  team_manager:
    base: "base/manager.md"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/communication-protocol.md"  # ← Add this

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/api-contracts.md"
      - ".ai-agents/context/communication-protocol.md"  # ← Add this

  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/api-contracts.md"
      - ".ai-agents/context/communication-protocol.md"  # ← Add this
```

---

## Understanding State Files

### Three-File State System

The AI_agents system uses **three complementary state files** for coordination. Understanding their roles is crucial:

#### 1. Real-Time Communication (`team-communication.json`)
**Purpose**: Live coordination **within a single session**

```json
{
  "manager_instructions": {
    "current_focus": "User authentication",
    "active_tasks": [...]
  },
  "agent_updates": [
    {"agent_id": "backend-dev", "status": "completed", ...}
  ],
  "integration_requests": [...]
}
```

**Used for**:
- ✅ Manager assigns tasks to agents
- ✅ Agents report status back
- ✅ Agents request help from each other
- ✅ Coordination during active work

**Lifespan**: Within session (can be cleared between sessions)

---

#### 2. Session Progress (`session-progress.json`)
**Purpose**: **Cross-session continuity** - resume work days/weeks later

```json
{
  "last_session": "2025-12-03T18:00:00Z",
  "current_phase": "authentication-implementation",
  "completed_tasks": ["SETUP-001", "DB-001"],
  "active_tasks": ["AUTH-002"],
  "blockers": [],
  "next_priorities": ["AUTH-002", "TASK-001"],
  "git_baseline": "abc123",
  "notes": "Login in progress, registration complete"
}
```

**Used for**:
- ✅ **Next session** - "Where did we leave off?"
- ✅ Prevents redundant planning (50% faster startup)
- ✅ Tracks overall project phase
- ✅ Documents blockers for next time

**Lifespan**: Persistent across all sessions

---

#### 3. Feature Tracking (`feature-tracking.json`)
**Purpose**: Detailed feature status with **pass/fail verification**

```json
{
  "features": [
    {
      "id": "AUTH-001",
      "description": "User registration",
      "status": "passing",
      "test_file": "tests/auth/register.spec.ts",
      "verified_by": "senior_engineer"
    }
  ],
  "summary": {
    "total": 8,
    "passing": 1,
    "in_progress": 1,
    "failing": 0
  }
}
```

**Used for**:
- ✅ Track feature pass/fail status
- ✅ Prevent premature "done" declarations
- ✅ Enforce E2E testing
- ✅ Show progress metrics (6/8 complete)

**Lifespan**: Persistent, tracks entire project lifecycle

---

### How They Work Together

**Within a Session:**
```
1. Manager reads session-progress.json (if resuming)
2. Manager writes tasks to team-communication.json
3. Agents read team-communication.json for assignments
4. Agents update team-communication.json with status
5. Manager updates feature-tracking.json when features complete
```

**End of Session:**
```
Manager updates:
  - session-progress.json: What's done, what's next
  - feature-tracking.json: Feature statuses
  - Commits all to git
```

**Next Session (Days Later):**
```
Manager reads:
  1. session-progress.json → "We completed AUTH-001, AUTH-002 is active"
  2. feature-tracking.json → "1/8 features passing"
  3. Skips re-planning → Continues immediately

Result: 50% faster startup, no wasted time
```

---

### When to Use Which File

| Scenario | File to Use |
|----------|-------------|
| Assigning task to agent | `team-communication.json` |
| Agent reporting "done" | `team-communication.json` |
| Agent requesting help | `team-communication.json` |
| Wrapping up session | Update `session-progress.json` and `feature-tracking.json` |
| Starting new session | Read `session-progress.json` first |
| Checking progress | Read `feature-tracking.json` summary |
| Marking feature "passing" | Update `feature-tracking.json` |

---

### Quick Setup for All Three Files

```bash
# Create state directory
mkdir -p .ai-agents/state

# 1. Team communication (real-time)
cat > .ai-agents/state/team-communication.json << 'EOF'
{
  "manager_instructions": {"current_focus": "", "active_tasks": []},
  "agent_updates": [],
  "integration_requests": []
}
EOF

# 2. Session progress (cross-session)
cat > .ai-agents/state/session-progress.json << 'EOF'
{
  "last_session": null,
  "current_phase": "initialization",
  "completed_tasks": [],
  "active_tasks": [],
  "blockers": [],
  "next_priorities": []
}
EOF

# 3. Feature tracking (verification)
cat > .ai-agents/state/feature-tracking.json << 'EOF'
{
  "project": "your-project-name",
  "features": [],
  "summary": {"total": 0, "passing": 0, "in_progress": 0, "failing": 0}
}
EOF
```

**Schemas available**: See `schemas/session-progress.json` and `schemas/feature-tracking.json` for complete structures.

---

## Communication Protocol

### The Communication File Structure (team-communication.json)

```json
{
  "last_updated": "ISO 8601 timestamp",

  "manager_instructions": {
    // Manager writes here
    "current_focus": "What the team is working on",
    "active_tasks": [
      {
        "task_id": "TASK-001",
        "assigned_to": "backend-dev",
        "description": "What needs to be done",
        "status": "in_progress",
        "branch": "feature/auth/agent/backend-dev/api",
        "priority": "high|medium|low",
        "dependencies": ["TASK-000"],
        "deadline": "ISO 8601 timestamp (optional)"
      }
    ],
    "decisions": [
      {
        "decision": "Use JWT for authentication",
        "rationale": "Industry standard, well-supported",
        "affected_agents": ["backend-dev", "frontend-dev"]
      }
    ]
  },

  "agent_updates": [
    // Agents write here
    {
      "timestamp": "ISO 8601 timestamp",
      "agent_id": "backend-dev|frontend-dev|qa-tester|etc",
      "task_id": "TASK-XXX",
      "status": "not_started|in_progress|blocked|ready_for_review|completed",
      "progress": 0-100,
      "message": "Human-readable status update",
      "completed_items": ["List of deliverables"],
      "blockers": [
        {
          "description": "What's blocking you",
          "blocking_agent": "Who can unblock (if applicable)",
          "severity": "high|medium|low"
        }
      ],
      "questions_for_manager": ["Questions that need answers"]
    }
  ],

  "shared_resources": {
    // Shared artifacts
    "api_contracts": [
      {
        "endpoint": "/api/auth/login",
        "file": ".ai-agents/context/api-contracts.md#login",
        "status": "approved",
        "version": "1.0.0"
      }
    ],
    "type_definitions": [
      {
        "type": "User",
        "file": "src/types/user.ts",
        "defined_by": "backend-dev"
      }
    ]
  }
}
```

### Communication Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Manager Updates                                       │
│    - Creates tasks in manager_instructions.active_tasks │
│    - Sets priorities and assignments                    │
│    - Makes decisions and adds them to decisions array   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. YOU (Coordinator)                                     │
│    - Read the file                                       │
│    - Start appropriate agent session                    │
│    - Tell agent: "Read team-communication.json and      │
│      work on your assigned task"                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Task Agent Works                                      │
│    - Reads team-communication.json                      │
│    - Sees their assignment                              │
│    - Works on the task                                  │
│    - Adds update to agent_updates array                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. YOU (Coordinator) Reads Updates                       │
│    - Check team-communication.json                      │
│    - See agent's progress, blockers, questions          │
│    - Decide next steps                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Back to Manager (if needed)                           │
│    - Show manager the agent updates                     │
│    - Manager addresses blockers                         │
│    - Manager answers questions                          │
│    - Manager updates instructions                       │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Workflow Example

### Scenario: Building User Authentication Feature

Let's walk through a complete example from start to finish.

---

### Session 1: Manager Planning

**You start a conversation with the Manager agent:**

```
YOU: We need to implement user authentication using JWT tokens.
     Please read team-communication.json and create a task breakdown.
```

**Manager reads the file, creates task plan:**

```json
{
  "last_updated": "2025-11-21T09:00:00Z",
  "project_name": "TaskFlow App",
  "current_feature": "JWT Authentication",

  "manager_instructions": {
    "current_focus": "Implementing JWT-based user authentication",
    "active_tasks": [
      {
        "task_id": "TASK-001",
        "assigned_to": "backend-dev",
        "description": "Implement JWT authentication service and API endpoints",
        "status": "not_started",
        "branch": "feature/auth/agent/backend-dev/api",
        "priority": "high",
        "dependencies": [],
        "deliverables": [
          "JWT service (src/services/jwt.ts)",
          "Auth controller (src/controllers/auth.ts)",
          "POST /api/auth/login endpoint",
          "POST /api/auth/register endpoint",
          "Auth middleware for protected routes"
        ]
      },
      {
        "task_id": "TASK-002",
        "assigned_to": "frontend-dev",
        "description": "Build login and registration UI components",
        "status": "not_started",
        "branch": "feature/auth/agent/frontend-dev/ui",
        "priority": "high",
        "dependencies": ["TASK-001"],
        "deliverables": [
          "Login form component",
          "Registration form component",
          "Auth context/state management",
          "Protected route wrapper"
        ]
      },
      {
        "task_id": "TASK-003",
        "assigned_to": "qa-tester",
        "description": "Write tests for authentication flow",
        "status": "not_started",
        "branch": "feature/auth/agent/qa/tests",
        "priority": "medium",
        "dependencies": ["TASK-001", "TASK-002"],
        "deliverables": [
          "API endpoint tests",
          "UI component tests",
          "End-to-end authentication flow tests"
        ]
      }
    ],
    "decisions": [
      {
        "decision": "Use JWT with 1-hour expiration for access tokens",
        "rationale": "Security best practice, short-lived tokens reduce risk",
        "affected_agents": ["backend-dev", "frontend-dev"]
      },
      {
        "decision": "Frontend will use API contract with mock data until backend is ready",
        "rationale": "Enable parallel development without blocking",
        "affected_agents": ["frontend-dev"]
      }
    ]
  },

  "agent_updates": [],

  "shared_resources": {
    "api_contracts": []
  }
}
```

**Manager also creates API contract** in `.ai-agents/context/api-contracts.md`:

```markdown
# Authentication API Contract

## POST /api/auth/login

**Request:**
```json
{
  "email": "string (email format)",
  "password": "string (min 8 chars)"
}
```

**Response (200 OK):**
```json
{
  "token": "string (JWT)",
  "expiresAt": "string (ISO 8601)",
  "user": {
    "id": "string (UUID)",
    "email": "string",
    "name": "string"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```
```

**You review the plan:**
```
YOU: Great! I can see the task breakdown. I'll start with the backend agent.
```

---

### Session 2: Backend Developer Working

**You switch to Backend Developer agent:**

```
YOU: Please read .ai-agents/state/team-communication.json and work on
     your assigned task (TASK-001). Create the branch and start implementing.
```

**Backend agent:**
1. Reads team-communication.json
2. Sees TASK-001 is assigned to them
3. Creates branch: `feature/auth/agent/backend-dev/api`
4. Implements JWT service, auth controller, API endpoints
5. After 60% progress, updates the file:

```json
{
  "agent_updates": [
    {
      "timestamp": "2025-11-21T10:30:00Z",
      "agent_id": "backend-dev",
      "task_id": "TASK-001",
      "status": "in_progress",
      "progress": 60,
      "message": "JWT service and auth controller implemented, working on middleware",
      "completed_items": [
        "Created src/services/jwt.ts with token generation and verification",
        "Created src/controllers/auth.ts with login/register handlers",
        "Defined User type in src/types/user.ts",
        "Implemented POST /api/auth/login endpoint",
        "Implemented POST /api/auth/register endpoint"
      ],
      "in_progress": [
        "Auth middleware for protected routes"
      ],
      "blockers": [],
      "questions_for_manager": [
        "Should we implement refresh tokens in this iteration or defer to v2?"
      ],
      "available_for_other_agents": [
        "User type definition in src/types/user.ts",
        "JWT token format (see src/services/jwt.ts for structure)"
      ]
    }
  ]
}
```

**Backend agent commits:**
```bash
git add .
git commit -m "feat(auth): Implement JWT service and auth endpoints (60% complete)

Implemented:
- JWT token generation and verification service
- Auth controller with login/register handlers
- API endpoints for authentication
- User type definitions

In Progress:
- Auth middleware for protected routes

Status: TASK-001 60% complete

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**You review:**
```
YOU: Good progress! I see you have a question about refresh tokens.
     Let me check with the manager.
```

---

### Session 3: Back to Manager (Addressing Questions)

**You switch to Manager:**

```
YOU: The backend dev has a question about refresh tokens.
     Please read team-communication.json and provide guidance.
```

**Manager reads the file, sees the question, updates:**

```json
{
  "manager_instructions": {
    "active_tasks": [
      {
        "task_id": "TASK-001",
        "status": "in_progress",
        "notes": "Defer refresh tokens to v2. Focus on core auth flow for v1."
      }
    ],
    "decisions": [
      {
        "decision": "Defer refresh tokens to v2",
        "rationale": "Keep v1 scope focused on core authentication. Refresh tokens add complexity and we need to ship quickly.",
        "affected_agents": ["backend-dev"],
        "in_response_to": "backend-dev question about refresh tokens"
      }
    ]
  }
}
```

**You relay back to backend:**
```
YOU: Manager says to defer refresh tokens to v2. Please continue with
     the auth middleware using the current approach.
```

---

### Session 4: Backend Completes

**Backend agent continues, completes the middleware, updates:**

```json
{
  "agent_updates": [
    {
      "timestamp": "2025-11-21T11:45:00Z",
      "agent_id": "backend-dev",
      "task_id": "TASK-001",
      "status": "ready_for_review",
      "progress": 100,
      "message": "Authentication API complete and tested",
      "completed_items": [
        "JWT service (src/services/jwt.ts)",
        "Auth controller (src/controllers/auth.ts)",
        "POST /api/auth/login endpoint",
        "POST /api/auth/register endpoint",
        "Auth middleware (src/middleware/auth.ts)",
        "Unit tests with 95% coverage"
      ],
      "test_results": {
        "unit_tests": "24 passed, 0 failed",
        "coverage": "95%"
      },
      "blockers": [],
      "questions_for_manager": [],
      "ready_for_merge": false,
      "notes": "Ready for review. Will merge after QA tests pass."
    }
  ]
}
```

---

### Session 5: Frontend Developer (Can Start Now)

**You switch to Frontend Developer:**

```
YOU: Please read team-communication.json. I see the backend has completed
     the auth API. You can now work on TASK-002. Start by creating your branch.
```

**Frontend agent:**
1. Reads team-communication.json
2. Sees TASK-002 assigned, and backend-dev has completed API
3. Reads API contract from `.ai-agents/context/api-contracts.md`
4. Reads User type from `src/types/user.ts` (from backend's work)
5. Creates branch: `feature/auth/agent/frontend-dev/ui`
6. Implements login/register forms, auth state management

**Frontend agent updates after 50%:**

```json
{
  "agent_updates": [
    {
      "timestamp": "2025-11-21T13:00:00Z",
      "agent_id": "frontend-dev",
      "task_id": "TASK-002",
      "status": "in_progress",
      "progress": 50,
      "message": "Login form complete, working on registration form",
      "completed_items": [
        "Created LoginForm component (src/components/auth/LoginForm.tsx)",
        "Created auth context (src/contexts/AuthContext.tsx)",
        "Integrated with auth API endpoints",
        "Added form validation"
      ],
      "in_progress": [
        "Registration form component",
        "Protected route wrapper"
      ],
      "blockers": [],
      "questions_for_manager": [],
      "notes": "Using backend's User type definition. API integration working perfectly."
    }
  ]
}
```

---

### Session 6: Checking In with Manager

**Periodically, you check with Manager:**

```
YOU: Please read team-communication.json and provide a status update
     on the authentication feature.
```

**Manager reviews all agent updates:**

```markdown
# Authentication Feature Status Report

## Overall Progress: 75%

### Completed Tasks
✅ TASK-001 (Backend): Complete and ready for review
   - All deliverables completed
   - 95% test coverage
   - Ready for merge after QA approval

### In Progress Tasks
🔄 TASK-002 (Frontend): 50% complete
   - Login form complete
   - Registration form in progress
   - Expected completion: 2 hours

### Blocked Tasks
None

### Upcoming Tasks
⏳ TASK-003 (QA): Waiting for frontend completion
   - Can start preliminary API tests now
   - Full E2E tests after frontend ready

## Blockers & Risks
None currently

## Decisions Made
- Deferred refresh tokens to v2 (keeps scope focused)
- Frontend using backend's type definitions (good coordination)

## Next Steps
1. Frontend dev: Complete TASK-002
2. QA tester: Start API tests for TASK-001
3. Integration: Merge backend and frontend after QA approval
```

---

### Session 7: QA Agent Starts

**You switch to QA Tester:**

```
YOU: Please read team-communication.json. Backend is complete, frontend is
     in progress. Start with TASK-003 - you can begin API testing now.
```

**QA agent:**
1. Reads communication file
2. Sees backend complete, frontend 50%
3. Decides to start with API tests
4. Creates branch: `feature/auth/agent/qa/tests`
5. Writes API endpoint tests

```json
{
  "agent_updates": [
    {
      "timestamp": "2025-11-21T14:00:00Z",
      "agent_id": "qa-tester",
      "task_id": "TASK-003",
      "status": "in_progress",
      "progress": 40,
      "message": "API tests complete, waiting for frontend to finish UI tests",
      "completed_items": [
        "API endpoint tests (tests/api/auth.test.ts)",
        "JWT token validation tests",
        "Error handling tests"
      ],
      "in_progress": [
        "Waiting for frontend completion to write component tests",
        "E2E tests will follow after integration"
      ],
      "test_results": {
        "api_tests": "18 passed, 0 failed"
      },
      "blockers": [
        {
          "description": "Need frontend components to complete UI tests",
          "blocking_agent": "frontend-dev",
          "severity": "low",
          "notes": "Not blocking - can continue with other tests"
        }
      ]
    }
  ]
}
```

---

### Session 8: Integration

**After frontend completes, you coordinate integration:**

```
YOU (to Manager): All agents have completed their tasks. Please coordinate
                  the integration and merging process.
```

**Manager:**
1. Reviews all agent updates
2. Verifies all tests pass
3. Creates integration plan
4. Updates communication file with merge order:

```json
{
  "manager_instructions": {
    "current_phase": "integration",
    "merge_order": [
      {
        "step": 1,
        "branch": "feature/auth/agent/backend-dev/api",
        "into": "feature/user-auth",
        "reason": "Backend is foundation"
      },
      {
        "step": 2,
        "branch": "feature/auth/agent/frontend-dev/ui",
        "into": "feature/user-auth",
        "reason": "Frontend depends on backend types"
      },
      {
        "step": 3,
        "branch": "feature/auth/agent/qa/tests",
        "into": "feature/user-auth",
        "reason": "Tests validate integration"
      }
    ],
    "integration_checklist": [
      "✅ All agent tests passing",
      "⏳ Merge backend branch",
      "⏳ Merge frontend branch",
      "⏳ Merge QA branch",
      "⏳ Run full test suite",
      "⏳ Verify E2E tests pass",
      "⏳ Merge feature/user-auth into main"
    ]
  }
}
```

**You execute the merges:**

```bash
# Create integration branch
git checkout -b feature/user-auth

# Merge backend
git merge feature/auth/agent/backend-dev/api

# Merge frontend
git merge feature/auth/agent/frontend-dev/ui

# Merge QA
git merge feature/auth/agent/qa/tests

# Run tests
npm test

# If all pass, merge to main
git checkout main
git merge feature/user-auth
```

**Feature complete!** 🎉

---

## Common Patterns

### Pattern 1: Handling Blockers

**Scenario**: Frontend is blocked waiting for backend to define a type.

**Agent reports blocker:**
```json
{
  "agent_id": "frontend-dev",
  "blockers": [
    {
      "description": "Need Product type definition to build product list UI",
      "blocking_agent": "backend-dev",
      "severity": "high"
    }
  ]
}
```

**Your action:**
1. Switch to backend agent session
2. Tell backend: "Frontend needs Product type definition (see their blocker in team-communication.json)"
3. Backend creates the type
4. Backend updates file with type location
5. Switch back to frontend
6. Tell frontend: "Product type is now available in src/types/product.ts"

---

### Pattern 2: Manager Makes a Decision

**Scenario**: Two agents have conflicting approaches, need manager decision.

**Backend suggests:** "Use PostgreSQL for user storage"
**Frontend suggests:** "Use Firebase for user storage"

**You bring both perspectives to Manager:**
```
YOU: Backend suggests PostgreSQL, Frontend suggests Firebase.
     Please review both options and make a decision.
```

**Manager:**
1. Evaluates both options
2. Makes decision with rationale
3. Updates communication file:

```json
{
  "decisions": [
    {
      "decision": "Use PostgreSQL for user storage",
      "rationale": "Better for complex queries, more control over data, team has PostgreSQL experience",
      "alternatives_considered": ["Firebase"],
      "affected_agents": ["backend-dev", "frontend-dev"],
      "action_items": [
        "backend-dev: Set up PostgreSQL schema",
        "frontend-dev: Use REST API (no Firebase SDK needed)"
      ]
    }
  ]
}
```

---

### Pattern 3: Parallel Work with Dependencies

**Scenario**: Frontend needs backend API, but we want to work in parallel.

**Solution**: Use API contract as interface.

**Manager creates contract first:**
```json
{
  "shared_resources": {
    "api_contracts": [
      {
        "endpoint": "/api/products",
        "file": ".ai-agents/context/api-contracts.md#products-api",
        "status": "approved",
        "version": "1.0.0"
      }
    ]
  }
}
```

**Backend and Frontend work simultaneously:**
- Backend implements real API
- Frontend uses mock API matching the contract
- Both reference the same contract
- Integration happens after both complete

---

### Pattern 4: Knowledge Sharing

**Scenario**: Agent discovers something useful for others.

**Agent shares in update:**
```json
{
  "agent_id": "backend-dev",
  "message": "Discovered useful pattern for error handling",
  "available_for_other_agents": [
    "Error handling utilities in src/utils/errors.ts",
    "See examples in src/controllers/auth.ts for usage"
  ]
}
```

**You relay to other agents:**
```
YOU (to frontend-dev): Backend has created error handling utilities
                       in src/utils/errors.ts that you can use.
```

---

## Troubleshooting

### Problem: Agents not reading communication file

**Symptom**: Agent starts working without checking assigned tasks.

**Solution**:
1. Be explicit: "Before you start, read .ai-agents/state/team-communication.json"
2. Ensure communication-protocol.md is in agent's project_context
3. Ask agent: "What task is assigned to you according to the communication file?"

---

### Problem: Agents overwriting each other's updates

**Symptom**: Agent updates disappear when another agent writes.

**Solution**:
1. Tell agents to append to the array, not replace it
2. Use this prompt: "Read the current file, then add your update to the agent_updates array without removing existing entries"
3. Review the file between sessions to ensure nothing was lost

---

### Problem: Too much back-and-forth between agents

**Symptom**: Spending too much time relaying messages.

**Solution**:
1. Have manager create comprehensive initial plan
2. Use API contracts to reduce dependencies
3. Let agents work longer before checking in
4. Batch multiple questions/updates together

---

### Problem: Communication file getting too large

**Symptom**: File is thousands of lines, hard to navigate.

**Solution**:
1. Archive old updates:
   ```bash
   # Move completed feature updates to archive
   mv .ai-agents/state/team-communication.json \
      .ai-agents/state/archive/auth-feature-communication.json

   # Start fresh
   cp .ai-agents/state/team-communication-template.json \
      .ai-agents/state/team-communication.json
   ```
2. Keep only active/recent updates in main file
3. Completed tasks can be moved to completed_tasks array

---

### Problem: Agent doesn't understand their task

**Symptom**: Agent asks too many questions or goes off-track.

**Solution**:
1. Go back to manager
2. Ask manager to provide more detailed task description
3. Manager should include:
   - Specific deliverables
   - Acceptance criteria
   - Reference examples
   - Related context files

---

## Advanced Techniques

### Technique 1: Time-Boxing Sessions

Limit agent sessions to focused time blocks:

```
YOU: You have 1 hour to make as much progress as possible on TASK-001.
     Update the communication file every 30 minutes with your progress.
```

**Benefits:**
- Keeps agents focused
- Regular progress updates
- Prevents scope creep

---

### Technique 2: Pre-Planning with Manager

Before any coding, do thorough planning:

```
YOU: Please create a detailed implementation plan for the shopping cart feature.
     Include:
     - Task breakdown with dependencies
     - API contracts
     - Type definitions
     - Acceptance criteria for each task
```

**Benefits:**
- Reduces blockers during implementation
- Agents have clear direction
- Parallel work is more effective

---

### Technique 3: Checkpoints and Reviews

Regular coordination points:

```
Schedule:
09:00 - Manager: Daily planning
10:00 - Agents: Implementation (2-3 hours)
13:00 - Manager: Mid-day review, unblock issues
14:00 - Agents: Continue implementation
16:00 - Manager: End-of-day integration
```

**Benefits:**
- Regular synchronization
- Early blocker detection
- Predictable workflow

---

### Technique 4: Graduated Autonomy

Start with more control, gradually give more autonomy:

**Week 1**: Check in after every 25% progress
**Week 2**: Check in after 50% progress
**Week 3**: Check in only when blocked or complete

**Benefits:**
- Build trust in agent capabilities
- Learn optimal check-in frequency
- Increase efficiency over time

---

## Summary

### Key Takeaways

1. **You are the coordinator** - embrace this role
2. **Communication file is central** - keep it updated
3. **Be explicit with prompts** - tell agents to read/update the file
4. **Manager creates structure** - detailed plans reduce blockers
5. **Regular check-ins** - find your rhythm
6. **Iterate and improve** - refine your process over time

### Success Checklist

✅ Communication file created and accessible
✅ Communication protocol added to agent contexts
✅ Agents instructed to read file at session start
✅ Agents updating file with progress/blockers
✅ Manager creating detailed task plans
✅ Regular coordination between agents via you
✅ Integration coordinated by manager

### Next Steps

1. **Try it**: Start with a small feature
2. **Learn**: Note what works and what doesn't
3. **Refine**: Adjust prompts and process
4. **Scale**: Add more agents as you get comfortable

**The human-coordinated approach is practical, powerful, and works today with any LLM tool. Start using it and see the benefits immediately!**

---

**Questions?** Check [README.md](README.md) for more information or see [examples/](examples/) for reference implementations.
