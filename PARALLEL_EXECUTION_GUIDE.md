# Parallel Agent Execution Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-20
**Purpose:** Maximize parallel execution efficiency in multi-agent systems

---

## Table of Contents

- [Overview](#overview)
- [Key Principles](#key-principles)
- [Task Decomposition Strategies](#task-decomposition-strategies)
- [Dependency Management](#dependency-management)
- [API Contract-Driven Development](#api-contract-driven-development)
- [Resource Locking Strategies](#resource-locking-strategies)
- [Manager Orchestration Patterns](#manager-orchestration-patterns)
- [Communication Protocols](#communication-protocols)
- [Examples](#examples)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)

---

## Overview

Parallel agent execution allows multiple agents to work simultaneously, dramatically reducing overall completion time. The key is maximizing parallelism while minimizing coordination overhead and conflicts.

### Potential Speedup

```
Sequential Execution:
Agent A: [====] 4 hours
Agent B:      [====] 4 hours
Agent C:           [====] 4 hours
Total: 12 hours

Parallel Execution:
Agent A: [====]
Agent B: [====]
Agent C: [====]
Total: 4 hours (3x speedup)

With Dependencies:
Agent A: [====]
Agent B:      [==]
Agent C: [====]
Total: 6 hours (2x speedup)
```

### Success Metrics

**Good Parallelization:**
- 50-80% of tasks run in parallel
- Minimal merge conflicts (<10%)
- Clear ownership boundaries
- Fast integration cycles

**Poor Parallelization:**
- Agents waiting on each other
- Frequent merge conflicts (>25%)
- Unclear ownership
- Long integration delays

---

## Key Principles

### 1. Independence Through Contracts

**Principle**: Define interfaces first, implement later.

```yaml
# Good: Contract-driven
Step 1: Define API contract (1 hour)
Step 2: Backend + Frontend + Tests work in parallel (4 hours)
Total: 5 hours

# Bad: Sequential dependencies
Step 1: Backend implements API (4 hours)
Step 2: Frontend uses real API (4 hours)
Step 3: Tests validate (2 hours)
Total: 10 hours
```

### 2. Clear Ownership Boundaries

**Principle**: Each agent owns distinct code areas.

```
Good Ownership:
├── Agent A: src/api/auth/*           ← Clear boundary
├── Agent B: src/components/auth/*    ← Clear boundary
└── Agent C: tests/auth/*             ← Clear boundary

Bad Ownership:
├── Agent A: src/auth/* (everything)  ← Overlapping
├── Agent B: src/auth/* (everything)  ← Overlapping
└── Agent C: src/auth/* (everything)  ← Overlapping
```

### 3. Minimize Shared Resources

**Principle**: Reduce files that multiple agents need to modify.

```typescript
// Bad: Shared file everyone modifies
// src/types/index.ts
export interface User { ... }
export interface Product { ... }
export interface Order { ... }
// Every agent needs to modify this!

// Good: Separate files per domain
// src/types/user.ts    ← Agent A owns
// src/types/product.ts ← Agent B owns
// src/types/order.ts   ← Agent C owns
```

### 4. Late Integration

**Principle**: Work in isolation, integrate when complete.

```
Good:
├── Agents work on branches for 2-3 days
├── Each reaches "done" state independently
└── Manager merges all at once

Bad:
├── Agents constantly merging to see others' changes
├── Frequent conflicts
└── Constant context switching
```

### 5. Progressive Dependencies

**Principle**: Structure work so later tasks can start before earlier ones finish.

```
Task Graph (Good):
[A: Design API] ──┐
                  ├──> [D: Integration Tests]
[B: Build UI] ────┤
                  │
[C: Write Docs] ──┘

A, B, C run in parallel (use contracts)
D waits for all three (needs real implementation)
```

---

## Task Decomposition Strategies

### Strategy 1: Vertical Slicing (By Feature)

**When to use**: Large features with multiple components

**Example**: User Authentication Feature

```yaml
Feature: User Authentication

# Vertical slices (can run in parallel):
Slice 1: "Backend API"
  - Agent: Backend Developer
  - Scope: API endpoints, JWT service, database
  - Branch: feature/auth/agent/backend-dev/api
  - Duration: 8 hours

Slice 2: "Web UI"
  - Agent: Frontend Developer
  - Scope: Login form, auth context, protected routes
  - Branch: feature/auth/agent/frontend-dev/ui
  - Duration: 6 hours

Slice 3: "Mobile UI"
  - Agent: Mobile Developer
  - Scope: Login screen, secure storage, auth flow
  - Branch: feature/auth/agent/mobile-dev/ui
  - Duration: 8 hours

Slice 4: "API Documentation"
  - Agent: Technical Writer
  - Scope: API docs, integration guide
  - Branch: feature/auth/agent/tech-writer/docs
  - Duration: 4 hours

# Dependencies: All use API contract, can work in parallel
# Parallelism: 4 agents working simultaneously
# Total Time: 8 hours (vs 26 hours sequential)
```

### Strategy 2: Horizontal Slicing (By Layer)

**When to use**: Infrastructure changes, cross-cutting concerns

**Example**: Add Logging Infrastructure

```yaml
Feature: Logging Infrastructure

# Horizontal slices (can run in parallel):
Slice 1: "Backend Logging"
  - Agent: Backend Developer
  - Scope: Winston setup, log middleware, structured logging
  - Branch: feature/logging/agent/backend-dev/implementation
  - Duration: 4 hours

Slice 2: "Frontend Logging"
  - Agent: Frontend Developer
  - Scope: Browser logging, error tracking, user events
  - Branch: feature/logging/agent/frontend-dev/implementation
  - Duration: 4 hours

Slice 3: "Log Aggregation"
  - Agent: DevOps Engineer
  - Scope: ELK stack, log shipping, dashboards
  - Branch: feature/logging/agent/devops/aggregation
  - Duration: 6 hours

Slice 4: "Logging Standards Doc"
  - Agent: Architect
  - Scope: Logging standards, best practices, examples
  - Branch: feature/logging/agent/architect/standards
  - Duration: 3 hours

# Dependencies: Standards doc informs implementations
# Strategy: Architect creates standards first (3h), others follow (4-6h)
# Total Time: 9 hours (vs 17 hours sequential)
```

### Strategy 3: Component Isolation

**When to use**: Independent components with clear boundaries

**Example**: E-commerce Cart System

```yaml
Feature: Shopping Cart

# Independent components (fully parallel):
Component 1: "Cart Service"
  - Agent: Backend Developer A
  - Scope: Cart CRUD, persistence, business logic
  - Dependencies: None (uses type contracts)
  - Duration: 8 hours

Component 2: "Cart UI"
  - Agent: Frontend Developer
  - Scope: Cart display, item management, UI state
  - Dependencies: Cart service contract
  - Duration: 6 hours

Component 3: "Cart Analytics"
  - Agent: Backend Developer B
  - Scope: Cart events, metrics, tracking
  - Dependencies: Cart service contract
  - Duration: 4 hours

Component 4: "Cart Tests"
  - Agent: QA Tester
  - Scope: Unit tests, integration tests, E2E tests
  - Dependencies: Component contracts
  - Duration: 6 hours

# All components use contracts, 100% parallel
# Total Time: 8 hours (vs 24 hours sequential)
```

### Strategy 4: Dependency-Ordered Tasks

**When to use**: Tasks with hard dependencies

**Example**: Database Migration Feature

```yaml
Feature: Database Schema Update

# Must be ordered, but can optimize:
Phase 1: "Schema Design" (cannot parallelize)
  - Agent: Architect
  - Scope: Design new schema, migration strategy
  - Duration: 4 hours

Phase 2: "Parallel Implementation" (can parallelize)
  Task 2a: "Migration Scripts"
    - Agent: Backend Developer A
    - Scope: Alembic migrations, data transformations
    - Duration: 6 hours

  Task 2b: "Model Updates"
    - Agent: Backend Developer B
    - Scope: ORM models, repositories
    - Duration: 4 hours

  Task 2c: "API Updates"
    - Agent: Backend Developer C
    - Scope: Update API to use new schema
    - Duration: 5 hours

Phase 3: "Testing" (can partially parallelize)
  Task 3a: "Migration Testing"
    - Agent: QA Tester A
    - Scope: Test migration scripts, rollback
    - Duration: 3 hours

  Task 3b: "API Testing"
    - Agent: QA Tester B
    - Scope: Test API with new schema
    - Duration: 3 hours

# Timeline:
# 0-4h: Phase 1 (1 agent)
# 4-10h: Phase 2 (3 agents in parallel)
# 10-13h: Phase 3 (2 agents in parallel)
# Total: 13 hours (vs 25 hours sequential)
```

---

## Dependency Management

### Dependency Types

#### 1. Hard Dependencies (Sequential)

**Definition**: Task B cannot start until Task A completes.

```yaml
Example: Database Migration
Task A: Create migration script (must complete first)
Task B: Test migration (depends on A)

Strategy: Must be sequential
Timeline:
  0-4h: Task A
  4-7h: Task B
```

#### 2. Soft Dependencies (Contract-Based)

**Definition**: Task B needs Task A's interface, not implementation.

```yaml
Example: API Integration
Task A: Implement /api/auth endpoint
Task B: Build login UI that calls /api/auth

Strategy: Use API contract to parallelize
Timeline:
  0h: Define API contract (30 min)
  0-4h: Task A (implement real API)
  0-4h: Task B (use contract, mock API)
```

#### 3. Information Dependencies

**Definition**: Task B needs information from Task A, but not the implementation.

```yaml
Example: Design + Implementation
Task A: Design system architecture
Task B: Implement backend based on design

Strategy: Share design early, implement in parallel
Timeline:
  0-2h: Task A creates design doc (draft)
  2-8h: Task B starts implementing based on draft
  2-4h: Task A finalizes design (parallel with B)
```

#### 4. No Dependencies (Fully Parallel)

**Definition**: Tasks are completely independent.

```yaml
Example: Multiple Features
Task A: Implement feature X
Task B: Implement feature Y

Strategy: Full parallelization
Timeline:
  0-6h: Task A and B run simultaneously
```

### Dependency Graph Analysis

**Tools for Manager Agent:**

```python
class DependencyGraph:
    def __init__(self):
        self.tasks = {}
        self.dependencies = {}

    def add_task(self, task_id, agent, duration, depends_on=None):
        self.tasks[task_id] = {
            "agent": agent,
            "duration": duration,
            "depends_on": depends_on or []
        }

    def find_parallelizable_tasks(self):
        """Find all tasks that can run in parallel"""
        # Tasks with no dependencies can start immediately
        ready = [
            task_id for task_id, task in self.tasks.items()
            if not task["depends_on"]
        ]
        return ready

    def get_critical_path(self):
        """Find longest dependency chain (bottleneck)"""
        # Use topological sort + longest path algorithm
        return self._longest_path()

    def optimize_schedule(self, available_agents):
        """Create optimal schedule given agent availability"""
        schedule = []
        time = 0
        completed = set()

        while len(completed) < len(self.tasks):
            # Find ready tasks
            ready = [
                task_id for task_id, task in self.tasks.items()
                if task_id not in completed
                and all(dep in completed for dep in task["depends_on"])
            ]

            # Assign to available agents
            assigned = 0
            for task_id in ready:
                if assigned >= available_agents:
                    break
                schedule.append({
                    "task": task_id,
                    "start": time,
                    "duration": self.tasks[task_id]["duration"]
                })
                assigned += 1

            # Advance time
            time += min(self.tasks[t]["duration"] for t in ready[:assigned])
            completed.update(ready[:assigned])

        return schedule

# Example usage:
graph = DependencyGraph()

# User authentication feature
graph.add_task("TASK-001", "architect", 2, depends_on=[])  # Design
graph.add_task("TASK-002", "backend", 6, depends_on=["TASK-001"])  # API
graph.add_task("TASK-003", "frontend", 4, depends_on=["TASK-001"])  # UI
graph.add_task("TASK-004", "qa", 3, depends_on=["TASK-002", "TASK-003"])  # Tests

# Find what can run in parallel
ready = graph.find_parallelizable_tasks()  # ["TASK-001"]

# Get optimal schedule
schedule = graph.optimize_schedule(available_agents=3)
# Result:
# 0-2h: TASK-001 (architect)
# 2-8h: TASK-002 (backend) + TASK-003 (frontend) [parallel]
# 8-11h: TASK-004 (qa)
# Total: 11 hours vs 15 hours sequential
```

---

## API Contract-Driven Development

### Why Contracts Enable Parallelism

**Without Contracts (Sequential):**
```
Backend implements API → Frontend uses API → Tests validate
(4 hours)              (4 hours)          (2 hours)
Total: 10 hours
```

**With Contracts (Parallel):**
```
Define contract → Backend + Frontend + Tests work in parallel
(30 minutes)     (4 hours)
Total: 4.5 hours
```

### Contract Definition Template

```markdown
# API Contract: Authentication Endpoints

**Version:** 1.0.0
**Status:** Approved ✓
**Owner:** backend-dev-001
**Consumers:** frontend-dev-001, mobile-dev-001, qa-tester-001

---

## POST /api/auth/login

**Purpose**: Authenticate user and return JWT token

### Request

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "email": "string (email format, required)",
  "password": "string (min 8 chars, required)"
}
```

**Example:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Response (Success - 200 OK)

```json
{
  "token": "string (JWT token)",
  "expiresAt": "string (ISO 8601 datetime)",
  "user": {
    "id": "string (UUID)",
    "email": "string",
    "name": "string",
    "roles": ["string"]
  }
}
```

**Example:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2025-11-21T12:00:00Z",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["user"]
  }
}
```

### Response (Error - 401 Unauthorized)

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

**Error Codes:**
- `INVALID_CREDENTIALS`: Email/password combination incorrect
- `ACCOUNT_LOCKED`: Account locked due to multiple failed attempts
- `ACCOUNT_DISABLED`: Account has been disabled

**Example:**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {
      "remainingAttempts": 2
    }
  }
}
```

### Response (Error - 400 Bad Request)

**Validation errors:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "fields": {
        "email": ["Invalid email format"],
        "password": ["Password must be at least 8 characters"]
      }
    }
  }
}
```

### Mock Implementation

**For development/testing:**

```typescript
// mock-auth-api.ts
export const mockLogin = (email: string, password: string) => {
  // Always succeeds in dev mode
  if (password === "test123") {
    return {
      token: "mock-jwt-token-123",
      expiresAt: new Date(Date.now() + 3600000).toISOString(),
      user: {
        id: "mock-user-id",
        email: email,
        name: "Test User",
        roles: ["user"]
      }
    };
  }

  throw {
    error: {
      code: "INVALID_CREDENTIALS",
      message: "Invalid email or password",
      details: { remainingAttempts: 3 }
    }
  };
};
```

### Testing Contract

```typescript
// contract-tests.ts
describe("Auth API Contract", () => {
  it("POST /api/auth/login returns token on success", async () => {
    const response = await api.post("/api/auth/login", {
      email: "test@example.com",
      password: "ValidPass123!"
    });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("token");
    expect(response.body).toHaveProperty("expiresAt");
    expect(response.body).toHaveProperty("user");
    expect(response.body.user).toHaveProperty("id");
    expect(response.body.user).toHaveProperty("email");
  });

  it("POST /api/auth/login returns 401 on invalid credentials", async () => {
    const response = await api.post("/api/auth/login", {
      email: "test@example.com",
      password: "WrongPassword"
    });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe("INVALID_CREDENTIALS");
  });
});
```

### Implementation Checklist

**Backend Developer:**
- [ ] Implement endpoint according to contract
- [ ] Validate request format
- [ ] Return responses matching contract exactly
- [ ] Handle all error cases specified
- [ ] Run contract tests

**Frontend Developer:**
- [ ] Use mock API during development
- [ ] Handle success response
- [ ] Handle all error cases
- [ ] Display appropriate messages
- [ ] Run contract tests with mock

**QA Tester:**
- [ ] Verify contract tests pass with real API
- [ ] Test all success scenarios
- [ ] Test all error scenarios
- [ ] Verify response format matches contract
- [ ] Test edge cases

---

## Resource Locking Strategies

### Lock Types

#### 1. Exclusive Lock (Full Ownership)

**Use case**: Major refactoring of a file

```json
{
  "shared_resources": {
    "src/types/User.ts": {
      "lock_type": "exclusive",
      "owner": "backend-dev-001",
      "locked_at": "2025-11-20T10:00:00Z",
      "reason": "Adding authentication fields",
      "estimated_release": "2025-11-20T14:00:00Z"
    }
  }
}
```

**Behavior:**
- Only owner can modify file
- Other agents must wait
- Used sparingly

#### 2. Shared Lock (Read Access)

**Use case**: Multiple agents reading same file

```json
{
  "shared_resources": {
    "src/types/User.ts": {
      "lock_type": "shared",
      "holders": ["frontend-dev-001", "mobile-dev-001"],
      "locked_at": "2025-11-20T10:00:00Z"
    }
  }
}
```

**Behavior:**
- Multiple agents can read
- No one can write
- Converts to exclusive for writes

#### 3. Intent Lock (Planning Modification)

**Use case**: Agent plans to modify soon

```json
{
  "shared_resources": {
    "src/types/User.ts": {
      "lock_type": "intent",
      "intenders": {
        "backend-dev-001": {
          "intent": "Add lastLoginAt field",
          "priority": "high",
          "requested_at": "2025-11-20T10:00:00Z"
        },
        "backend-dev-002": {
          "intent": "Add roles array",
          "priority": "medium",
          "requested_at": "2025-11-20T10:30:00Z"
        }
      }
    }
  }
}
```

**Behavior:**
- Agents declare intent before actual modification
- Manager coordinates to batch changes
- Reduces conflicts

#### 4. No Lock (Free Access)

**Use case**: Agent-specific files

```json
{
  "src/components/LoginForm.tsx": {
    "lock_type": "none",
    "owner": "frontend-dev-001",
    "note": "Frontend dev exclusive area"
  }
}
```

**Behavior:**
- No locking needed
- Clear ownership
- Rarely conflicts

### Lock Management Protocol

#### Requesting Lock

```json
{
  "type": "lock_request",
  "agent_id": "backend-dev-001",
  "task_id": "TASK-002",
  "resource": "src/types/User.ts",
  "lock_type": "exclusive",
  "reason": "Adding authentication fields",
  "estimated_duration": "4 hours",
  "priority": "high",
  "timestamp": "2025-11-20T10:00:00Z"
}
```

#### Granting Lock

```json
{
  "type": "lock_granted",
  "agent_id": "backend-dev-001",
  "resource": "src/types/User.ts",
  "lock_type": "exclusive",
  "granted_at": "2025-11-20T10:00:00Z",
  "expires_at": "2025-11-20T14:00:00Z",
  "lock_id": "lock-12345"
}
```

#### Releasing Lock

```json
{
  "type": "lock_release",
  "agent_id": "backend-dev-001",
  "lock_id": "lock-12345",
  "resource": "src/types/User.ts",
  "timestamp": "2025-11-20T13:30:00Z",
  "changes_made": true
}
```

#### Lock Conflict

```json
{
  "type": "lock_denied",
  "agent_id": "backend-dev-002",
  "resource": "src/types/User.ts",
  "reason": "Resource locked by backend-dev-001",
  "current_lock": {
    "owner": "backend-dev-001",
    "lock_type": "exclusive",
    "estimated_release": "2025-11-20T14:00:00Z"
  },
  "alternatives": [
    "Wait for lock release",
    "Work on different file",
    "Coordinate with lock owner for batched changes"
  ]
}
```

### Automated Lock Manager

```python
class LockManager:
    def __init__(self):
        self.locks = {}
        self.lock_queue = {}

    def request_lock(self, agent_id, resource, lock_type, duration):
        """Request lock on resource"""

        # Check if resource is already locked
        if resource in self.locks:
            current_lock = self.locks[resource]

            # Shared locks can be granted to multiple agents
            if current_lock["type"] == "shared" and lock_type == "shared":
                current_lock["holders"].append(agent_id)
                return {"granted": True, "lock_id": current_lock["id"]}

            # Exclusive lock blocks others
            else:
                # Add to queue
                if resource not in self.lock_queue:
                    self.lock_queue[resource] = []

                self.lock_queue[resource].append({
                    "agent_id": agent_id,
                    "lock_type": lock_type,
                    "requested_at": datetime.now()
                })

                return {
                    "granted": False,
                    "reason": f"Locked by {current_lock['owner']}",
                    "estimated_wait": self._estimate_wait_time(resource),
                    "alternatives": self._suggest_alternatives(agent_id, resource)
                }

        # Grant lock
        lock_id = f"lock-{uuid.uuid4()}"
        self.locks[resource] = {
            "id": lock_id,
            "type": lock_type,
            "owner": agent_id if lock_type == "exclusive" else None,
            "holders": [agent_id] if lock_type == "shared" else [],
            "granted_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=duration)
        }

        return {"granted": True, "lock_id": lock_id}

    def release_lock(self, agent_id, lock_id):
        """Release lock and process queue"""

        # Find resource by lock_id
        resource = self._find_resource_by_lock(lock_id)
        if not resource:
            return {"error": "Lock not found"}

        # Release lock
        del self.locks[resource]

        # Process queue
        if resource in self.lock_queue and self.lock_queue[resource]:
            next_request = self.lock_queue[resource].pop(0)
            self.request_lock(
                next_request["agent_id"],
                resource,
                next_request["lock_type"],
                duration=4  # Default
            )

        return {"released": True}

    def suggest_alternatives(self, agent_id, blocked_resource):
        """Suggest alternative resources agent can work on"""

        # Get agent's task list
        agent_tasks = self._get_agent_tasks(agent_id)

        # Find tasks with unlocked resources
        alternatives = []
        for task in agent_tasks:
            if task["resource"] not in self.locks:
                alternatives.append(task)

        return alternatives
```

---

## Manager Orchestration Patterns

### Pattern 1: Parallel Task Assignment

**Scenario**: Multiple independent tasks

```python
def assign_parallel_tasks(self, feature):
    """Assign all parallelizable tasks at once"""

    # Identify tasks with no dependencies
    ready_tasks = [
        task for task in feature.tasks
        if not task.depends_on
    ]

    # Assign to available agents simultaneously
    assignments = []
    for task in ready_tasks:
        agent = self.find_available_agent(task.required_role)
        if agent:
            assignment = {
                "type": "task_assignment",
                "task_id": task.id,
                "assigned_to": agent.id,
                "branch": f"{feature.branch}/agent/{agent.role}/{task.id}",
                "priority": "parallel_batch_1",
                "start_immediately": True
            }
            assignments.append(assignment)
            self.send_to_agent(agent, assignment)

    return assignments

# Example:
# User authentication feature
tasks = [
    Task("TASK-002", "Implement API", role="backend", depends_on=["TASK-001"]),
    Task("TASK-003", "Build UI", role="frontend", depends_on=["TASK-001"]),
    Task("TASK-004", "Write docs", role="tech-writer", depends_on=["TASK-001"]),
]

# After TASK-001 completes:
manager.assign_parallel_tasks(feature)
# → TASK-002, TASK-003, TASK-004 all start simultaneously
```

### Pattern 2: Pipeline Execution

**Scenario**: Tasks with dependency chains

```python
def execute_pipeline(self, feature):
    """Execute tasks in pipeline with maximum parallelism"""

    completed = set()

    while len(completed) < len(feature.tasks):
        # Find ready tasks
        ready = [
            task for task in feature.tasks
            if task.id not in completed
            and all(dep in completed for dep in task.depends_on)
        ]

        if not ready:
            # Wait for at least one task to complete
            self.wait_for_any_completion()
            continue

        # Assign all ready tasks in parallel
        for task in ready:
            agent = self.find_available_agent(task.required_role)
            self.assign_task(agent, task)

        # Wait for this batch to complete
        completed_batch = self.wait_for_batch_completion(ready)
        completed.update(completed_batch)

    return completed

# Example pipeline:
# TASK-001: Design (no deps)
# TASK-002: Backend (deps: TASK-001)
# TASK-003: Frontend (deps: TASK-001)
# TASK-004: Tests (deps: TASK-002, TASK-003)

# Execution:
# Batch 1: TASK-001 (1 agent)
# Batch 2: TASK-002, TASK-003 (2 agents in parallel)
# Batch 3: TASK-004 (1 agent)
```

### Pattern 3: Dynamic Work Stealing

**Scenario**: Agents finish at different times

```python
def enable_work_stealing(self):
    """Allow idle agents to pick up work from queue"""

    while self.has_pending_tasks():
        # Find idle agents
        idle_agents = [
            agent for agent in self.agents
            if agent.status == "idle"
        ]

        for agent in idle_agents:
            # Find highest priority task agent can do
            task = self.find_best_task_for_agent(agent)

            if task:
                self.assign_task(agent, task)
            else:
                # No suitable task, keep agent idle
                pass

        # Check for completed tasks
        self.poll_for_completions()

def find_best_task_for_agent(self, agent):
    """Find best task for agent to work on"""

    # Get ready tasks (deps satisfied)
    ready_tasks = self.get_ready_tasks()

    # Filter by agent capabilities
    suitable = [
        task for task in ready_tasks
        if agent.can_handle(task.required_role)
    ]

    if not suitable:
        return None

    # Sort by priority
    suitable.sort(key=lambda t: (t.priority, t.estimated_duration))

    return suitable[0]
```

### Pattern 4: Batch Integration

**Scenario**: Multiple agents completing around same time

```python
def batch_integration(self, feature):
    """Integrate multiple agent branches at once"""

    # Wait for all agents to reach "ready to merge" state
    ready_branches = []

    while len(ready_branches) < len(feature.agents):
        # Check each agent's status
        for agent in feature.agents:
            if agent.status == "ready_to_merge" and agent.branch not in ready_branches:
                ready_branches.append(agent.branch)

        # If most agents are ready (80%), proceed
        if len(ready_branches) >= len(feature.agents) * 0.8:
            break

        time.sleep(60)  # Check every minute

    # Merge all branches in dependency order
    merge_order = self.determine_merge_order(ready_branches)

    for branch in merge_order:
        result = self.merge_branch(feature.branch, branch)

        if result.has_conflicts:
            # Coordinate conflict resolution
            self.coordinate_conflict_resolution(branch, result.conflicts)

        if not result.tests_pass:
            # Agent must fix
            self.request_fixes(branch, result.failures)

    return {"merged": len(merge_order)}

# Example:
# 3 agents working on feature
# Agent A completes at 2:00 PM
# Agent B completes at 2:10 PM
# Agent C completes at 2:15 PM
#
# Manager waits until 2:15 PM (all ready)
# Then merges all 3 branches in sequence
# Total integration time: 30 minutes
# vs. merging one at a time as they complete: 45+ minutes
```

---

## Communication Protocols

### Status Updates (Regular Heartbeat)

```json
{
  "type": "status_update",
  "agent_id": "backend-dev-001",
  "task_id": "TASK-002",
  "status": "in_progress",
  "progress": 65,
  "completed_items": [
    "JWT service implemented",
    "Auth middleware created",
    "User model updated"
  ],
  "current_item": "Writing tests for JWT service",
  "next_items": [
    "Create auth controller",
    "Add API endpoints"
  ],
  "estimated_completion": "2025-11-20T16:00:00Z",
  "blockers": [],
  "timestamp": "2025-11-20T14:30:00Z"
}
```

**Frequency**: Every 25% progress or hourly, whichever is more frequent

### Blocker Reports (Immediate)

```json
{
  "type": "blocker",
  "agent_id": "frontend-dev-001",
  "task_id": "TASK-003",
  "blocker_description": "API endpoint /api/auth/login returns 404",
  "severity": "high",
  "blocking_agent": "backend-dev-001",
  "can_proceed_with_workaround": true,
  "workaround": "Using mock API for now, but need real endpoint for testing",
  "needs_resolution_by": "2025-11-20T16:00:00Z",
  "impact": "Cannot complete integration tests",
  "timestamp": "2025-11-20T14:45:00Z"
}
```

**Trigger**: Immediately when blocker detected

### Coordination Requests

```json
{
  "type": "coordination_request",
  "from_agent": "frontend-dev-001",
  "to_agent": "backend-dev-001",
  "regarding": "User type definition",
  "request": "Can we add 'avatarUrl' field to User type?",
  "urgency": "medium",
  "current_state": "I need avatar for profile page",
  "proposed_solution": "Add 'avatarUrl?: string' to User interface",
  "timeline": "Need by 2025-11-20T17:00:00Z",
  "timestamp": "2025-11-20T15:00:00Z"
}
```

### Completion Notifications

```json
{
  "type": "task_complete",
  "agent_id": "backend-dev-001",
  "task_id": "TASK-002",
  "branch": "feature/auth/agent/backend-dev/api",
  "completion_time": "2025-11-20T16:00:00Z",
  "summary": "Implemented JWT authentication API",
  "deliverables": [
    "JWT service (src/services/jwt.ts)",
    "Auth controller (src/controllers/auth.ts)",
    "Auth middleware (src/middleware/auth.ts)",
    "Unit tests (tests/auth.test.ts)"
  ],
  "test_results": {
    "passed": 24,
    "failed": 0,
    "coverage": 95
  },
  "ready_for_review": true,
  "ready_for_merge": true,
  "notes": "All tests passing, ready for integration",
  "timestamp": "2025-11-20T16:00:00Z"
}
```

---

## Examples

### Example 1: E-Commerce Feature (Good Parallelization)

**Feature**: Shopping Cart System

**Task Breakdown:**
```yaml
TASK-001: "Design Cart Data Model"
  - Agent: Architect
  - Duration: 2 hours
  - Dependencies: None
  - Output: Data model spec, API contract

TASK-002: "Implement Cart API"
  - Agent: Backend Developer A
  - Duration: 6 hours
  - Dependencies: TASK-001 (contract only)
  - Parallelizable: Yes (uses contract)

TASK-003: "Build Cart UI"
  - Agent: Frontend Developer
  - Duration: 5 hours
  - Dependencies: TASK-001 (contract only)
  - Parallelizable: Yes (uses contract)

TASK-004: "Add Cart Analytics"
  - Agent: Backend Developer B
  - Duration: 4 hours
  - Dependencies: TASK-001 (contract only)
  - Parallelizable: Yes (uses contract)

TASK-005: "Write Tests"
  - Agent: QA Tester
  - Duration: 4 hours
  - Dependencies: TASK-001 (contract only)
  - Parallelizable: Yes (uses mock)

TASK-006: "Integration Testing"
  - Agent: QA Tester
  - Duration: 2 hours
  - Dependencies: TASK-002, TASK-003, TASK-004, TASK-005
  - Parallelizable: No (needs all implementations)
```

**Timeline:**
```
0-2h:  TASK-001 (Architect) [1 agent]
2-8h:  TASK-002, TASK-003, TASK-004, TASK-005 [4 agents in parallel]
8-10h: TASK-006 (QA) [1 agent]

Total: 10 hours
Sequential would be: 23 hours
Speedup: 2.3x
```

**Key Success Factors:**
- ✅ Clear API contract defined upfront
- ✅ Agents work independently using contract
- ✅ Mock implementations for testing
- ✅ Only integration at the end needs coordination
- ✅ Clear ownership boundaries (no file conflicts)

### Example 2: Authentication Refactor (Mixed Parallelization)

**Feature**: Migrate from Session to JWT Auth

**Task Breakdown:**
```yaml
TASK-001: "Design JWT Architecture"
  - Agent: Architect
  - Duration: 3 hours
  - Dependencies: None
  - Output: Architecture doc, migration strategy

TASK-002: "Implement JWT Service"
  - Agent: Backend Developer A
  - Duration: 4 hours
  - Dependencies: TASK-001
  - Parallelizable: No (needs architecture)

TASK-003: "Update Auth Middleware"
  - Agent: Backend Developer B
  - Duration: 3 hours
  - Dependencies: TASK-002 (needs JWT service)
  - Parallelizable: No (hard dependency)

TASK-004: "Update Frontend Auth"
  - Agent: Frontend Developer
  - Duration: 5 hours
  - Dependencies: TASK-001 (contract), TASK-002 (implementation)
  - Parallelizable: Partial (can start with contract)

TASK-005: "Update Mobile Auth"
  - Agent: Mobile Developer
  - Duration: 5 hours
  - Dependencies: TASK-001 (contract), TASK-002 (implementation)
  - Parallelizable: Partial (can start with contract)

TASK-006: "Migration Script"
  - Agent: Backend Developer A
  - Duration: 3 hours
  - Dependencies: TASK-002
  - Parallelizable: Partial (can design in parallel with TASK-002)

TASK-007: "Testing"
  - Agent: QA Tester
  - Duration: 4 hours
  - Dependencies: All above
  - Parallelizable: No (needs everything)
```

**Timeline:**
```
0-3h:   TASK-001 (Architect) [1 agent]
3-7h:   TASK-002 (Backend A) + TASK-004/005 start with contract [3 agents]
7-10h:  TASK-003 (Backend B) + TASK-006 (Backend A) + TASK-004/005 finish [4 agents]
10-14h: TASK-007 (QA) [1 agent]

Total: 14 hours
Sequential would be: 27 hours
Speedup: 1.9x
```

**Key Success Factors:**
- ✅ Contract allows early start on frontend/mobile
- ✅ Backend work has some dependencies but optimized
- ✅ Migration script design can happen in parallel
- ⚠️ Some hard dependencies limit parallelism

### Example 3: Database Migration (Poor Parallelization - Unavoidable)

**Feature**: Add User Roles and Permissions

**Task Breakdown:**
```yaml
TASK-001: "Design Schema Changes"
  - Agent: Architect
  - Duration: 3 hours
  - Dependencies: None
  - Parallelizable: No (foundational)

TASK-002: "Create Migration Scripts"
  - Agent: Backend Developer A
  - Duration: 4 hours
  - Dependencies: TASK-001 (needs exact schema)
  - Parallelizable: No (hard dependency)

TASK-003: "Test Migration on Staging"
  - Agent: DevOps Engineer
  - Duration: 2 hours
  - Dependencies: TASK-002 (needs scripts)
  - Parallelizable: No (hard dependency)

TASK-004: "Update ORM Models"
  - Agent: Backend Developer B
  - Duration: 3 hours
  - Dependencies: TASK-002 (needs migrated schema)
  - Parallelizable: No (hard dependency)

TASK-005: "Update API Layer"
  - Agent: Backend Developer C
  - Duration: 4 hours
  - Dependencies: TASK-004 (needs models)
  - Parallelizable: No (hard dependency)

TASK-006: "Update Frontend"
  - Agent: Frontend Developer
  - Duration: 5 hours
  - Dependencies: TASK-005 (needs API changes)
  - Parallelizable: No (hard dependency)

TASK-007: "Full Integration Test"
  - Agent: QA Tester
  - Duration: 3 hours
  - Dependencies: All above
  - Parallelizable: No (final validation)
```

**Timeline:**
```
0-3h:   TASK-001 [1 agent]
3-7h:   TASK-002 [1 agent]
7-9h:   TASK-003 [1 agent]
9-12h:  TASK-004 [1 agent]
12-16h: TASK-005 [1 agent]
16-21h: TASK-006 [1 agent]
21-24h: TASK-007 [1 agent]

Total: 24 hours (fully sequential)
Speedup: 1.0x (no parallelization possible)
```

**Why Sequential?**
- Each task requires output of previous task
- Database changes are foundational
- Can't mock database schema changes
- Testing must happen in sequence

**Optimization Strategies:**
- Use feature flags to merge early
- Break into smaller, independent migrations
- Use API versioning to allow parallel UI work

---

## Anti-Patterns

### Anti-Pattern 1: False Parallelization

**Bad:**
```yaml
# Looks parallel, but isn't really
TASK-001: "Frontend Dev starts"
TASK-002: "Backend Dev starts"
# Both agents wait for shared design doc that doesn't exist yet
# Both blocked until design is done
# No actual parallelism
```

**Good:**
```yaml
TASK-001: "Create design doc and API contract" (2h)
TASK-002: "Frontend Dev uses contract" (starts at 2h)
TASK-003: "Backend Dev uses contract" (starts at 2h)
# Real parallelism after contract is ready
```

### Anti-Pattern 2: Over-Parallelization

**Bad:**
```yaml
# 10 agents working on same feature
# Too much coordination overhead
# Frequent merge conflicts
# Communication bottleneck
```

**Good:**
```yaml
# 3-5 agents per feature
# Clear boundaries
# Manageable coordination
# Optimal speedup without overhead
```

### Anti-Pattern 3: Shared File Hell

**Bad:**
```yaml
# All agents modify src/types/index.ts
Agent A: Add User type
Agent B: Add Product type
Agent C: Add Order type
Agent D: Update User type
# Constant conflicts on same file
```

**Good:**
```yaml
# Separate files per domain
Agent A: src/types/user.ts
Agent B: src/types/product.ts
Agent C: src/types/order.ts
# No conflicts
```

### Anti-Pattern 4: Premature Integration

**Bad:**
```yaml
# Agents merge incomplete work to "show progress"
# Main branch broken
# Other agents blocked
# Constant conflicts
```

**Good:**
```yaml
# Agents work on branches until "done"
# Merge complete, tested work
# Main branch always stable
# Integration happens in batch
```

### Anti-Pattern 5: Ignoring Dependencies

**Bad:**
```yaml
# Manager assigns all tasks at once without checking dependencies
TASK-002: Build UI (depends on TASK-001: API)
# Frontend agent blocked waiting for API
# Wasted time, frustrated agent
```

**Good:**
```yaml
# Manager checks dependencies first
# Assigns ready tasks only
# Or provides contracts for soft dependencies
```

---

## Best Practices

### 1. Start with Dependency Analysis

Before assigning tasks:
```python
# Manager's first step
def plan_feature_execution(self, feature):
    # 1. Build dependency graph
    graph = DependencyGraph()
    for task in feature.tasks:
        graph.add_task(task.id, task.agent, task.duration, task.depends_on)

    # 2. Find critical path (bottleneck)
    critical_path = graph.get_critical_path()
    print(f"Critical path: {critical_path} ({sum(t.duration for t in critical_path)} hours)")

    # 3. Identify parallelizable tasks
    parallel_tasks = graph.find_parallelizable_tasks()
    print(f"Can start immediately: {len(parallel_tasks)} tasks")

    # 4. Estimate completion time
    estimated_time = graph.estimate_completion_time(available_agents=5)
    print(f"Estimated completion: {estimated_time} hours")

    return graph
```

### 2. Define Contracts Early

```markdown
# Feature Kickoff Checklist

## Before Any Implementation:
- [ ] API contracts defined
- [ ] Data models specified
- [ ] Interface contracts documented
- [ ] Error handling specified
- [ ] Mock implementations available

## Contract Review:
- [ ] All consuming agents reviewed contracts
- [ ] Contracts are complete and unambiguous
- [ ] Mock implementations provided for testing
- [ ] Contract tests written

## Ready for Parallel Execution:
- [ ] All agents have what they need to start
- [ ] No blocking questions remaining
- [ ] Agents can work independently
```

### 3. Monitor Parallel Efficiency

```python
def measure_parallel_efficiency(self, feature):
    """Measure how well parallelism is working"""

    total_work_hours = sum(task.duration for task in feature.tasks)
    actual_elapsed_hours = feature.end_time - feature.start_time
    agent_count = len(feature.agents)

    # Ideal: perfect parallelism
    ideal_time = total_work_hours / agent_count

    # Efficiency: how close to ideal
    efficiency = (ideal_time / actual_elapsed_hours) * 100

    # Speedup: vs sequential
    sequential_time = sum(task.duration for task in feature.tasks)
    speedup = sequential_time / actual_elapsed_hours

    return {
        "total_work_hours": total_work_hours,
        "actual_elapsed_hours": actual_elapsed_hours,
        "ideal_time": ideal_time,
        "efficiency": f"{efficiency}%",
        "speedup": f"{speedup}x",
        "bottlenecks": self.identify_bottlenecks(feature)
    }

# Example output:
# {
#   "total_work_hours": 24,
#   "actual_elapsed_hours": 10,
#   "ideal_time": 6,  # 24 hours / 4 agents
#   "efficiency": "60%",  # Pretty good
#   "speedup": "2.4x",  # Good speedup
#   "bottlenecks": ["Initial design phase (sequential)", "Final integration testing (sequential)"]
# }
```

### 4. Use Work Stealing

```python
def implement_work_stealing(self):
    """Allow idle agents to help with other work"""

    @event_handler("agent_completed_task")
    def on_agent_complete(agent, task):
        # Agent just finished, look for more work

        # 1. Check agent's assigned tasks
        next_task = self.get_next_task_for_agent(agent)
        if next_task:
            self.assign_task(agent, next_task)
            return

        # 2. Look for work from other agents
        stealing_candidates = self.find_steal_candidates(agent)
        if stealing_candidates:
            stolen_task = stealing_candidates[0]
            self.reassign_task(stolen_task, agent)
            return

        # 3. No work available, mark idle
        agent.status = "idle"

def find_steal_candidates(self, idle_agent):
    """Find tasks that could be stolen from busy agents"""

    candidates = []

    # Look for agents with multiple tasks queued
    for agent in self.agents:
        if len(agent.queued_tasks) > 1:
            for task in agent.queued_tasks:
                # Can idle agent handle this task?
                if idle_agent.can_handle(task.required_role):
                    candidates.append(task)

    # Sort by priority and duration
    candidates.sort(key=lambda t: (t.priority, t.duration))

    return candidates
```

### 5. Batch Communication

```python
def batched_updates(self):
    """Batch status updates to reduce communication overhead"""

    # Instead of each agent sending updates immediately
    # Collect updates and send in batch

    update_buffer = []

    @periodic(interval=300)  # Every 5 minutes
    def send_batched_updates():
        if update_buffer:
            self.manager.process_batch_updates(update_buffer)
            update_buffer.clear()

    def agent_update(self, update):
        update_buffer.append(update)

        # Also send immediately if critical
        if update.get("severity") == "high":
            self.manager.process_update(update)
```

### 6. Visualize Parallel Execution

```python
def generate_gantt_chart(self, feature):
    """Create visual timeline of parallel execution"""

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot each task as a horizontal bar
    for i, task in enumerate(feature.tasks):
        start = task.start_time
        end = task.end_time
        duration = (end - start).total_seconds() / 3600  # hours

        ax.barh(i, duration, left=start, height=0.8,
                label=f"{task.id}: {task.title}",
                color=self.get_agent_color(task.agent))

    # Format
    ax.set_ylabel("Tasks")
    ax.set_xlabel("Time")
    ax.set_title(f"Parallel Execution Timeline: {feature.name}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"timeline-{feature.id}.png")

    return f"timeline-{feature.id}.png"
```

### 7. Celebrate Parallel Wins

```python
def report_parallel_success(self, feature):
    """Report on parallel execution success"""

    metrics = self.measure_parallel_efficiency(feature)

    message = f"""
    🎉 Feature Complete: {feature.name}

    📊 Parallel Execution Metrics:
    - Total work: {metrics['total_work_hours']} hours
    - Actual time: {metrics['actual_elapsed_hours']} hours
    - Speedup: {metrics['speedup']}
    - Efficiency: {metrics['efficiency']}

    👥 Agent Contributions:
    {self.list_agent_contributions(feature)}

    🚀 Time Saved: {metrics['total_work_hours'] - metrics['actual_elapsed_hours']} hours

    💡 Insights:
    {self.generate_insights(feature)}
    """

    self.broadcast(message)
```

---

## Summary

### Key Takeaways

1. **Contracts Enable Parallelism**
   - Define interfaces before implementation
   - Agents work independently using contracts
   - Integration validates contracts

2. **Clear Ownership Prevents Conflicts**
   - Each agent owns specific code areas
   - Minimize shared resources
   - Use resource locking when sharing is necessary

3. **Dependencies Limit Parallelism**
   - Analyze dependencies upfront
   - Break down work to minimize dependencies
   - Use soft dependencies (contracts) where possible

4. **Manager Orchestration is Critical**
   - Assign tasks based on dependency analysis
   - Monitor for blockers
   - Batch integration when possible

5. **Communication is Key**
   - Regular status updates
   - Immediate blocker reports
   - Coordination requests
   - Completion notifications

### Parallelization Checklist

**Before Starting:**
- [ ] Dependency graph created
- [ ] Critical path identified
- [ ] Parallelizable tasks identified
- [ ] Contracts defined
- [ ] Resource ownership clarified

**During Execution:**
- [ ] Monitor for blockers
- [ ] Track parallel efficiency
- [ ] Enable work stealing
- [ ] Batch communications
- [ ] Visualize progress

**After Completion:**
- [ ] Measure efficiency
- [ ] Identify bottlenecks
- [ ] Document lessons learned
- [ ] Celebrate successes
- [ ] Improve for next feature

---

**Remember**: The goal is maximum parallelism with minimum coordination overhead. Start with good task decomposition and clear contracts, and the rest follows naturally.
