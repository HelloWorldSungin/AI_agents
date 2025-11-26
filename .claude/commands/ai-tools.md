---
description: Discover and explore available AI agent tools from AI_agents repo
---

<objective>
Help users discover and understand the AI agent tools available from the AI_agents repository.
</objective>

<available_tools>

### Prompt Engineering
  - `/create-prompt` - Create a new prompt that another Claude can execute
  - `/create-meta-prompt` - Create optimized prompts for Claude-to-Claude pipelines (research -> plan -> implement)
  - `/run-prompt` - Delegate one or more prompts to fresh sub-task contexts with parallel or sequential execution

### Agent Development
  - `/create-subagent` - Create specialized Claude Code subagents with expert guidance
  - `/create-agent-skill` - Create or edit Claude Code skills with expert guidance on structure and best practices
  - `/create-hook` - Invoke create-hooks skill for expert guidance on Claude Code hook development

### Slash Commands
  - `/create-slash-command` - Create a new slash command following best practices and patterns
  - `/audit-slash-command` - Audit slash command file for YAML, arguments, dynamic context, tool restrictions, and content quality
  - `/audit-skill` - Audit skill for YAML compliance, pure XML structure, progressive disclosure, and best practices
  - `/audit-subagent` - Audit subagent configuration for role definition, prompt quality, tool selection, XML structure compliance, and effectiveness
  - `/heal-skill` - Heal skill documentation by applying corrections discovered during execution with approval workflow

### Planning & Execution
  - `/create-plan` - Create hierarchical project plans for solo agentic development (briefs, roadmaps, phase plans)
  - `/run-plan` - Execute a PLAN.md file directly without loading planning skill context

### Debugging
  - `/debug` - Apply expert debugging methodology to investigate a specific issue

### Task Management
  - `/add-to-todos` - Add todo item to TO-DOS.md with context from conversation
  - `/check-todos` - List outstanding todos and select one to work on
  - `/whats-next` - Analyze the current conversation and create a handoff document for continuing this work in a fresh context

### Thinking Models
  - `/consider:first-principles` - Break down to fundamentals and rebuild from base truths
  - `/consider:5-whys` - Drill to root cause by asking why repeatedly
  - `/consider:swot` - Map strengths, weaknesses, opportunities, and threats
  - `/consider:inversion` - Solve problems backwards - what would guarantee failure?
  - `/consider:opportunity-cost` - Analyze what you give up by choosing this option
  - `/consider:second-order` - Think through consequences of consequences
  - `/consider:pareto` - Apply Pareto's principle (80/20 rule) to analyze arguments or current discussion

### Skills (invoke with Skill() tool)
  - `create-hooks` - Expert guidance for creating, configuring, and using Claude Code hooks. Use when working with hooks, setting up event listeners, validating commands, automating workflows, adding notifications, or understanding hook types (PreToolUse, PostToolUse, Stop, SessionStart, UserPromptSubmit, etc).
  - `create-meta-prompts` - Create optimized prompts for Claude-to-Claude pipelines with research, planning, and execution stages. Use when building prompts that produce outputs for other prompts to consume, or when running multi-stage workflows (research -> plan -> implement).
  - `create-slash-commands` - Expert guidance for creating Claude Code slash commands. Use when working with slash commands, creating custom commands, understanding command structure, or learning YAML configuration.
  - `debug-like-expert` - Deep analysis debugging mode for complex issues. Activates methodical investigation protocol with evidence gathering, hypothesis testing, and rigorous verification. Use when standard troubleshooting fails or when issues require systematic root cause analysis.
  - `create-agent-skills` - Expert guidance for creating, writing, building, and refining Claude Code Skills. Use when working with SKILL.md files, authoring new skills, improving existing skills, or understanding skill structure and best practices.
  - `create-plans` - Create hierarchical project plans optimized for solo agentic development. Use when planning projects, phases, or tasks that Claude will execute. Produces Claude-executable plans with verification criteria, not enterprise documentation. Handles briefs, roadmaps, phase plans, and context handoffs.
  - `create-subagents` - Expert guidance for creating, building, and using Claude Code subagents and the Task tool. Use when working with subagents, setting up agent configurations, understanding how agents work, or using the Task tool to launch specialized agents.

</available_tools>

<usage>
**Run a command:**
```
/create-prompt [your task description]
/debug [error or symptom]
/consider:first-principles [problem to analyze]
```

**Invoke a skill:**
```
Use the Skill() tool: Skill(create-plans)
```

**Get help:**
```
/ai-tools - Show this list
```
</usage>

<source>
These tools come from: /Users/sunginkim/GIT/AI_agents

To update or customize, edit the source files directly.
</source>
