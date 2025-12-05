# AI Agents Library - Frequently Asked Questions

Your comprehensive guide to common questions about building, configuring, and using multi-agent software development teams.

**Version:** 1.0.0
**Last Updated:** 2025-11-21
**Status:** Production-Ready

---

## Quick Reference

**New to AI Agents?** Start here:
1. [What is the AI Agents Library?](#what-is-the-ai-agents-library) - Understanding the basics
2. [What's the fastest way to get started?](#whats-the-fastest-way-to-get-started) - Quick setup with templates
3. [Do I need programming experience?](#do-i-need-programming-experience-to-use-this-library) - No! See human-coordinated workflows
4. [How do agents communicate?](#how-do-agents-communicate-in-human-coordinated-mode) - Simple JSON file coordination

**Common Issues:**
- [Agent running out of context](#my-agent-is-running-out-of-context-what-should-i-do)
- [Token budget warnings](#the-token-budget-warnings-say-my-agent-is-over-recommended-size-how-do-i-fix-this)
- [Agents producing inconsistent results](#my-agents-are-producing-inconsistent-results-whats-wrong)
- [Debug agent not working](#how-do-i-debug-when-an-agent-isnt-working-correctly)

---

## Table of Contents

- [Getting Started](#getting-started)
- [Setup & Installation](#setup--installation)
- [Multi-Agent Coordination](#multi-agent-coordination)
- [Skills & Customization](#skills--customization)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

---

## Getting Started

### What is the AI Agents Library?

The AI Agents Library is a comprehensive framework for building multi-agent software development systems. Instead of manually crafting prompts for each project, it provides reusable, composable AI agent prompts that work together as a coordinated team.

Think of it as a "developer team in a box" - you get specialized agents (frontend developer, backend developer, QA tester, manager) that can collaborate on complex software projects using structured communication and proven patterns.

**Key benefits:**
- Modular, reusable agent prompts
- Skills integration for specialized capabilities
- Human-coordinated or automated workflows
- Advanced context management
- Git-based branch isolation to prevent conflicts

### Do I need programming experience to use this library?

Not necessarily! The library supports two approaches:

**No programming required:**
- Use the human-coordinated workflow where you manually run agents and relay information
- Works with any LLM tool (Claude Code, ChatGPT, etc.)
- Perfect for 90% of users
- See [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) for step-by-step instructions

**Programming helpful:**
- For fully automated multi-agent orchestration
- For custom tooling and integrations
- For advanced customizations

Start with human-coordinated workflows - they're practical, cost-effective, and work immediately.

**Related:** [How do agents communicate in human-coordinated mode?](#how-do-agents-communicate-in-human-coordinated-mode), [What's the difference between human-coordinated and automated workflows?](#whats-the-difference-between-human-coordinated-and-automated-workflows)

### What LLM providers are supported?

The library works with any LLM that supports:
- Sufficient context window (recommended: 100k+ tokens)
- Function/tool calling capabilities
- Markdown-formatted prompts

**Tested with:**
- **Anthropic Claude Sonnet 4.5** (recommended - 200,000 token context window)
- OpenAI GPT-4 and GPT-4 Turbo (128,000 token context)
- Other providers with similar capabilities

**Recommended:** Claude Sonnet 4.5 provides the best balance of capability and context size. The 200,000 token context window allows for comprehensive agent prompts (~6,000-12,000 tokens) while leaving ample room for conversation (~188,000+ tokens).

### How do I know if this library is right for my project?

This library is excellent for:

**Project types:**
- Web applications (React, Vue, Angular + Node.js)
- Mobile apps (React Native, Flutter, native)
- API services and microservices
- Full-stack systems
- Data pipelines

**Team situations:**
- Solo developers wanting systematic agent collaboration
- Small teams wanting AI augmentation
- Projects needing consistent coding standards
- Complex features requiring specialized expertise

**Not ideal for:**
- Simple, single-file scripts (too much overhead)
- Projects where you want a single general-purpose agent
- Real-time collaborative editing (not supported)

---

## Setup & Installation

### What's the fastest way to get started?

Use the **starter templates** for instant setup (5 minutes):

```bash
# Navigate to your project
cd your-project

# Run the template generator
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive

# Or specify directly
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

This creates a complete `.ai-agents/` directory with:
- Pre-configured context files (architecture, API contracts, coding standards)
- Ready-to-use agent configurations
- Comprehensive documentation
- All necessary directory structure

See [starter-templates/README.md](starter-templates/README.md) for complete details.

**Related:** [What's the difference between starter templates and manual setup?](#whats-the-difference-between-starter-templates-and-manual-setup), [What files should I commit to git?](#what-files-should-i-commit-to-git)

### Where should I place the .ai-agents/ directory?

**Simple rule: `.ai-agents/` goes next to `.git/`** - place it at your repository root.

**Examples:**

Standard repository:
```
my-project/              ← Repository root
├── .git/
├── .ai-agents/          ✅ Place here
├── src/
└── package.json
```

Code in subdirectory:
```
my-project/              ← Repository root
├── .git/
├── .ai-agents/          ✅ Place here (NOT in app/)
├── app/                 ← Code lives here
│   ├── src/
│   └── package.json
└── README.md
```

Monorepo with single team:
```
monorepo/                ← Repository root
├── .git/
├── .ai-agents/          ✅ Single shared setup
└── packages/
    ├── frontend/
    ├── backend/
    └── mobile/
```

Monorepo with per-package teams:
```
monorepo/
├── .git/
└── packages/
    ├── frontend/
    │   └── .ai-agents/  ✅ Per-package setup
    ├── backend/
    │   └── .ai-agents/  ✅ Per-package setup
    └── mobile/
        └── .ai-agents/  ✅ Per-package setup
```

**Why?** The library uses relative paths from repository root. Configuration references like `context/architecture.md` assume `.ai-agents/` is at the root.

See [README.md - Where to Place .ai-agents/](README.md#where-to-place-ai-agents) for detailed scenarios.

### What's the difference between starter templates and manual setup?

**Starter Templates (Recommended):**
- ✅ Instant setup in 5 minutes
- ✅ Pre-configured context files for your project type
- ✅ Best practices built-in
- ✅ Ready-to-use agent configurations
- ✅ Perfect for existing projects

**Manual Setup:**
- ⚠️ More control over structure
- ⚠️ Requires understanding of library architecture
- ⚠️ More time-consuming (30+ minutes)
- ⚠️ Better for highly custom requirements
- ⚠️ Perfect for new, greenfield projects

**Recommendation:** Start with templates. You can always customize afterwards.

### What files should I commit to git?

**DO commit:**
```bash
.ai-agents/context/           # Your project context
.ai-agents/config.yml         # Agent configuration
.ai-agents/workflows/         # Custom workflows
.ai-agents/.gitignore         # Git ignore rules
.ai-agents/README.md          # Documentation
```

**DON'T commit:**
```bash
.ai-agents/state/             # Runtime agent state
.ai-agents/checkpoints/       # Conversation checkpoints
.ai-agents/composed/          # Generated agent prompts
.ai-agents/memory/            # Agent memory/cache
```

The starter templates include a `.ai-agents/.gitignore` that handles this automatically.

**Tip:** Think of it like this - commit your configuration and context (the "source"), but not generated outputs or runtime state.

**Related:** [Where should I place the .ai-agents/ directory?](#where-should-i-place-the-ai-agents-directory), [How do I update the library without breaking my existing setup?](#how-do-i-update-the-library-without-breaking-my-existing-setup)

---

## Multi-Agent Coordination

### What's the difference between human-coordinated and automated workflows?

**Human-Coordinated (Recommended for 90% of users):**

What it is: You manually run agents in sequence and relay information between them.

```
You → Manager Agent (creates task plan)
You → Backend Agent (works on TASK-001)
You → Frontend Agent (works on TASK-002, you relay backend's progress)
You → Manager Agent (coordinates integration)
```

**Tools:** Claude Code, ChatGPT, or any LLM tool
**Communication:** Agents write status to `.ai-agents/state/team-communication.json`, you read and relay
**Best for:** Most users, small-medium teams (1-5 agents), learning multi-agent patterns

**Fully Automated (Advanced users):**

What it is: Programmatic orchestration system running multiple agents via LLM APIs.

```python
orchestrator.assign_task("TASK-001", backend_agent)
orchestrator.assign_task("TASK-002", frontend_agent)
# Agents run in parallel, communicate automatically
```

**Tools:** Custom Python scripts, LLM APIs, message queues
**Communication:** Direct agent-to-agent messaging via message queue

### What are the three state files and when do I use each?

The system uses **three complementary JSON files** for different coordination needs:

**1. `team-communication.json` - Real-Time Coordination**
- **Purpose:** Live communication within a single session
- **Used for:** Task assignments, status updates, agent requests
- **Lifespan:** Within session (can be cleared between sessions)
- **Example:** Manager assigns TASK-001 to backend-dev

**2. `session-progress.json` - Cross-Session Continuity**
- **Purpose:** Resume work across sessions without rediscovery
- **Used for:** Tracking completed/active tasks, blockers, next priorities
- **Lifespan:** Persistent across all sessions
- **Example:** "Last session completed AUTH-001, AUTH-002 is active, next: TASK-001"
- **Benefit:** 50% faster startup - skip redundant planning

**3. `feature-tracking.json` - Feature Verification**
- **Purpose:** Detailed feature status with pass/fail tracking
- **Used for:** Prevent premature "done", enforce E2E testing, show progress
- **Lifespan:** Persistent through project lifecycle
- **Example:** "6/8 features passing, 1 in progress, 0 failing"

**Quick Rule:**
- **Within session:** Use `team-communication.json`
- **End of session:** Update `session-progress.json` and `feature-tracking.json`
- **Resume session:** Read `session-progress.json` first

**Mode Usage:**
- **Simple Mode:** `team-communication.json` only
- **Complex Mode:** All three for full tracking

**See:** [docs/guides/LONG_RUNNING_AGENTS.md](../guides/LONG_RUNNING_AGENTS.md) for complete workflows

### Do I need all three state files?

**No!** It depends on your workflow mode:

**Simple Mode (90% of projects):**
- Required: `team-communication.json` only
- Optional: Other files if you want session continuity
- Best for: Quick tasks, prototypes, one-day projects

**Complex Mode (10% of projects):**
- Required: All three files
- Benefit: Full session continuity and progress tracking
- Best for: Multi-day projects, long-running development, complex features

**Start simple:** Begin with just `team-communication.json`. Add the other files when you need cross-session continuity.

### How do I resume work from a previous session?

**With session-progress.json (recommended):**

1. **Manager reads state files:**
   ```bash
   # Read session-progress.json
   {
     "last_session": "2025-12-03",
     "completed_tasks": ["AUTH-001"],
     "active_tasks": ["AUTH-002"],
     "next_priorities": ["AUTH-002", "TASK-001"]
   }

   # Read feature-tracking.json
   {
     "summary": {
       "passing": 1,
       "in_progress": 1,
       "failing": 0
     }
   }
   ```

2. **Manager immediately continues:**
   - No re-planning needed
   - No rediscovery of "what's done"
   - Direct to AUTH-002
   - Result: 50% faster startup

**Without state files (manual approach):**
- Review git commits
- Ask agents what they remember
- Re-read task files
- Manually reconstruct state
- Result: 15-20 minutes wasted

**Tip:** Always update `session-progress.json` at end of session with clear notes about what's next.

### When should features be marked "passing" in feature-tracking.json?

**Only when ALL criteria are met:**

1. ✅ **Code implemented** - Feature functionality complete
2. ✅ **Unit tests written** - Code-level tests passing
3. ✅ **E2E tests passing** - User-facing behavior verified (mandatory!)
4. ✅ **Code reviewed** - Senior Engineer approval (in Complex Mode)
5. ✅ **Integration verified** - Works with rest of system

**Anti-pattern:** Marking "passing" after just implementation
- This leads to bugs discovered later
- Wastes time with back-and-forth fixes
- Defeats the purpose of status tracking

**Best practice:** Use intermediate statuses
- `not_started` → `in_progress` → `testing` → `passing`
- Or: `in_progress` → `implemented` → `tested` → `passing`

**E2E Testing Requirement:**
In Complex Mode, the Senior Engineer **blocks** merges if E2E tests are missing. This enforces quality gates.

**See:** Phase 2 in [docs/guides/LONG_RUNNING_AGENTS.md](../guides/LONG_RUNNING_AGENTS.md#phase-2-e2e-testing-mandate)
**Best for:** Large projects (5+ agents), CI/CD automation, true parallel execution

**Key differences:**

| Aspect | Human-Coordinated | Fully Automated |
|--------|-------------------|-----------------|
| Setup | Simple | Complex (custom code) |
| Control | Full visibility | Less direct control |
| Speed | Sequential | True parallel |
| Cost | Lower (one at a time) | Higher (multiple APIs) |
| Learning curve | Low | High |

See [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) for human-coordinated tutorial.

### How do agents communicate in human-coordinated mode?

Agents communicate through a shared JSON file: `.ai-agents/state/team-communication.json`

**The workflow:**

1. **Manager writes** task assignments to the file
2. **You read** the file and start the appropriate agent
3. **Agent reads** the file, sees their assignment, works on it
4. **Agent writes** progress updates back to the file
5. **You read** the updates and relay to other agents as needed
6. **Manager coordinates** integration based on all agent updates

**Example update:**
```json
{
  "agent_updates": [
    {
      "timestamp": "2025-11-21T10:30:00Z",
      "agent_id": "backend-dev",
      "task_id": "TASK-001",
      "status": "in_progress",
      "progress": 60,
      "message": "JWT service implemented, working on auth middleware",
      "completed_items": ["Created src/services/jwt.ts", "..."],
      "blockers": [],
      "questions_for_manager": []
    }
  ]
}
```

You act as the coordinator, ensuring information flows between agents. This gives you full control and visibility while maintaining the benefits of specialized agents.

**Related:** [What's the difference between human-coordinated and automated workflows?](#whats-the-difference-between-human-coordinated-and-automated-workflows), [How many agents should I use?](#how-many-agents-should-i-use)

### How do I prevent agents from creating conflicts?

The library uses **branch isolation** to prevent conflicts:

**Branch naming convention:**
```
feature/<feature-name>/agent/<agent-role>/<specific-task>

Examples:
✓ feature/user-auth/agent/frontend-dev/login-form
✓ feature/user-auth/agent/backend-dev/jwt-service
✓ bugfix/memory-leak/agent/mobile-dev/profile-fix
```

**How it works:**
- Each agent works on their own isolated branch
- No two agents modify the same files simultaneously
- Manager coordinates integration after agents complete
- Merge conflicts are eliminated at the source

**Integration process:**
```bash
# Manager creates integration branch
git checkout -b feature/user-auth

# Merge each agent's work in order
git merge feature/user-auth/agent/backend-dev/jwt-service
git merge feature/user-auth/agent/frontend-dev/login-form
git merge feature/user-auth/agent/qa/tests

# Test integration
npm test

# Merge to main when ready
git checkout main
git merge feature/user-auth
```

**Additional safeguards:**
- API contracts defined upfront (frontend and backend agree on interfaces)
- Resource locking in communication file (soft locks on shared files)
- Manager reviews all integrations before merging

### How many agents should I use?

**Start small and scale:**

**Solo developer (1-2 agents):**
- Start with just 1 developer agent
- Add manager when complexity increases
- Cost-effective, easy to manage

**Small team (2-4 agents):**
- Manager for coordination
- 1-2 specialized developers (frontend, backend)
- QA tester for quality assurance
- Typical for most projects

**Medium team (4-6 agents):**
- Manager
- Multiple specialized developers (frontend, backend, mobile)
- QA tester
- Architect for complex features
- Best for larger features or applications

**Large team (7+ agents):**
- Full team including DevOps, documentation specialists
- Consider fully automated orchestration
- Requires careful coordination

**General rule:** Only add agents when you have distinct, specialized work that benefits from role separation. More agents = more coordination overhead.

**Related:** [How do I prevent agents from creating conflicts?](#how-do-i-prevent-agents-from-creating-conflicts), [What's the best practices for scaling from a few agents to a large team?](#what-are-the-best-practices-for-scaling-from-a-few-agents-to-a-large-team)

---

## Skills & Customization

### What are Anthropic Skills and how do they work?

**Anthropic Skills** are modular instruction packages that extend AI agent capabilities with specialized knowledge, workflows, and tool integrations.

Think of skills as "training manuals" - they teach agents how to perform specific tasks more effectively.

**How they enhance agents:**

```
Complete Agent = Base + Platform + Skills + Tools + Context

Example Frontend Developer:
├── Base: software-developer.md (universal engineering)
├── Platform: web/frontend-developer.md (React expertise)
├── Skills: artifacts-builder, theme-factory (specialized workflows)
├── Tools: git-tools.md, testing-tools.md (actions available)
└── Context: architecture.md, coding-standards.md (project specifics)
```

**Available skill categories:**
- **Core Development:** artifacts-builder, webapp-testing, mcp-builder, skill-creator
- **Communication:** internal-comms (team updates, reports)
- **Design:** theme-factory, algorithmic-art, canvas-design
- **Documents:** docx, pdf, xlsx, pptx (document manipulation)
- **Custom:** Your project-specific skills

**Key benefits:**
- Focused expertise in specific domains
- Improved task success rates
- Consistent application of best practices
- Reusable across agents and projects

See [SKILLS_GUIDE.md](SKILLS_GUIDE.md) for comprehensive details.

**Related:** [How many skills should I assign to each agent?](#how-many-skills-should-i-assign-to-each-agent), [What's the difference between skills, tools, and platform augmentations?](#whats-the-difference-between-skills-tools-and-platform-augmentations)

### How many skills should I assign to each agent?

**Recommended: 1-3 skills per agent**

**Guidelines:**
- **0 skills:** Valid for simple, general-purpose agents
- **1-2 skills:** Ideal for most production agents (6,000-9,000 tokens)
- **3-4 skills:** Acceptable for specialized roles (9,000-15,000 tokens)
- **5+ skills:** ⚠️ Approaching token limits - carefully justify each

**Example configurations:**

**Frontend Developer (Standard):**
```yaml
frontend_developer:
  skills:
    - "core/artifacts-builder"   # Component building
    - "design/theme-factory"     # UI styling
# Total: ~6,000 tokens for skills
```

**Project Manager (Advanced):**
```yaml
project_manager:
  skills:
    - "communication/internal-comms"  # Team updates
    - "documents/xlsx"                # Metrics tracking
    - "documents/docx"                # Documentation
    - "documents/pptx"                # Presentations
# Total: ~14,000 tokens (approaching limit)
```

**Token budget considerations:**
- **Claude Sonnet 4.5:** 200,000 total context
- **Recommended agent prompt:** 6,000-12,000 tokens (3-6% of context)
- **Conversation space:** 188,000-194,000 tokens (94-97% of context)

Going over 12,000 tokens is possible but leaves less room for conversation. The composition script (`compose-agent.py`) automatically warns you when approaching or exceeding recommended limits.

### What's the difference between skills, tools, and platform augmentations?

These are three distinct concepts that work together:

**Skills (Instruction Packages):**
- **What:** Markdown documents with workflows and best practices
- **Purpose:** Teach agents how to perform specialized tasks
- **Example:** `artifacts-builder` teaches React component creation
- **Token impact:** 2-5k tokens per skill
- **When loaded:** At composition time

**Tools (Function Definitions):**
- **What:** JSON schemas defining callable actions
- **Purpose:** Enable agents to perform specific operations
- **Example:** `file_read` allows reading file contents
- **Token impact:** Minimal (just schema)
- **When available:** Always accessible to agent

**Platform Augmentations (Knowledge Layers):**
- **What:** Markdown documents with platform-specific expertise
- **Purpose:** Add platform-wide knowledge (React, Node.js, etc.)
- **Example:** `frontend-developer.md` provides React/web expertise
- **Token impact:** 2-3k tokens per platform
- **When loaded:** At composition time, always active

**How they work together:**

Example: Frontend developer building a login form

1. **Base:** Software engineering fundamentals
2. **Platform:** Knows React, JSX, hooks, component patterns
3. **Skills:** Guides through creating interactive component (artifacts-builder)
4. **Tools:** Enables git commits, file operations, test execution
5. **Context:** Provides project-specific API endpoints

Result: Agent can build, style, test, and commit a login form following project standards.

### How do I create custom skills for my project?

Creating custom skills is straightforward:

**Step 1: Copy the template**
```bash
cd /path/to/AI_agents
cp -r skills/custom/template skills/custom/your-workflow-name
cd skills/custom/your-workflow-name
```

**Step 2: Edit SKILL.md**
```markdown
---
name: your-workflow-name
description: Brief description of what this skill does
license: MIT
---

# Your Workflow Name

## Overview
Brief overview of the workflow...

## When to Use This Skill
- Use case 1
- Use case 2

## Prerequisites
- Required knowledge
- Required tools

## Workflow Steps

### Step 1: Initial Setup
Detailed instructions...

### Step 2: Main Process
Detailed instructions...

## Examples
Concrete examples...

## Best Practices
Tips and recommendations...
```

**Step 3: Reference in config**
```yaml
agents:
  backend_developer:
    skills:
      - "core/mcp-builder"
      - "custom/your-workflow-name"  # Your custom skill
```

**Step 4: Compose and test**
```bash
cd /path/to/AI_agents
python scripts/compose-agent.py --config /path/to/your/project/.ai-agents/config.yml --agent backend_developer
```

**Good candidates for custom skills:**
- Repeated workflows specific to your organization
- Integration with proprietary systems
- Company-specific best practices
- Complex procedures needing consistency

See [SKILLS_GUIDE.md - Custom Skills](SKILLS_GUIDE.md#custom-skills) for detailed guidance.

---

## Troubleshooting

### My agent is running out of context. What should I do?

The library includes a **multi-tier memory architecture** with automatic warnings:

**Context Usage Thresholds:**

```
60% → Yellow Alert
      Begin progressive summarization

75% → Orange Alert
      Compress conversation history
      Create checkpoint
      Move old context to vector DB

85% → Red Alert
      Aggressive compression
      Emergency checkpoint
      Alert user

95% → Emergency
      Force compression to essentials
      Final checkpoint
      Immediate session restart required
```

**Immediate actions when you see warnings:**

1. **Create a checkpoint** - Save current state
2. **Compress old messages** - Summarize older conversation turns
3. **Remove non-essential context** - Temporarily drop less-critical information
4. **Restart with checkpoint** - Start fresh session, reload from checkpoint

**Long-term solutions:**

1. **Reduce agent complexity:**
   - Remove 1-2 skills
   - Consolidate context files
   - Split into more specialized agents

2. **Use progressive disclosure:**
   - Only include essential info in base prompt
   - Retrieve details from memory/RAG when needed

3. **Regular checkpoints:**
   - Every 10 turns
   - Before major operations
   - At 75% context usage

See [ARCHITECTURE.md - Context Management](ARCHITECTURE.md#context-management) for full details.

### How do I debug when an agent isn't working correctly?

**Systematic debugging approach:**

**1. Verify the composed prompt:**
```bash
# Check what's actually in the agent prompt
cat .ai-agents/composed/agent_name.md

# Look for skills loaded
grep "## Skill:" .ai-agents/composed/agent_name.md

# Check token count
cd .ai-agents/library
python scripts/compose-agent.py --config ../../config.yml --agent agent_name
# Output shows token usage and warnings
```

**2. Check agent configuration:**
```yaml
# Verify config.yml is correct
cat .ai-agents/config.yml

# Common issues:
# - Wrong file paths in project_context
# - Skills not found
# - Missing platform augmentations
```

**3. Review context files:**
```bash
# Ensure context files exist and have content
ls -la .ai-agents/context/
cat .ai-agents/context/architecture.md
cat .ai-agents/context/api-contracts.md
```

**4. Test with minimal configuration:**
```yaml
# Strip down to basics to isolate issue
test_agent:
  base: "base/software-developer.md"
  # Remove all skills, platforms, context
```

If minimal works, gradually add back components to find what's broken.

**5. Check communication file (for multi-agent):**
```bash
# Verify agents can read/write
cat .ai-agents/state/team-communication.json

# Common issues:
# - File permissions
# - JSON syntax errors
# - Agents not instructed to read file
```

**6. Review agent behavior:**
- Is agent following instructions?
- Is agent referencing skills/context correctly?
- Are there error messages in agent responses?

### The token budget warnings say my agent is over recommended size. How do I fix this?

**The warning looks like:**
```
⚠️ WARNING: Agent prompt exceeds recommended size!
Recommendation: 2,500 tokens over budget

Suggestions:
- Consider removing 2-3 skill(s)
- Review 4 project context files
```

**Optimization strategies:**

**Strategy 1: Remove least-used skills**
```yaml
# Before (14,500 tokens - over budget)
skills:
  - "core/artifacts-builder"      # Used frequently
  - "design/theme-factory"        # Used frequently
  - "core/webapp-testing"         # Rarely used
  - "design/canvas-design"        # Never used

# After (11,500 tokens - within budget)
skills:
  - "core/artifacts-builder"
  - "design/theme-factory"
# Moved webapp-testing to QA agent
# Removed canvas-design
```

**Strategy 2: Consolidate context files**
```bash
# Merge multiple small files into one
cat context/file1.md context/file2.md > context/combined.md
```

**Strategy 3: Create specialized agents**
```yaml
# Instead of one agent with all skills
super_developer:
  skills: [artifacts-builder, mcp-builder, webapp-testing, theme-factory]

# Create focused agents
ui_developer:
  skills: [artifacts-builder, theme-factory]

api_developer:
  skills: [mcp-builder]

test_engineer:
  skills: [webapp-testing]
```

**Strategy 4: Progressive addition**
```yaml
# Week 1: Start minimal
developer:
  base: "base/software-developer.md"
  platforms: ["platforms/web/frontend-developer.md"]
  # No skills yet - validate base functionality

# Week 2: Add essential skill
developer:
  skills: ["core/artifacts-builder"]  # Primary need

# Week 3: Add complementary skill if needed
developer:
  skills: ["core/artifacts-builder", "design/theme-factory"]
```

See [SKILLS_GUIDE.md - Token Budget Management](SKILLS_GUIDE.md#token-budget-management) for detailed strategies.

### My agents are producing inconsistent results. What's wrong?

**Common causes and solutions:**

**1. Ambiguous context:**
- **Problem:** Context files have vague or contradictory information
- **Solution:** Review and clarify context files
  - Be specific in architecture.md about tech stack
  - Provide concrete examples in coding-standards.md
  - Define clear API contracts

**2. Missing critical information:**
- **Problem:** Agents don't have enough context about the project
- **Solution:** Add essential context files
  - Current features and roadmap
  - Key architectural decisions
  - Important constraints

**3. Skills not being used:**
- **Problem:** Skill is loaded but agent doesn't reference it
- **Solution:**
  - Verify skill is actually loaded (check composed file)
  - Ensure task matches skill's use case
  - Improve skill instructions with concrete examples
  - Explicitly reference the skill in your prompt

**4. Token budget issues:**
- **Problem:** Agent is over-budget and losing context
- **Solution:** Reduce agent complexity (see previous FAQ)

**5. Conflicting guidance:**
- **Problem:** Multiple skills or context files provide contradictory advice
- **Solution:** Remove redundant skills or consolidate context

**Best practice:** Start minimal, add complexity gradually. Test each addition to ensure it improves rather than degrades performance.

---

## Advanced Topics

### Can I use this library with CI/CD automation?

Yes! The library supports automated workflows:

**Approach 1: Human-coordinated in CI/CD**
- Trigger specific agents via CI/CD pipeline
- Agent reads code, runs tests, generates reports
- Results posted back to PR/issue
- Human reviews and approves

**Approach 2: Fully automated orchestration**
- Custom Python orchestration scripts
- LLM API integration (Claude API, OpenAI API)
- Automated agent communication
- True parallel execution

**Example CI/CD integration:**

```yaml
# .github/workflows/agent-review.yml
name: Agent Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Compose QA Agent
        run: |
          cd .ai-agents/library
          python scripts/compose-agent.py --config ../../config.yml --agent qa_tester

      - name: Run Agent Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/orchestration/run-agent.py \
            --agent qa_tester \
            --task "Review this PR for quality and test coverage"

      - name: Post Results
        uses: actions/github-script@v6
        with:
          script: |
            // Post agent's findings as PR comment
```

See [scripts/orchestration/](scripts/orchestration/) for example implementations.

### How do I handle long-term project memory?

The library includes **RAG (Retrieval-Augmented Generation)** integration:

**Memory types:**

**1. Pinned Context (Always Available):**
- System prompt
- Current task details
- Critical constraints
- Active file context

**2. Working Memory (Recent):**
- Last 5-10 conversation turns (full detail)
- Relevant code snippets
- Recent decisions

**3. Long-Term Memory (Retrieved):**
- Architectural decisions (ADRs)
- Code patterns and solutions
- Troubleshooting history
- Requirements evolution

**Setting up RAG:**

```bash
# Create memory directory structure
mkdir -p .ai-agents/memory/{decisions,patterns,troubleshooting}

# Document architectural decisions
cat > .ai-agents/memory/decisions/adr-001-jwt-auth.md << EOF
# ADR-001: Use JWT for Authentication

## Status
Accepted

## Context
Need secure authentication for API endpoints...

## Decision
Use JWT tokens with 1-hour expiration...

## Consequences
- Stateless authentication
- Easy to scale horizontally
- Need refresh token mechanism for long sessions
EOF
```

**How agents use it:**
1. Agent encounters similar problem
2. System searches long-term memory
3. Relevant ADRs/patterns retrieved
4. Agent has context about past decisions
5. Consistency maintained across features

**Vector database integration:**
- Use embedding models to index memory
- Semantic search during agent sessions
- Automatic retrieval based on task context

See [ARCHITECTURE.md - Context Management](ARCHITECTURE.md#context-management) for full architecture.

### How do I update the library without breaking my existing setup?

**Safe update process:**

**1. Use git submodule (recommended):**
```bash
# Update library
cd .ai-agents/library
git fetch origin
git log HEAD..origin/main  # Review changes
git merge origin/main

# Update submodule reference
cd ../..
git add .ai-agents/library
git commit -m "chore: update AI agents library to vX.Y.Z"
```

**2. Test in staging first:**
```bash
# Recompose agents with updated library
cd .ai-agents/library
python scripts/compose-agent.py --config ../../config.yml --all

# Review token budgets and warnings
# Test with sample tasks before deploying to production
```

**3. Version pinning for stability:**
```yaml
# In config.yml
agent_library:
  repo: "git@github.com:org/AI_agents.git"
  version: "1.0.0"           # Pin to specific version
  update_strategy: "manual"  # Explicit updates only
```

**4. Review breaking changes:**
```bash
# Check CHANGELOG for breaking changes
cat .ai-agents/library/CHANGELOG.md

# Common breaking changes to watch for:
# - Schema changes in communication protocol
# - Skill updates with new requirements
# - Config.yml format changes
```

**5. Update gradually:**
- Update one agent at a time
- Test each agent after updating
- Roll back if issues occur
- Document any configuration changes needed

**Best practice:** Subscribe to library releases and review changes before updating. Test updates in development before production.

### What are the best practices for scaling from a few agents to a large team?

**Scaling progression:**

**Phase 1: Solo (1-2 agents)**
```yaml
# Simple setup
agents:
  developer:
    base: "base/software-developer.md"
    skills: ["core/artifacts-builder"]
```

**Characteristics:**
- Minimal overhead
- Quick iteration
- Learn the system

**Phase 2: Small Team (3-4 agents)**
```yaml
agents:
  team_manager:
    base: "base/manager.md"

  frontend_developer:
    skills: ["core/artifacts-builder", "design/theme-factory"]

  backend_developer:
    skills: ["core/mcp-builder"]

  qa_tester:
    skills: ["core/webapp-testing"]
```

**Add:**
- Structured communication (team-communication.json)
- API contracts for coordination
- Regular sync points

**Phase 3: Medium Team (5-7 agents)**
```yaml
# Add specialists
agents:
  # ... existing agents ...

  architect:
    skills: ["core/skill-creator", "core/mcp-builder"]

  mobile_developer:
    skills: ["design/theme-factory"]

  devops_engineer:
    skills: ["core/skill-creator"]
```

**Add:**
- More formal workflows
- Dedicated architecture planning
- Cross-platform coordination

**Phase 4: Large Team (8+ agents)**

**Consider:**
- Fully automated orchestration
- Message queue for agent communication
- Dedicated orchestrator (not just manager agent)
- Advanced metrics and monitoring

**Key scaling principles:**

1. **Add agents only for distinct roles** - Each agent should have clear, specialized responsibilities
2. **Increase coordination structure** - More agents = need more formal communication
3. **Monitor token budgets** - Total team token budget matters
4. **Progressive automation** - Move from human to automated coordination as team grows
5. **Specialize, don't generalize** - Focused agents with 1-3 skills work better than generalists

**Warning signs you need to scale up:**
- Single agent handling too many disparate tasks
- Frequent context overflows
- Long wait times between agent sessions
- Complex features requiring diverse expertise

**Warning signs you need to scale down:**
- Agents idle most of the time
- Excessive coordination overhead
- Simple tasks taking too long due to handoffs
- Duplicate work across agents

---

## Additional Resources

**Core Documentation:**
- [README.md](README.md) - Overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Comprehensive skills guide
- [PRACTICAL_WORKFLOW_GUIDE.md](PRACTICAL_WORKFLOW_GUIDE.md) - Human-coordinated tutorial
- [Context_Engineering.md](Context_Engineering.md) - Foundational principles

**Templates & Examples:**
- [starter-templates/README.md](starter-templates/README.md) - Template generator guide
- [examples/](examples/) - Reference implementations

**Support:**
- GitHub Issues - Bug reports and feature requests
- GitHub Discussions - Questions and community support
- Repository documentation - Comprehensive guides

---

## Still Have Questions?

**Can't find your answer?**
1. Check the relevant guide (README, ARCHITECTURE, SKILLS_GUIDE, etc.)
2. Review the examples/ directory for similar scenarios
3. Open a GitHub Discussion for community help
4. Submit a GitHub Issue if you've found a bug

**Want to improve this FAQ?**
- Submit a pull request with your question and answer
- Open an issue suggesting topics to add
- Share your experience in GitHub Discussions

---

**Last Updated:** 2025-11-21
**Version:** 1.0.0
**Maintained by:** AI Agents Library Contributors
