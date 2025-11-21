# Complete Guide to Automated Orchestration

This guide shows you how to use the orchestration scripts for fully automated multi-agent coordination.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Complete Example](#complete-example)
- [Architecture Deep Dive](#architecture-deep-dive)
- [Customization](#customization)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install & Configure

```bash
# Install dependencies
cd scripts/orchestration
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Verify installation
python -c "import anthropic; print('✅ Ready!')"
```

### 2. Prepare Your Project

```bash
# Go to YOUR project
cd ~/projects/my-app

# Create communication file
mkdir -p .ai-agents/state
cp /path/to/AI_agents/examples/team-communication-template.json \
   .ai-agents/state/team-communication.json
```

### 3. Run Your First Orchestration

```bash
# Simple orchestrator (learning)
python /path/to/AI_agents/scripts/orchestration/simple_orchestrator.py \
  --feature "user login with email and password" \
  --project-dir ~/projects/my-app

# Watch the magic happen!
```

---

## Complete Example: Building Authentication

Let's walk through a complete example building user authentication.

### Project Setup

```bash
# Your project structure
my-app/
├── .git/
├── .ai-agents/
│   ├── state/
│   │   └── team-communication.json
│   └── context/
│       ├── architecture.md
│       ├── api-contracts.md
│       └── coding-standards.md
├── src/
│   ├── backend/
│   └── frontend/
└── package.json
```

### Running the Orchestrator

```bash
python scripts/orchestration/file_based_orchestrator.py \
  --feature "JWT-based user authentication with login and registration" \
  --project-dir ~/projects/my-app \
  --api-provider anthropic
```

### What Happens (Step by Step)

**Phase 1: Manager Planning (API Call 1)**

```
[Orchestrator] Starting...
[Orchestrator] Calling Manager agent via API...

[Manager] Creating task breakdown for: JWT authentication

[API Response from Manager]:
{
  "tasks": [
    {
      "task_id": "TASK-001",
      "description": "Implement JWT service and auth API endpoints",
      "assigned_to": "backend-dev",
      "deliverables": [
        "JWT token generation and verification (src/services/jwt.ts)",
        "Auth controller with login/register (src/controllers/auth.ts)",
        "POST /api/auth/login endpoint",
        "POST /api/auth/register endpoint",
        "Auth middleware (src/middleware/auth.ts)"
      ]
    },
    {
      "task_id": "TASK-002",
      "description": "Build login and registration UI components",
      "assigned_to": "frontend-dev",
      "dependencies": ["TASK-001"],
      "deliverables": [
        "Login form component",
        "Registration form component",
        "Auth context for state management",
        "Protected route wrapper"
      ]
    },
    {
      "task_id": "TASK-003",
      "description": "Write comprehensive tests for auth flow",
      "assigned_to": "qa-tester",
      "dependencies": ["TASK-001", "TASK-002"]
    }
  ],
  "decisions": [
    {
      "decision": "Use JWT with 1-hour expiration",
      "rationale": "Security best practice for access tokens",
      "affected_agents": ["backend-dev", "frontend-dev"]
    }
  ]
}

[Orchestrator] Tasks written to team-communication.json
[Orchestrator] 3 tasks created
```

**Phase 2: Backend Implementation (API Call 2)**

```
[Orchestrator] Executing TASK-001...
[Orchestrator] Calling backend-dev agent via API...

[Backend Agent Prompt]:
"You are a backend developer. Implement this task:

Task: TASK-001 - JWT service and auth API
Project: ~/projects/my-app
Branch: feature/auth/agent/backend-dev/api

Requirements (from manager):
- JWT token generation/verification
- Auth controller
- Login/register endpoints
- Auth middleware

Context files:
- team-communication.json (manager's decisions)
- .ai-agents/context/api-contracts.md (API specs)

Update team-communication.json with your progress."

[API Response from Backend Agent]:
{
  "status": "completed",
  "progress": 100,
  "completed_items": [
    "Created src/services/jwt.ts with token generation/verification",
    "Implemented src/controllers/auth.ts with login/register handlers",
    "Added POST /api/auth/login endpoint with validation",
    "Added POST /api/auth/register endpoint with password hashing",
    "Created src/middleware/auth.ts for protected routes",
    "Wrote 24 unit tests (95% coverage)"
  ],
  "files_modified": [
    "src/services/jwt.ts (new)",
    "src/controllers/auth.ts (new)",
    "src/middleware/auth.ts (new)",
    "src/routes/auth.ts (new)",
    "tests/auth.test.ts (new)"
  ],
  "test_results": "24 passed, 0 failed",
  "blockers": []
}

[Orchestrator] Backend task complete
[Orchestrator] Updating team-communication.json...
```

**Phase 3: Frontend Implementation (API Call 3)**

```
[Orchestrator] TASK-002 dependencies satisfied (TASK-001 complete)
[Orchestrator] Executing TASK-002...
[Orchestrator] Calling frontend-dev agent via API...

[Frontend Agent Prompt]:
"You are a frontend developer. Implement this task:

Task: TASK-002 - Login and registration UI
Project: ~/projects/my-app
Branch: feature/auth/agent/frontend-dev/ui

Backend Status (from team-communication.json):
- JWT API complete
- Available endpoints: POST /api/auth/login, /api/auth/register
- User type defined in src/types/user.ts

Requirements:
- Login form component
- Registration form component
- Auth state management
- Protected routes

Read team-communication.json for API contract details."

[API Response from Frontend Agent]:
{
  "status": "completed",
  "progress": 100,
  "completed_items": [
    "Created src/components/auth/LoginForm.tsx",
    "Created src/components/auth/RegisterForm.tsx",
    "Implemented src/contexts/AuthContext.tsx for state",
    "Added ProtectedRoute wrapper component",
    "Integrated with backend API endpoints",
    "Added form validation and error handling",
    "Wrote component tests (18 tests, all passing)"
  ],
  "notes": "Used backend's User type definition. API integration working."
}

[Orchestrator] Frontend task complete
```

**Phase 4: QA Testing (API Call 4)**

```
[Orchestrator] All implementation complete
[Orchestrator] Executing TASK-003...
[Orchestrator] Calling qa-tester agent via API...

[QA Agent Response]:
{
  "status": "completed",
  "test_suites": [
    {
      "name": "Backend API Tests",
      "tests_run": 24,
      "passed": 24,
      "failed": 0,
      "coverage": 95
    },
    {
      "name": "Frontend Component Tests",
      "tests_run": 18,
      "passed": 18,
      "failed": 0
    },
    {
      "name": "E2E Tests",
      "tests_run": 6,
      "passed": 6,
      "failed": 0
    }
  ],
  "overall_status": "PASS"
}

[Orchestrator] QA validation complete - ALL TESTS PASS
```

**Phase 5: Integration (API Call 5 - Manager)**

```
[Orchestrator] All tasks complete
[Orchestrator] Calling Manager for integration...

[Manager]:
All tasks completed successfully:
✅ TASK-001: Backend API (complete, tested)
✅ TASK-002: Frontend UI (complete, tested)
✅ TASK-003: QA validation (all tests pass)

Integration plan:
1. Merge feature/auth/agent/backend-dev/api → feature/user-auth
2. Merge feature/auth/agent/frontend-dev/ui → feature/user-auth
3. Run full test suite
4. Merge feature/user-auth → main

[Orchestrator] Integration complete
```

**Final Output**

```
================================================================================
ORCHESTRATION SUMMARY
================================================================================
Feature: JWT-based user authentication
Duration: 4 minutes
API Calls: 5 (Manager x2, Backend x1, Frontend x1, QA x1)
Tokens Used: ~57,000
Estimated Cost: ~$3.50

Tasks:
  ✅ TASK-001: Backend API (completed)
  ✅ TASK-002: Frontend UI (completed)
  ✅ TASK-003: QA Tests (completed)

Results:
  • Files created: 12
  • Tests written: 48
  • Test coverage: 95%
  • All tests: PASS

Status: ✅ SUCCESS - Ready to merge
================================================================================
```

---

## Architecture Deep Dive

### How API Calls Work

```python
# Simplified orchestrator flow

class Orchestrator:
    def run(self, feature):
        # 1. Call Manager via API
        tasks = self.manager_create_tasks(feature)

        # 2. Execute each task via API
        for task in tasks:
            agent_id = task["assigned_to"]

            # Make API call to spawn agent
            response = self.call_api(
                role=agent_id,
                prompt=self._build_task_prompt(task),
                system=self._get_system_prompt(agent_id)
            )

            # Process response
            self._update_state(task, response)

        # 3. Call Manager for integration
        self.manager_integrate(tasks)

    def call_api(self, role, prompt, system):
        # Actual API call to Claude/GPT
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
```

### Communication Flow

```
                    ┌──────────────┐
                    │ Orchestrator │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌────────┐       ┌─────────┐      ┌──────────┐
    │Manager │       │Backend  │      │Frontend  │
    │API Call│       │API Call │      │API Call  │
    └────┬───┘       └────┬────┘      └────┬─────┘
         │                │                 │
         └────────────────┼─────────────────┘
                          │
                          ▼
              team-communication.json
              (Shared coordination state)
```

---

## Customization

### Custom Workflow

Create your own workflow by extending the base orchestrator:

```python
from file_based_orchestrator import FileBasedOrchestrator

class MyCustomOrchestrator(FileBasedOrchestrator):
    """Custom workflow for your specific needs"""

    def run(self, feature):
        # Your custom phases
        print("Starting custom workflow...")

        # Phase 1: Design review
        design = self.architect_review(feature)

        # Phase 2: Security analysis
        security = self.security_scan(design)

        # Phase 3: Implementation (using base orchestrator)
        super().run(feature)

        # Phase 4: Performance testing
        perf = self.performance_test()

        return {
            "design": design,
            "security": security,
            "performance": perf
        }

    def architect_review(self, feature):
        """Custom phase: Architect reviews design"""
        system = "You are a software architect..."
        prompt = f"Review the design for: {feature}"
        return self.call_agent("architect", "architect", prompt, system)
```

### Custom Agent Types

Add your own specialized agents:

```python
class DataEngineerOrchestrator(FileBasedOrchestrator):
    """Orchestrator with data engineering agents"""

    def get_agent_types(self):
        return {
            "data-engineer": {
                "system": "You are a data engineer...",
                "specialties": ["pipelines", "ETL", "data modeling"]
            },
            "ml-engineer": {
                "system": "You are an ML engineer...",
                "specialties": ["model training", "deployment"]
            }
        }
```

---

## Production Deployment

### Configuration File

Create `orchestrator-config.json`:

```json
{
  "project_dir": "/app/my-project",
  "api_provider": "anthropic",
  "model": "claude-sonnet-4-20250514",

  "agents": {
    "manager": {
      "max_tokens": 8000,
      "temperature": 0.7
    },
    "backend-dev": {
      "max_tokens": 8000,
      "temperature": 0.3
    },
    "frontend-dev": {
      "max_tokens": 8000,
      "temperature": 0.3
    }
  },

  "coordination": {
    "check_interval_seconds": 30,
    "max_iterations": 50,
    "auto_merge": false,
    "parallel_execution": true
  },

  "limits": {
    "max_api_calls": 100,
    "token_budget": 500000,
    "cost_limit_usd": 50
  }
}
```

### CI/CD Integration

```yaml
# .github/workflows/ai-development.yml

name: AI Agent Development

on:
  issues:
    types: [labeled]

jobs:
  ai-develop:
    if: contains(github.event.issue.labels.*.name, 'ai-implement')
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install anthropic

      - name: Run orchestrator
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/orchestration/file_based_orchestrator.py \
            --feature "${{ github.event.issue.title }}" \
            --project-dir . \
            --max-iterations 20

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: "AI: ${{ github.event.issue.title }}"
          body: "Automated implementation by AI agents"
          branch: "ai/issue-${{ github.event.issue.number }}"
```

### Docker Deployment

```dockerfile
# Dockerfile for orchestrator service

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/orchestration/ /app/orchestration/

ENV ANTHROPIC_API_KEY=""
ENV PROJECT_DIR="/workspace"

ENTRYPOINT ["python", "/app/orchestration/file_based_orchestrator.py"]
```

Run with:

```bash
docker run -it \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v $(pwd):/workspace \
  ai-orchestrator \
  --feature "user authentication" \
  --project-dir /workspace
```

---

## Troubleshooting

### Issue: High API Costs

**Symptom**: Bills higher than expected

**Solution**:

```python
# Add token tracking
class CostAwareOrchestrator(FileBasedOrchestrator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_tokens = 0
        self.token_budget = 500000  # 500k tokens

    def call_agent(self, agent_id, role, prompt, system_prompt):
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        estimated_tokens = (len(prompt) + len(system_prompt)) // 4

        if self.total_tokens + estimated_tokens > self.token_budget:
            raise Exception(f"Token budget exceeded: {self.total_tokens}/{self.token_budget}")

        response = super().call_agent(agent_id, role, prompt, system_prompt)

        # Track actual usage (if API provides it)
        self.total_tokens += estimated_tokens

        return response
```

### Issue: Agents Getting Stuck

**Symptom**: Agent keeps asking same question

**Solution**:

```python
def call_agent_with_retry(self, agent_id, task, max_retries=3):
    """Call agent with loop detection"""

    for attempt in range(max_retries):
        response = self.call_agent(agent_id, task)

        # Check if agent is stuck
        if self._is_repetitive(response, agent_id):
            print(f"⚠️  Agent {agent_id} stuck, escalating to manager")

            # Have manager provide guidance
            guidance = self.manager_resolve(task, response)

            # Retry with guidance
            task["additional_context"] = guidance
            continue

        return response

    raise Exception(f"Agent {agent_id} failed after {max_retries} attempts")
```

### Issue: Parallel Execution Conflicts

**Symptom**: Agents modifying same files

**Solution**: Use git worktrees with orchestration:

```python
import subprocess

class ParallelOrchestrator(FileBasedOrchestrator):
    def setup_worktrees(self, tasks):
        """Create worktree for each agent"""
        worktrees = {}

        for task in tasks:
            agent_id = task["assigned_to"]
            branch = task["branch"]

            # Create worktree
            worktree_path = self.project_dir.parent / f"worktrees/{agent_id}"
            subprocess.run([
                "git", "worktree", "add",
                str(worktree_path),
                "-b", branch
            ])

            worktrees[agent_id] = worktree_path

        return worktrees

    def execute_task_in_worktree(self, task, worktree):
        """Execute task in isolated worktree"""
        # Agent works in their own directory
        # No conflicts with other agents!
        pass
```

---

## Advanced: Parallel Execution

Full parallel implementation:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class TrueParallelOrchestrator(FileBasedOrchestrator):
    def run_parallel(self, feature, max_workers=3):
        """Execute independent tasks in parallel"""

        # Phase 1: Manager creates tasks
        tasks = self.manager_create_tasks(feature)

        # Phase 2: Group tasks by dependencies
        independent_tasks = [t for t in tasks if not t.get("dependencies")]
        dependent_tasks = [t for t in tasks if t.get("dependencies")]

        results = []

        # Execute independent tasks in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.agent_execute_task, task): task
                for task in independent_tasks
            }

            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ {task['task_id']} completed")
                except Exception as e:
                    print(f"❌ {task['task_id']} failed: {e}")

        # Execute dependent tasks after dependencies complete
        for task in dependent_tasks:
            if self._dependencies_satisfied(task, results):
                result = self.agent_execute_task(task)
                results.append(result)

        return results
```

---

## Cost Estimation

### Token Usage Breakdown

For a typical feature (like user authentication):

| Agent | Calls | Avg Tokens/Call | Total Tokens |
|-------|-------|----------------|--------------|
| Manager (planning) | 1 | 2,000 | 2,000 |
| Backend Dev | 3 | 6,000 | 18,000 |
| Frontend Dev | 3 | 6,000 | 18,000 |
| QA Tester | 2 | 4,000 | 8,000 |
| Manager (integration) | 1 | 2,000 | 2,000 |
| **TOTAL** | **10** | - | **48,000** |

### Cost Calculation (Claude Sonnet 4)

```
Input tokens:  ~24,000 × $15/million  = $0.36
Output tokens: ~24,000 × $75/million  = $1.80
─────────────────────────────────────────────
Total cost per feature: ~$2.16
```

For comparison:
- Small feature: $1-3
- Medium feature: $3-10
- Large feature: $10-30

---

## Summary

**Automated orchestration gives you:**

✅ True multi-agent parallelism
✅ No manual coordination needed
✅ Reproducible workflows
✅ CI/CD integration capability
✅ Scalable to many agents

**But requires:**

⚠️ API keys and budget
⚠️ Python programming knowledge
⚠️ Infrastructure setup
⚠️ Careful monitoring

**Best for:**
- Large projects with 5+ agents
- Repetitive workflows
- CI/CD automation
- Teams with engineering resources

---

**Ready to try it?** Start with `simple_orchestrator.py`, then graduate to `file_based_orchestrator.py`, then build your own custom orchestrator!
