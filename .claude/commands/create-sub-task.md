---
description: Create and spawn a sub-task agent with standardized prompt
argument-hint: <task> [--role <role>] [--phase <phase>] [--requirements <requirements>] [--preview]
allowed-tools: [Task, Read]
---

# Create Sub-Task Command

This command generates a standardized agent prompt and spawns it via the Task tool for delegation.

## How It Works

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **task** (required): First non-flag argument or all text before first flag
- **--role**: Agent role (Backend Developer, QA Tester, IT Specialist, Frontend Developer, DevOps, etc.)
- **--phase**: Which phase this task belongs to
- **--requirements**: Specific requirements or steps (can be multiline)
- **--preview**: Flag to show generated prompt before spawning

**Default values:**
- role: "Developer" if not specified
- phase: Not included if not specified
- requirements: Not included if not specified

### Step 2: Read Context

Read `.ai-agents/state/team-communication.json` to extract:
- `project_name`: For role setup
- Current session info for context

Generate task ID:
- If phase provided: Use format like "TASK-{phase-number}-{increment}"
- Otherwise: Use simple format "TASK-{increment}" (based on existing tasks)

### Step 3: Generate Standardized Prompt

Create prompt with the following structure:

```markdown
You are a {role} working on {project_name}.

## Your Assignment

**Task ID**: {task_id}
**Description**: {task_description}

## Critical File Locations

**Read these files BEFORE starting work:**

1. **Team Communication** (REQUIRED):
   - Path: .ai-agents/state/team-communication.json
   - Purpose: Task assignments, manager decisions, agent updates
   - Action: Read at session start, update at completion

2. **Project Context** (as needed):
   - Session Progress: .ai-agents/state/session-progress.json
   - Feature Tracking: .ai-agents/state/feature-tracking.json

**IMPORTANT**: Use exact paths above. Do not create alternative files.

## What to Implement

{task_description}

{requirements_section_if_provided}

{phase_context_if_provided}

## Update Protocol

When complete, update .ai-agents/state/team-communication.json:

Add to agent_updates array:
{
  "agent_id": "{role}-{task_id}",
  "task_id": "{task_id}",
  "status": "completed",
  "timestamp": "<ISO-8601 timestamp>",
  "summary": "Brief summary of what was accomplished",
  "deliverables": ["list", "of", "deliverables"],
  "blockers": []
}

## Success Criteria

{success_criteria_inferred_from_task}
```

**Template Variables:**

- `{role}`: From --role argument or "Developer"
- `{project_name}`: From team-communication.json
- `{task_id}`: Generated based on phase or simple increment
- `{task_description}`: From task argument
- `{requirements_section_if_provided}`: Only included if --requirements provided:
  ```
  ### Requirements

  {requirements text}
  ```
- `{phase_context_if_provided}`: Only included if --phase provided:
  ```
  ## Phase Context

  Current Phase: {phase}
  Reference: Check session-progress.json for phase details and dependencies
  ```
- `{success_criteria_inferred_from_task}`: Auto-generate based on task description (e.g., if task mentions "tests", add "All tests passing")

### Step 4: Handle Preview Mode

**If --preview flag present:**
1. Display the generated prompt
2. Show explanation: "This prompt will be used to spawn an agent via Task tool"
3. Ask user: "Proceed with spawning? (yes/no)"
4. If yes: Continue to Step 5
5. If no: Exit without spawning

**If no --preview:**
- Skip directly to Step 5

### Step 5: Spawn Agent via Task Tool

Delegate using Task tool:

```
description: "{first 3-5 words of task}"
subagent_type: "general-purpose"
prompt: "{generated_prompt_from_step_3}"
```

**Example descriptions:**
- "Run all unit tests" → "Run unit tests"
- "Validate API infrastructure" → "Validate API infrastructure"
- "Implement login form" → "Implement login form"

### Step 6: Confirm Spawning

After spawning, display:

```
✓ Agent spawned successfully

Task ID: {task_id}
Role: {role}
Agent will report back when complete.

Monitor progress in: .ai-agents/state/team-communication.json (agent_updates section)
```

## Examples

### Example 1: Simple Task
```bash
/create-sub-task "Run all unit tests" --role "QA Tester"
```

**Result:** Spawns QA Tester agent with basic prompt, task ID auto-generated.

### Example 2: Detailed Task with Requirements
```bash
/create-sub-task "Validate API infrastructure" --role "IT Specialist" --requirements "Check all 8 infrastructure points from it-specialist-agent.md"
```

**Result:** Spawns IT Specialist agent with requirements section included in prompt.

### Example 3: Preview Mode
```bash
/create-sub-task "Complex database migration" --role "Backend Developer" --preview
```

**Result:** Displays generated prompt, waits for confirmation before spawning.

### Example 4: With Phase Context
```bash
/create-sub-task "Implement login form" --role "Frontend Developer" --phase "Phase 2: Authentication UI"
```

**Result:** Spawns Frontend Developer agent with phase context section.

## Error Handling

**Missing task argument:**
```
Error: Task description is required.

Usage: /create-sub-task <task> [--role <role>] [--phase <phase>] [--requirements <requirements>] [--preview]

Example: /create-sub-task "Run tests" --role "QA Tester"
```

**Cannot read team-communication.json:**
```
Warning: Could not read .ai-agents/state/team-communication.json
Using default project name: "AI Agents Project"

Consider initializing state files if managing complex projects.
```

**User cancels in preview mode:**
```
Agent spawning cancelled. No task created.
```

## Notes

- This command is designed for manager delegation workflows
- The generated prompt includes automatic state file reading instructions
- Agents spawned by this command should follow the Update Protocol
- Task IDs help track work in team-communication.json
- Preview mode useful for complex or sensitive tasks
