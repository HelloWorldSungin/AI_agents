# Automated Multi-Agent Orchestration Scripts

**Purpose**: Example scripts for building automated multi-agent coordination systems

---

## Overview

These scripts demonstrate how to build **fully automated** multi-agent orchestration systems where agents communicate programmatically without human intervention.

### ⚠️ Important Note

**90% of users should use human-coordinated workflows** (see [PRACTICAL_WORKFLOW_GUIDE.md](../../PRACTICAL_WORKFLOW_GUIDE.md)).

These automated scripts are for:
- Advanced users comfortable with Python and LLM APIs
- Projects requiring true parallel agent execution
- CI/CD automation
- Research and experimentation

---

## What's Included

### 1. `simple_orchestrator.py`
**Basic orchestration example**
- Single manager, multiple task agents
- Sequential task execution
- File-based state management
- Great starting point for learning

**Use case**: Small projects, learning orchestration basics

---

### 2. `file_based_orchestrator.py`
**Production-ready orchestrator using team-communication.json**
- Multiple agents running via API calls
- Shared state file for coordination
- Automatic blocker detection and resolution
- Parallel task execution where possible

**Use case**: Medium projects, 3-5 agents, file-based coordination

---

### 3. `advanced_orchestrator.py` (TODO: Future)
**Advanced orchestration with message queues**
- Redis-based message passing
- Real-time agent communication
- Event-driven architecture
- Scalable to many agents

**Use case**: Large projects, 5+ agents, production systems

---

## Prerequisites

### Required
- Python 3.8+
- Anthropic API key (or OpenAI API key)
- Understanding of async Python

### Install Dependencies

```bash
cd scripts/orchestration
pip install -r requirements.txt
```

### Set API Key

```bash
# For Anthropic Claude
export ANTHROPIC_API_KEY="your-api-key"

# Or for OpenAI
export OPENAI_API_KEY="your-api-key"
```

---

## Quick Start

### 1. Simple Orchestrator Example

```bash
# Run the basic orchestrator
python simple_orchestrator.py \
  --project-dir /path/to/your/project \
  --feature "user authentication"

# Example output:
# [Manager] Creating task breakdown...
# [Manager] Assigned TASK-001 to backend-dev
# [Manager] Assigned TASK-002 to frontend-dev
# [Backend] Working on TASK-001...
# [Backend] Completed: JWT service implemented
# [Frontend] Working on TASK-002...
# [Frontend] Blocked: Need API contract
# [Manager] Resolving blocker: Creating API contract
# [Frontend] Continuing TASK-002...
# [Manager] All tasks complete, initiating merge
```

---

### 2. File-Based Orchestrator

```bash
# Run the file-based orchestrator
python file_based_orchestrator.py \
  --project-dir /path/to/your/project \
  --communication-file .ai-agents/state/team-communication.json \
  --agents manager,backend-dev,frontend-dev,qa-tester

# This will:
# 1. Read team-communication.json
# 2. Assign tasks to agents
# 3. Run agents via API calls
# 4. Coordinate based on updates in the file
# 5. Handle blockers automatically
# 6. Merge when complete
```

---

## Architecture

### How Automated Orchestration Works

```
┌─────────────────────────────────────────────────────┐
│  Orchestrator Process (Python script)               │
│                                                      │
│  ┌─────────────┐                                    │
│  │  Manager    │ ← Creates tasks, coordinates       │
│  │  Agent LLM  │                                    │
│  └──────┬──────┘                                    │
│         │                                            │
│         ├──> Task Queue                             │
│         │                                            │
│  ┌──────┴──────────────────────────┐               │
│  │                                  │               │
│  ┌──────▼──────┐  ┌────────▼──────┐  ┌─────▼─────┐│
│  │  Backend    │  │  Frontend     │  │    QA     ││
│  │  Agent LLM  │  │  Agent LLM    │  │Agent LLM  ││
│  └──────┬──────┘  └────────┬──────┘  └─────┬─────┘│
│         │                   │                │      │
│         └────────┬──────────┴────────────────┘     │
│                  │                                   │
│            Shared State                             │
│    (team-communication.json)                        │
└─────────────────────────────────────────────────────┘
```

### Communication Flow

1. **Orchestrator** reads project requirements
2. **Manager agent** (via API) creates task breakdown
3. **Orchestrator** assigns tasks to agent queues
4. **Task agents** (via API) work on assignments in parallel
5. **Agents** update shared state file with progress
6. **Orchestrator** monitors state, handles blockers
7. **Manager agent** coordinates integration when tasks complete

---

## Configuration

### Agent Configuration

Agents are configured in your `.ai-agents/config.yml`:

```yaml
agents:
  team_manager:
    base: "base/manager.md"
    model: "claude-sonnet-4"  # or "gpt-4"
    max_tokens: 8000

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    model: "claude-sonnet-4"
    max_tokens: 8000

  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    model: "claude-sonnet-4"
    max_tokens: 8000
```

### Orchestrator Configuration

Example `orchestrator-config.json`:

```json
{
  "project_dir": "/path/to/project",
  "communication_file": ".ai-agents/state/team-communication.json",
  "agents": [
    {
      "id": "manager",
      "role": "team_manager",
      "max_concurrent_tasks": 10
    },
    {
      "id": "backend-dev",
      "role": "backend_developer",
      "max_concurrent_tasks": 1
    },
    {
      "id": "frontend-dev",
      "role": "frontend_developer",
      "max_concurrent_tasks": 1
    },
    {
      "id": "qa-tester",
      "role": "qa_tester",
      "max_concurrent_tasks": 1
    }
  ],
  "coordination": {
    "check_interval_seconds": 30,
    "max_iterations": 50,
    "auto_merge": false
  }
}
```

---

## Example Scripts

### Simple Orchestrator

**File**: `simple_orchestrator.py`

**What it does**:
- Reads feature request
- Calls manager agent to create task plan
- Executes tasks sequentially
- Handles basic blockers
- Coordinates integration

**Best for**: Learning, small projects

```bash
python simple_orchestrator.py \
  --feature "Add user profile page" \
  --agents manager,backend-dev,frontend-dev
```

---

### File-Based Orchestrator

**File**: `file_based_orchestrator.py`

**What it does**:
- Monitors team-communication.json
- Executes tasks in parallel where possible
- Automatic blocker detection from agent updates
- Manager coordination for conflicts
- Integration management

**Best for**: Production use, medium projects

```bash
python file_based_orchestrator.py \
  --config orchestrator-config.json \
  --feature "Shopping cart checkout flow"
```

---

## Cost Considerations

### API Costs

Automated orchestration makes multiple API calls:

**Example Feature** (user authentication):
- Manager initial planning: 1 call (~2,000 tokens)
- Backend agent: 3-5 calls (~20,000 tokens total)
- Frontend agent: 3-5 calls (~20,000 tokens total)
- QA agent: 2-3 calls (~10,000 tokens total)
- Manager coordination: 2-3 calls (~5,000 tokens total)

**Total**: ~15-20 API calls, ~57,000 tokens

**Estimated cost** (Claude Sonnet 4):
- Input: ~$15 per million tokens
- Output: ~$75 per million tokens
- Feature cost: ~$1-5 depending on complexity

### Cost Optimization

1. **Use cheaper models where possible**
   ```python
   # Manager and simple tasks: Haiku
   manager_agent = Agent(model="claude-haiku")

   # Complex tasks: Sonnet
   architect_agent = Agent(model="claude-sonnet-4")
   ```

2. **Batch API calls**
   ```python
   # Instead of calling agent for every small update
   # Batch multiple checks together
   ```

3. **Cache agent prompts**
   ```python
   # Use prompt caching for repeated context
   # Anthropic's prompt caching can reduce costs by 90%
   ```

---

## Troubleshooting

### Issue: Agents getting stuck in loops

**Symptom**: Agent keeps asking same question repeatedly

**Solution**:
```python
# Add max iterations per agent
agent.run(task, max_iterations=10)

# Add loop detection
if agent.has_repeated_output():
    escalate_to_manager()
```

---

### Issue: Blockers not being resolved

**Symptom**: Agent reports blocker but orchestrator doesn't handle it

**Solution**:
```python
# Improve blocker detection
def detect_blockers(agent_update):
    if agent_update.get("blockers"):
        notify_manager(agent_update["blockers"])
        pause_agent(agent_update["agent_id"])

# Ensure manager has resolution protocol
manager_prompt += """
When an agent reports a blocker:
1. Analyze the blocker
2. Create solution or workaround
3. Update communication file with resolution
4. Notify orchestrator via status field
"""
```

---

### Issue: High API costs

**Symptom**: Bills are higher than expected

**Solution**:
1. Monitor token usage per agent
   ```python
   logger.info(f"Agent {agent_id} used {tokens} tokens")
   ```

2. Use haiku for simple tasks
   ```python
   if task.complexity == "simple":
       model = "claude-haiku"
   else:
       model = "claude-sonnet-4"
   ```

3. Implement token budgets
   ```python
   if total_tokens > budget:
       raise BudgetExceededError()
   ```

---

## Advanced Topics

### Parallel Execution with Git Worktrees

Combine orchestration with git worktrees for true parallelism:

```python
# Create worktree for each agent
for agent in agents:
    create_worktree(f"worktrees/{agent.id}", agent.branch)

# Run agents in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(run_agent, agent, f"worktrees/{agent.id}"): agent
        for agent in agents
    }

    for future in as_completed(futures):
        agent = futures[future]
        result = future.result()
        process_agent_result(agent, result)
```

---

### Event-Driven Coordination

Use events instead of polling:

```python
# Agent emits events
agent.on("blocker", lambda blocker: notify_manager(blocker))
agent.on("complete", lambda result: update_state(result))
agent.on("question", lambda q: route_to_manager(q))

# Manager responds to events
manager.on("blocker_notification", resolve_blocker)
manager.on("task_complete", check_dependencies)
```

---

## Future Enhancements

### Planned Features

- [ ] WebSocket support for real-time coordination
- [ ] Multi-provider support (Claude + GPT-4 in same team)
- [ ] Visual dashboard for monitoring agents
- [ ] Automatic cost optimization
- [ ] Learning from past executions
- [ ] Agent performance metrics

---

## Contributing

Have improvements to the orchestration scripts? Please:

1. Test thoroughly
2. Add documentation
3. Include examples
4. Submit PR with clear description

---

## Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PRACTICAL_WORKFLOW_GUIDE.md](../../PRACTICAL_WORKFLOW_GUIDE.md) - Human-coordinated alternative
- [PARALLEL_EXECUTION_GUIDE.md](../../PARALLEL_EXECUTION_GUIDE.md) - Parallel execution strategies

---

## Summary

Automated orchestration is powerful but complex. **Start with human-coordinated workflows** to understand multi-agent patterns, then graduate to automation when you need scale and have the engineering resources.

The scripts in this directory are starting points - customize them for your specific needs!
