# External State Provider Pattern

**Version:** 1.0.0
**Category:** Infrastructure Pattern
**Purpose:** Persist agent state in external systems for session continuity

---

## Overview

The External State Provider Pattern abstracts state management behind a provider interface, enabling AI agents to use external systems (Linear, GitHub Issues, Notion) as distributed memory instead of relying on local files that don't survive context resets.

### Key Insight

> Local files are temporary. External systems are persistent.
> Agent state stored in Linear/GitHub survives context resets and is visible to humans.

---

## Problem Statement

File-based state has limitations:

1. **Context Resets**: State lost when agent context resets
2. **Human Visibility**: Humans can't easily see agent progress
3. **Collaboration**: Multiple agents can't coordinate on same tasks
4. **Durability**: Files can be corrupted, deleted, or become stale
5. **Integration**: Doesn't integrate with team workflows

---

## Solution: Provider Abstraction

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Application                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            StateProvider Interface                   │   │
│  │                                                      │   │
│  │  create_task() get_task() update_task()             │   │
│  │  get_tasks() get_meta() update_meta()               │   │
│  │  start_session() end_session()                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│           ┌───────────────┼───────────────┐                │
│           │               │               │                │
│           ▼               ▼               ▼                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Linear    │ │   GitHub    │ │    File     │          │
│  │  Provider   │ │  Provider   │ │  Provider   │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         │               │               │                  │
└─────────┼───────────────┼───────────────┼──────────────────┘
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Linear   │   │ GitHub   │   │  Local   │
    │   API    │   │ Issues   │   │  Files   │
    └──────────┘   └──────────┘   └──────────┘
```

### Provider Interface

```python
class StateProvider(ABC):
    """Abstract base for state providers"""

    # Task Management
    def create_task(self, task_data: Dict) -> str
    def get_task(self, task_id: str) -> Optional[Task]
    def update_task(self, task_id: str, updates: Dict) -> bool
    def delete_task(self, task_id: str) -> bool
    def get_tasks(self, **filters) -> List[Task]

    # Session Metadata (META issue)
    def get_meta(self) -> Optional[SessionMeta]
    def update_meta(self, updates: Dict) -> bool

    # Session Lifecycle
    def start_session(self) -> str
    def end_session(self, summary: str) -> bool
    def add_session_comment(self, comment: str) -> bool

    # Progress Tracking
    def get_progress_summary(self) -> Dict
```

---

## Provider Implementations

### 1. Linear Provider

Best for teams already using Linear for project management.

**Advantages:**
- Rich issue tracking with projects, cycles, labels
- Excellent API with GraphQL
- Built-in progress visualization
- Team collaboration features

**Configuration:**
```yaml
state_provider:
  type: "linear"
  api_key_env: "LINEAR_API_KEY"
  team_id: "TEAM_ID"  # Optional, auto-detected
  project_name: "AI Development"  # Auto-created if needed
  meta_issue_label: "meta"
```

**Mapping:**
| Agent Concept | Linear Entity |
|--------------|---------------|
| Task | Issue |
| META | Issue with "meta" label |
| Session Comment | Issue Comment |
| Category | Label |
| Priority | Priority (1-4) |
| Status | Workflow State |

### 2. GitHub Provider

Best for teams using GitHub Issues for tracking.

**Advantages:**
- Integrated with code repository
- Familiar workflow for developers
- Free for public repos
- PR linking support

**Configuration:**
```yaml
state_provider:
  type: "github"
  api_key_env: "GITHUB_TOKEN"
  repo: "owner/repo"
  meta_issue_label: "meta"
```

**Mapping:**
| Agent Concept | GitHub Entity |
|--------------|---------------|
| Task | Issue |
| META | Issue with "meta" label |
| Session Comment | Issue Comment |
| Category | Label |
| Priority | Label (P1, P2, P3, P4) |
| Status | State (open/closed) + Labels |

### 3. File Provider (Default)

Fallback for local development without external services.

**Advantages:**
- No setup required
- Works offline
- No API rate limits
- Full control

**Configuration:**
```yaml
state_provider:
  type: "file"
  state_dir: ".ai-agents/state"
```

**Files:**
```
.ai-agents/state/
├── tasks.json          # All tasks
├── meta.json           # Session metadata
└── sessions/           # Session logs
    └── session-YYYYMMDD-HHMMSS.json
```

---

## Usage Patterns

### 1. Simple Task Management

```python
from scripts.state_providers import get_provider

provider = get_provider()

# Create task
task_id = provider.create_task({
    "title": "Implement login form",
    "priority": 2,
    "category": "frontend",
    "acceptance_criteria": ["Form displays", "Validation works"],
    "test_steps": ["Load page", "Submit form"]
})

# Update status
provider.update_task(task_id, {"status": "in_progress"})

# Complete task
provider.update_task(task_id, {"status": "done"})
```

### 2. Session Continuity

```python
# Session 1: Initialize
provider = get_provider()
session_id = provider.start_session()

# Create tasks...
provider.create_task({...})
provider.create_task({...})

# End session
provider.end_session("Completed setup, 2 tasks created")

# ---- Context Reset ----

# Session 2: Resume
provider = get_provider()
session_id = provider.start_session()

# Query existing tasks
tasks = provider.get_tasks(status=TaskStatus.TODO)
print(f"Resuming with {len(tasks)} todo tasks")

# Continue work...
```

### 3. META Issue for Context

```python
# Update META with decisions
provider.update_meta({
    "current_focus": "Authentication system",
    "architecture_decisions": [
        {"decision": "Use JWT", "rationale": "Stateless auth"}
    ],
    "regression_status": "passing"
})

# Add session notes
provider.add_session_comment("""
## Session #5 Summary

Completed:
- TASK-001: Login form
- TASK-002: Token service

Issues:
- Rate limiting needs work

Next session: Start on TASK-003
""")
```

### 4. Progress Tracking

```python
# Get summary
summary = provider.get_progress_summary()

print(f"""
Progress:
  Total: {summary['total']}
  Done: {summary['done']} ({summary['completion_rate']:.0%})
  In Progress: {summary['in_progress']}
  Blocked: {summary['blocked']}
""")
```

---

## Configuration Reference

### Full Configuration

```yaml
# .ai-agents/config.yml

state_provider:
  # Provider type
  type: "linear"  # linear, github, notion, file

  # Authentication
  api_key_env: "LINEAR_API_KEY"

  # Provider-specific
  team_id: "TEAM_ID"
  project_id: "PROJECT_ID"  # Optional, auto-created
  project_name: "AI Development Project"

  # META issue configuration
  meta_issue_label: "meta"
  meta_issue_title: "[META] Project State Tracker"

  # File provider specific
  state_dir: ".ai-agents/state"

  # Caching (optional)
  cache_ttl_seconds: 60
  cache_enabled: true

  # Fallback behavior
  fallback_to_file: true  # If external provider fails
```

### Environment Variables

```bash
# Linear
export LINEAR_API_KEY="lin_api_xxxxx"

# GitHub
export GITHUB_TOKEN="ghp_xxxxx"

# Notion
export NOTION_API_KEY="secret_xxxxx"
```

---

## Migration Between Providers

### File to Linear

```python
from scripts.state_providers import get_provider
from scripts.state_providers.file_provider import FileStateProvider
from scripts.state_providers.linear_provider import LinearStateProvider

# Load from file
file_provider = FileStateProvider()
file_provider.initialize({"state_dir": ".ai-agents/state"})

# Create Linear provider
linear_provider = LinearStateProvider()
linear_provider.initialize({
    "api_key_env": "LINEAR_API_KEY",
    "project_name": "Migrated Project"
})

# Migrate tasks
tasks = file_provider.get_tasks()
for task in tasks:
    linear_provider.create_task(task.to_dict())

# Migrate META
meta = file_provider.get_meta()
if meta:
    linear_provider.update_meta(meta.to_dict())

print(f"Migrated {len(tasks)} tasks to Linear")
```

### Linear to File (Offline Mode)

```python
# Export from Linear
tasks = linear_provider.get_tasks()
meta = linear_provider.get_meta()

# Save to files
file_provider = FileStateProvider()
file_provider.initialize({"state_dir": ".ai-agents/state-backup"})

for task in tasks:
    file_provider.create_task(task.to_dict())

file_provider.update_meta(meta.to_dict())
```

---

## Best Practices

### DO:

1. **Configure early** - Set up provider before starting work
2. **Use META for context** - Store decisions and notes
3. **Track sessions** - Start/end sessions for continuity
4. **Handle failures gracefully** - Fall back to file provider

### DON'T:

1. **Don't mix providers** - Use one provider per project
2. **Don't skip META updates** - Future sessions need context
3. **Don't ignore errors** - Provider failures indicate issues
4. **Don't hardcode credentials** - Use environment variables

---

## Troubleshooting

### Connection Failed

```
Error: Could not connect to Linear API
Solution:
  1. Verify API key in environment
  2. Check network connectivity
  3. Verify team_id is correct
  4. Enable fallback_to_file: true
```

### Rate Limited

```
Error: Rate limit exceeded
Solution:
  1. Enable caching (cache_enabled: true)
  2. Increase cache TTL
  3. Batch operations where possible
  4. Add retry with backoff
```

### META Issue Not Found

```
Error: META issue not found
Solution:
  1. Provider will auto-create on first use
  2. Check meta_issue_label matches existing
  3. Verify project permissions
```

---

## Version History

- **1.0.0** (2024-01-15): Initial external state provider pattern
