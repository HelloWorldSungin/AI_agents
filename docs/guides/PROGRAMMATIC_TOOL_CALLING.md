# Programmatic Tool Calling Guide

> **Advanced orchestration pattern where Claude writes Python code to orchestrate tools**

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

---

## Overview

Programmatic tool calling is an advanced pattern where instead of Claude making individual tool calls (each returning to the model), Claude writes Python code that:

1. Calls multiple tools
2. Processes intermediate results in code
3. Returns only the final aggregated result

This dramatically reduces context pollution and eliminates N inference passes for N-tool workflows.

---

## Why Programmatic Tool Calling?

### The Problem with Sequential Tool Calls

```
Traditional Flow:
┌─────────────────────────────────────────────────────────────────┐
│ User: "Implement user auth"                                      │
│                                    ↓                             │
│ Claude: calls assign_task(backend-dev, task1)                   │
│                                    ↓                             │
│ Result: {task_id: TASK-001, status: assigned} ← ADDED TO CONTEXT│
│                                    ↓                             │
│ Claude: calls execute_task(TASK-001)                            │
│                                    ↓                             │
│ Result: {status: completed, deliverables: [...]} ← MORE CONTEXT │
│                                    ↓                             │
│ Claude: calls assign_task(frontend-dev, task2)                  │
│                    ... repeats N times ...                       │
│                                    ↓                             │
│ Context now has 50KB+ of intermediate results                   │
└─────────────────────────────────────────────────────────────────┘
```

**Problems:**
- Each tool result pollutes context (50KB+ accumulates quickly)
- N tools = N inference passes
- No parallel execution
- Expensive and slow

### The Programmatic Solution

```
Programmatic Flow:
┌─────────────────────────────────────────────────────────────────┐
│ User: "Implement user auth"                                      │
│                                    ↓                             │
│ Claude: generates orchestration code                            │
│                                    ↓                             │
│ Sandbox executes code:                                          │
│   - assign_task(backend-dev, task1)                             │
│   - assign_task(frontend-dev, task2)                            │
│   - parallel_execute([task1, task2])  ← Processed in code       │
│   - aggregate_results([...])                                     │
│   - result = {summary: ...}           ← Only this returned      │
│                                    ↓                             │
│ Context only has final summary (1KB vs 50KB)                    │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- 37% token reduction
- Single inference pass
- Parallel execution
- Intermediate results stay in code

---

## Quick Start

### 1. Basic Usage

```bash
# Run programmatic orchestrator
python scripts/orchestration/programmatic_orchestrator.py \
  --feature "user authentication system" \
  --project-dir /path/to/project \
  --verbose
```

### 2. Python API

```python
from scripts.orchestration.programmatic_orchestrator import ProgrammaticOrchestrator

# Create orchestrator
orch = ProgrammaticOrchestrator(
    project_dir="/path/to/project",
    enable_cache=True,  # Use prompt caching
    verbose=True
)

# Run orchestration
result = orch.run("Implement shopping cart checkout")

print(f"Success: {result['success']}")
print(f"Tool calls: {result['tool_calls']}")
print(f"Execution time: {result['execution_time_ms']}ms")
```

### 3. Direct Sandbox Usage

```python
from scripts.orchestration.sandbox_executor import SandboxExecutor, Tool

# Define custom tools
tools = [
    Tool("fetch_user", lambda id: {"name": "John"}, "Fetch user by ID"),
    Tool("fetch_orders", lambda id: [{"total": 100}], "Fetch user orders"),
]

# Create sandbox
sandbox = SandboxExecutor(tools)

# Execute code
code = """
user = fetch_user("123")
orders = fetch_orders("123")
result = {"user": user["name"], "order_count": len(orders)}
"""

output = sandbox.execute(code)
print(output.result)  # {"user": "John", "order_count": 1}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Programmatic Orchestrator                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    Claude    │───▶│   Sandbox    │───▶│    Tools     │      │
│  │  (Planner)   │    │  Executor    │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   │                   │               │
│    Generates           Executes            Called from          │
│    Python code         safely              code only            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Sandbox Features                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • Restricted builtins (no os, sys, file access)          │  │
│  │ • Timeout protection (default 60s)                        │  │
│  │ • Code validation (blocks dangerous patterns)             │  │
│  │ • Tool call tracking                                      │  │
│  │ • Output capture                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Available Tools

All tools use `allowed_callers: ["code_execution_20250825"]`:

| Tool | Description | Returns |
|------|-------------|---------|
| `assign_task(agent_id, task_id, description)` | Assign task to agent | Confirmation |
| `execute_task(task_id)` | Execute a task | Status, deliverables |
| `parallel_execute(task_ids)` | Execute tasks in parallel | Dict of results |
| `get_task_status(task_id)` | Check task status | Status info |
| `resolve_blocker(task_id, resolution)` | Resolve blocked task | Updated status |
| `aggregate_results(task_ids)` | Combine task results | Summary |
| `get_all_tasks()` | List all tasks | Task list |

---

## Example: Complex Workflow

Here's what Claude might generate for "Implement user dashboard":

```python
# Claude-generated orchestration code

# Phase 1: Create tasks
assign_task("backend-dev", "TASK-001", "Create dashboard API endpoints")
assign_task("backend-dev", "TASK-002", "Add caching layer for dashboard data")
assign_task("frontend-dev", "TASK-003", "Build dashboard layout component")
assign_task("frontend-dev", "TASK-004", "Create data visualization widgets")
assign_task("qa-tester", "TASK-005", "Write E2E tests for dashboard",
            dependencies=["TASK-001", "TASK-003", "TASK-004"])

# Phase 2: Execute backend tasks in parallel
backend_results = parallel_execute(["TASK-001", "TASK-002"])

# Phase 3: Handle any blockers
blocked_tasks = [tid for tid, r in backend_results.items()
                 if r.get("status") == "blocked"]
for task_id in blocked_tasks:
    status = get_task_status(task_id)
    if "database" in str(status.get("blockers", [])).lower():
        resolve_blocker(task_id, "Use in-memory cache for development")

# Phase 4: Execute frontend tasks (depend on backend)
if all(backend_results[t]["status"] == "completed" for t in ["TASK-001", "TASK-002"]):
    frontend_results = parallel_execute(["TASK-003", "TASK-004"])
else:
    frontend_results = {}

# Phase 5: Run tests if all prerequisites complete
prereqs = ["TASK-001", "TASK-003", "TASK-004"]
if all(get_task_status(t)["status"] == "completed" for t in prereqs):
    execute_task("TASK-005")

# Phase 6: Aggregate results
all_tasks = ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-005"]
summary = aggregate_results(all_tasks)

# Final result - only this is returned to the model
result = {
    "feature": "User Dashboard",
    "completed": summary["completed"],
    "total": summary["task_count"],
    "deliverables": summary["all_deliverables"],
    "success": summary["completed"] == summary["task_count"]
}
```

**Result:** A single, focused summary instead of 10+ intermediate tool results.

---

## Security Model

### Sandbox Restrictions

The sandbox provides security through:

1. **Restricted Builtins**
   - No `open()`, `exec()`, `eval()`, `__import__`
   - No file system access
   - No network access

2. **Code Validation**
   - AST analysis before execution
   - Blocks dangerous patterns
   - No imports allowed

3. **Execution Limits**
   - Timeout protection (configurable)
   - Output size limits
   - Memory constraints

4. **Tool Restriction**
   - `allowed_callers` prevents direct tool invocation
   - Tools only accessible within sandbox

### What's Blocked

```python
# These will all fail validation:
import os               # No imports
open("file.txt")        # No file access
eval("code")            # No eval
exec("code")            # No exec
__import__("sys")       # No __import__
request.get("url")      # No network (can't import requests anyway)
```

---

## Comparison: Sequential vs Programmatic

| Aspect | Sequential | Programmatic |
|--------|-----------|--------------|
| **Tool calls** | N separate calls | N calls in 1 execution |
| **Inference passes** | N | 1 |
| **Context growth** | +result per call | Only final result |
| **Token usage** | Higher | ~37% less |
| **Parallel execution** | No | Yes (via code) |
| **Error handling** | Model handles | Code handles |
| **Best for** | Simple tasks | Complex workflows |

---

## Integration with Other Features

### With Deferred Skill Loading

```yaml
# config.yml
agents:
  orchestrator:
    skills:
      always_loaded:
        - "core/skill-creator"  # For planning
      deferred:
        - path: "communication/internal-comms"
          triggers: ["coordinate", "communicate"]
    tools:
      - path: "tools/programmatic-tools.md"
        allowed_callers: ["code_execution_20250825"]
```

### With Prompt Caching

The programmatic orchestrator automatically uses prompt caching when available:

```python
orch = ProgrammaticOrchestrator(
    project_dir="/path/to/project",
    enable_cache=True  # Uses CachedAnthropicClient
)
```

---

## Troubleshooting

### Code Execution Timeout

```
Error: Execution timed out after 60s
```

**Solution:** Increase timeout or simplify workflow:
```python
sandbox = SandboxExecutor(tools, timeout_seconds=120)
```

### Code Validation Failed

```
Error: Code validation failed: Forbidden name: __import__
```

**Solution:** Claude generated unsafe code. This is blocked by design. Re-prompt for safer approach.

### Tool Not Found

```
Error: NameError: name 'my_tool' is not defined
```

**Solution:** Ensure tool is registered with sandbox:
```python
tools = [Tool("my_tool", my_func, "description")]
sandbox = SandboxExecutor(tools)
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/orchestration/sandbox_executor.py` | Sandboxed code execution |
| `scripts/orchestration/programmatic_orchestrator.py` | Main orchestrator |
| `tools/programmatic-tools.md` | Tool definitions |
| `docs/PROGRAMMATIC_TOOL_CALLING.md` | This documentation |

---

## Further Reading

- [Anthropic: Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
- [Agent Schema v2.0](../schemas/agent-schema.json) - `allowed_callers` support
- [Prompt Caching Guide](./prompt_cache.py) - Cost reduction
- [Deferred Loading Guide](../tools/skill-search.md) - Token optimization
