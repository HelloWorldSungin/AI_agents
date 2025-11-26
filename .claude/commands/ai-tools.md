---
description: Discover and explore available AI agent tools from this repository
---

<objective>
Help users discover and understand the AI agent tools available in this repository.
Display available commands organized by category, with usage examples.
</objective>

<available_tools>

### Prompt Engineering
- `/create-prompt` - Create optimized prompts with XML structure
- `/create-meta-prompt` - Create prompts that generate other prompts
- `/run-prompt` - Execute a saved prompt file

### Agent Development
- `/create-subagent` - Create specialized sub-agents for Task tool
- `/create-agent-skill` - Create or edit Claude Code skills
- `/create-hook` - Create Claude Code hooks for automation

### Slash Commands
- `/create-slash-command` - Create new slash commands
- `/audit-slash-command` - Review slash commands for best practices
- `/audit-skill` - Audit skills for quality and structure
- `/audit-subagent` - Review sub-agent definitions
- `/heal-skill` - Fix issues in broken skills

### Planning & Execution
- `/create-plan` - Create hierarchical project plans
- `/run-plan` - Execute a saved plan file

### Debugging
- `/debug` - Systematic debugging workflow

### Task Management
- `/add-to-todos` - Add items to TODO list
- `/check-todos` - Review and select todos to work on
- `/whats-next` - Create handoff document for context continuation

### Thinking Models (`/consider:*`)
- `/consider:first-principles` - Break down to fundamentals
- `/consider:5-whys` - Root cause analysis
- `/consider:swot` - Strengths, weaknesses, opportunities, threats
- `/consider:devil-advocate` - Challenge assumptions
- `/consider:premortem` - Anticipate failure modes
- `/consider:inversion` - Think backwards from goals
- `/consider:socratic` - Question-driven exploration
- `/consider:red-team` - Adversarial analysis
- `/consider:steel-man` - Strengthen opposing arguments
- `/consider:opportunity-cost` - Evaluate trade-offs
- `/consider:second-order` - Consider downstream effects
- `/consider:pareto` - 80/20 analysis

### Multi-Agent Orchestration (Prompts)
Use these prompts with the Task tool for complex development:
- `prompts/manager-task-delegation.md` - Coordinate multi-agent development
- `prompts/senior-engineer-agent.md` - Code review and integration
- `prompts/it-specialist-agent.md` - Infrastructure validation

</available_tools>

<usage_examples>

**Create an optimized prompt:**
```
/create-prompt Build a user dashboard with analytics charts
```

**Debug an issue:**
```
/debug Tests failing with timeout errors in auth module
```

**Use a thinking model:**
```
/consider:first-principles Should we use microservices or monolith?
```

**Plan a complex feature:**
```
/create-plan Implement user authentication with OAuth
```

</usage_examples>

<setup_for_other_projects>

To use these tools in another project:

```bash
# Navigate to target project
cd /path/to/your/project

# Run setup script from AI_agents repo
python /path/to/AI_agents/scripts/setup-commands.py

# Or install globally
python /path/to/AI_agents/scripts/setup-commands.py --global
```

This creates minimal wrapper commands that redirect to the full implementations.

</setup_for_other_projects>
