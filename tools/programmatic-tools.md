# Programmatic Tool Calling Tools

> **Purpose**: Tools designed for code-based orchestration, restricted to execution from sandbox code only.
> **Based on**: [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

## Overview

These tools use `allowed_callers: ["code_execution_20250825"]` to restrict invocation to programmatic code execution only. This enables Claude to write Python code that orchestrates tools, with intermediate results processed in code rather than returned to the model.

## Benefits

| Metric | Sequential Calls | Programmatic Calls |
|--------|-----------------|-------------------|
| Context pollution | High (all results) | Low (final only) |
| Inference passes | N per workflow | 1 per workflow |
| Token usage | Higher | ~37% reduction |
| Parallel execution | Not possible | Via asyncio |

---

## Tool Definitions

### assign_task

Assign a development task to an agent.

```json
{
  "name": "assign_task",
  "description": "Assign a task to a specific agent for execution",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["agent_id", "task_id", "description"],
    "properties": {
      "agent_id": {
        "type": "string",
        "enum": ["backend-dev", "frontend-dev", "qa-tester", "architect"],
        "description": "Agent to assign the task to"
      },
      "task_id": {
        "type": "string",
        "pattern": "^TASK-[0-9]{3,}$",
        "description": "Unique task identifier"
      },
      "description": {
        "type": "string",
        "description": "Detailed task description"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "critical"],
        "default": "medium"
      },
      "dependencies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Task IDs that must complete first"
      }
    }
  }
}
```

**Example Usage in Code:**
```python
# Assign backend task
assign_task("backend-dev", "TASK-001", "Create user authentication API")

# Assign with dependencies
assign_task("frontend-dev", "TASK-002", "Build login form UI",
            priority="high", dependencies=["TASK-001"])
```

---

### execute_task

Execute a previously assigned task.

```json
{
  "name": "execute_task",
  "description": "Execute a task and return the result",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["task_id"],
    "properties": {
      "task_id": {
        "type": "string",
        "description": "ID of the task to execute"
      }
    }
  }
}
```

**Example Usage:**
```python
result = execute_task("TASK-001")
if result["status"] == "completed":
    print(f"Deliverables: {result['deliverables']}")
elif result["status"] == "blocked":
    print(f"Blockers: {result['blockers']}")
```

---

### parallel_execute

Execute multiple independent tasks in parallel.

```json
{
  "name": "parallel_execute",
  "description": "Execute multiple tasks simultaneously",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["task_ids"],
    "properties": {
      "task_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of task IDs to execute in parallel"
      }
    }
  }
}
```

**Example Usage:**
```python
# Execute independent tasks in parallel
results = parallel_execute(["TASK-001", "TASK-002", "TASK-003"])

# Check all results
completed = [tid for tid, r in results.items() if r["status"] == "completed"]
print(f"Completed: {len(completed)}/{len(results)}")
```

---

### get_task_status

Check the current status of a task.

```json
{
  "name": "get_task_status",
  "description": "Get current status of a task",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["task_id"],
    "properties": {
      "task_id": {
        "type": "string",
        "description": "Task ID to check"
      }
    }
  }
}
```

---

### resolve_blocker

Provide resolution for a blocked task.

```json
{
  "name": "resolve_blocker",
  "description": "Provide resolution guidance for a blocked task",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["task_id", "resolution"],
    "properties": {
      "task_id": {
        "type": "string",
        "description": "Blocked task ID"
      },
      "resolution": {
        "type": "string",
        "description": "Resolution guidance or decision"
      }
    }
  }
}
```

---

### aggregate_results

Combine results from multiple tasks.

```json
{
  "name": "aggregate_results",
  "description": "Aggregate results from multiple completed tasks",
  "allowed_callers": ["code_execution_20250825"],
  "input_schema": {
    "type": "object",
    "required": ["task_ids"],
    "properties": {
      "task_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Task IDs to aggregate"
      }
    }
  }
}
```

---

## Complete Orchestration Example

```python
# Programmatic orchestration code generated by Claude
# This runs in a sandbox - only final `result` is returned to the model

# Step 1: Create task breakdown
assign_task("backend-dev", "TASK-001", "Create REST API for user management")
assign_task("backend-dev", "TASK-002", "Set up database models and migrations")
assign_task("frontend-dev", "TASK-003", "Build user registration form")
assign_task("qa-tester", "TASK-004", "Write integration tests",
            dependencies=["TASK-001", "TASK-002", "TASK-003"])

# Step 2: Execute independent tasks in parallel
backend_results = parallel_execute(["TASK-001", "TASK-002"])

# Step 3: Check for blockers and resolve
for task_id, res in backend_results.items():
    if res["status"] == "blocked":
        resolve_blocker(task_id, "Proceed with SQLite for development")

# Step 4: Execute dependent task
frontend_result = execute_task("TASK-003")

# Step 5: Execute tests after all prerequisites
if all(get_task_status(t)["status"] == "completed" for t in ["TASK-001", "TASK-002", "TASK-003"]):
    test_result = execute_task("TASK-004")

# Step 6: Aggregate final results
final = aggregate_results(["TASK-001", "TASK-002", "TASK-003", "TASK-004"])

# Only this is returned to the model
result = {
    "feature": "User Management System",
    "tasks_completed": final["completed"],
    "tasks_total": final["task_count"],
    "deliverables": final["all_deliverables"],
    "status": "success" if final["completed"] == final["task_count"] else "partial"
}
```

---

## Configuration

### Agent Schema (v2.0)

Add tools with `allowed_callers` in your agent configuration:

```yaml
agents:
  orchestrator:
    base: "base/manager.md"
    tools:
      - path: "tools/programmatic-tools.md"
        allowed_callers: ["code_execution_20250825"]
```

### Enabling Programmatic Mode

```bash
# Run orchestrator in programmatic mode
python programmatic_orchestrator.py \
  --feature "user authentication" \
  --project-dir /path/to/project \
  --verbose
```

---

## Security Considerations

1. **Sandbox Execution**: All code runs in a restricted sandbox
   - No file system access
   - No network access
   - No dangerous imports
   - Timeout protection

2. **Tool Restriction**: `allowed_callers` prevents direct tool invocation
   - Tools can only be called from within sandbox code
   - Prevents injection attacks

3. **Code Validation**: All code is validated before execution
   - Syntax checking
   - Forbidden operation detection
   - Import blocking

---

## Best Practices

1. **Use for Complex Workflows**: Best when 3+ tools need to work together
2. **Parallelize Independent Tasks**: Use `parallel_execute` for efficiency
3. **Process Intermediate Results**: Filter/transform before returning
4. **Keep Final Result Focused**: Only return what's needed for next steps
5. **Handle Errors in Code**: Use try/except rather than propagating to model
