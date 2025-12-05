# Best Practices

Guidelines for effective multi-agent development and prompt engineering.

---

## General Best Practices

Core principles for multi-agent workflows.

### 1. Start Simple

**Do:** Begin with one agent, add more as needed
- Test single agent workflows first
- Add complexity gradually
- Validate each addition

**Don't:** Start with 10 agents for a simple task

**Example:**
```
Bad:  Manager + 5 developers + 2 testers + architect (for login form)
Good: Single developer (for login form)
      → Add tester if needed
      → Add manager if coordinating 3+ agents
```

### 2. Define Interfaces First

**Do:** Create API contracts before implementation
- Document endpoints, schemas, types
- Share contracts with all agents
- Version control contracts

**Don't:** Let agents make incompatible assumptions

**Files:**
- `.ai-agents/context/api-contracts.md`
- `.ai-agents/context/data-models.md`

### 3. Use Branch Isolation

**Do:** One branch per agent per task
- Clear ownership
- Easy to review
- Prevents conflicts

**Pattern:**
```
feature/auth-backend-AUTH-001      (backend developer)
feature/auth-frontend-AUTH-002     (frontend developer)
feature/auth-tests-AUTH-003        (QA tester)
```

**Don't:** Multiple agents on same branch simultaneously

### 4. Monitor Context Usage

**Do:** Watch for context usage warnings
- Aim for <50% context usage
- Use checkpoints at 75%
- Offload to fresh agents via Task tool

**Don't:** Let single agent hit 90%+ context

**Tools:**
- `/whats-next` at 75% context
- Task tool delegation for fresh context

### 5. Regular Checkpoints

**Do:** Create checkpoints frequently
- Every 10 turns
- At 75% context
- After major milestones
- End of work session

**Don't:** Work straight through 100 turns without checkpoints

**Checkpoint Actions:**
- Save state to files
- Update session-progress.json
- Create /whats-next document
- Commit work

### 6. Enforce Quality Gates

**Do:** Require tests, reviews, coverage
- Unit tests for all code
- E2E tests in Complex Mode (mandatory)
- Code review by Senior Engineer
- Integration verification

**Don't:** Merge untested code

**Complex Mode Requirement:**
All 5 completion criteria must be met:
1. ✅ Code implemented
2. ✅ Unit tests written and passing
3. ✅ E2E tests written and passing
4. ✅ Code reviewed
5. ✅ Integration verified

### 7. Use Structured Communication

**Do:** Use JSON message protocol
- Clear message types
- Timestamps
- Task IDs
- Status tracking

**Don't:** Use free-form text in state files

**See:** [08-schemas.md](08-schemas.md) for schemas

---

## Skills Best Practices

Guidelines for skill assignment and usage.

### 8. Choose Skills Strategically

**Do:** Assign 1-3 skills per agent based on role
- Match skills to agent responsibilities
- Consider token budget
- Use deferred loading for 5+ skills

**Don't:** Assign 10 skills to every agent

**Token Budget:**
- Target: 20,000-30,000 tokens per agent
- Average skill: 2,500-4,500 tokens
- Leave room for actual work (15,000+ tokens)

**Example:**
```yaml
# Good
frontend_dev:
  skills:
    - web-artifacts-builder    # 3,500 tokens
    - frontend-design          # 3,200 tokens
  # Total: 6,700 tokens (33% of budget)

# Bad
frontend_dev:
  skills:
    - web-artifacts-builder
    - frontend-design
    - theme-factory
    - webapp-testing
    - mcp-builder
    - document-skills/pdf
  # Total: 22,000 tokens (110% of budget) ❌
```

### 9. Track Skill Effectiveness

**Do:** Monitor which skills improve outcomes
- Note when skills are actually used
- Track success rates with/without skills
- Remove unused skills

**Don't:** Load skills "just in case"

**Metrics:**
- Skill invocation count
- Task success rate with skill
- Token cost vs. benefit

### 10. Use Deferred Loading

**Do:** Defer loading for large skill libraries
- 10+ skills → definitely defer
- 5-9 skills → consider deferring
- Use trigger words strategically

**Don't:** Load all skills upfront if 5+

**See:** [07-advanced.md](07-advanced.md#1-deferred-skill-loading)

### 11. Consider Token Budget

**Do:** Plan token allocation
- Base agent: ~5,000-10,000 tokens
- Skills: ~2,500-4,500 tokens each
- Context: ~3,000-5,000 tokens
- Working memory: 15,000+ tokens

**Don't:** Exceed 30,000 tokens at-rest

**Total Budget:**
```
Base agent:        8,000 tokens
Skills (2):        7,000 tokens
Context (3 files): 4,000 tokens
---
At-rest total:    19,000 tokens
Working memory:   31,000 tokens available
```

---

## Advanced Best Practices

For optimized workflows and large-scale projects.

### 12. Use Prompt Caching

**Do:** Cache stable prompt components
- System prompts
- Base agent prompts
- Context files
- Skill definitions

**Don't:** Cache dynamic content

**Best For:**
- Repeated operations
- Batch processing
- CI/CD pipelines

**See:** [07-advanced.md](07-advanced.md#2-prompt-caching)

### 13. Use Programmatic Tools

**Do:** Generate code for multi-step workflows
- File analysis (5+ files)
- Batch operations
- Data processing

**Don't:** Use for single tool calls

**Benefits:**
- 37% token reduction
- Faster execution
- Cleaner context

**See:** [07-advanced.md](07-advanced.md#3-programmatic-tool-calling)

### 14. Atomic Tasks

**Do:** Break work into small, atomic tasks
- Better 10 small tasks than 3 large ones
- Each task = 1 clear deliverable
- Easy to verify completion

**Don't:** Create huge, multi-day tasks

**Good Task Size:**
```
AUTH-001: Implement registration endpoint (2-4 hours)
AUTH-002: Implement login endpoint (2-4 hours)
AUTH-003: Write E2E tests for auth (2-3 hours)
```

**Bad Task Size:**
```
AUTH-001: Build complete authentication system (5 days)
```

### 15. Use Fresh Context

**Do:** Use Task tool delegation to prevent Manager bloat
- Manager spawns agents
- Each agent gets fresh context
- Manager stays lean (15-25% context)

**Don't:** Let Manager accumulate all context

**Pattern:**
```
Manager (15% context)
  ↓ spawns via Task tool
IT Specialist (fresh context) → completes → reports back
  ↓ Manager spawns next
Backend Dev (fresh context) → completes → reports back
  ↓ Manager spawns next
QA Tester (fresh context) → completes → reports back
```

**See:** [05-workflows.md](05-workflows.md#2-task-tool-delegation-recommended---new-v110)

---

## XML Structure Best Practices

Guidelines for writing agent prompts and skills.

### Why XML?

**Token Efficiency:** ~25% token reduction vs. markdown
- `<role>` = 2 tokens vs. `## Role` = 3 tokens
- Better parsing by LLMs
- Clear semantic structure
- Consistent across all prompts

### Standard Tags

Use these tags consistently:

| Tag | Purpose | Example |
|-----|---------|---------|
| `<role>` | Agent identity and persona | Who the agent is |
| `<objective>` | What to accomplish | Primary goal |
| `<constraints>` | MUST/MUST NOT rules | Hard requirements |
| `<workflow>` | Step-by-step process | How to execute |
| `<quick_start>` | Immediate actions | First steps |
| `<success_criteria>` | Completion conditions | How to know when done |
| `<context>` | Background information | Supporting details |
| `<examples>` | Usage examples | Concrete scenarios |
| `<output_format>` | Expected output structure | Format specifications |

### XML Template

```xml
<role>
Agent identity and persona.

Define who this agent is, their expertise, and their mindset.
</role>

<objective>
What this agent needs to accomplish.

Clear, concise statement of the primary goal.
</objective>

<constraints>
<must>
- MUST follow requirement 1
- MUST validate all inputs
- MUST write tests for all code
</must>

<must_not>
- MUST NOT skip error handling
- MUST NOT commit without review
- MUST NOT ignore existing patterns
</must_not>
</constraints>

<workflow>
<step number="1">
<action>First action to take</action>
<details>
Explanation of how to perform this step.
</details>
</step>

<step number="2">
<action>Second action to take</action>
<details>
Explanation of how to perform this step.
</details>
</step>
</workflow>

<quick_start>
When first invoked:
1. Read state file from .ai-agents/state/team-communication.json
2. Identify your assigned task
3. Check out new branch: feature/[task-id]
4. Begin implementation
</quick_start>

<success_criteria>
This task is complete when:
- [ ] Code implemented and tested
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Branch merged to main
</success_criteria>

<examples>
<example>
<scenario>Implementing login endpoint</scenario>
<approach>
1. Read API contract from .ai-agents/context/api-contracts.md
2. Implement endpoint following contract
3. Write unit tests
4. Write E2E tests
5. Update team-communication.json with status
</approach>
</example>
</examples>

<output_format>
Upon completion, write to team-communication.json:
{
  "type": "status_update",
  "from": "[agent_id]",
  "task_id": "[task_id]",
  "status": "completed",
  "summary": "Brief description of work completed"
}
</output_format>
```

### XML Best Practices

**Do:**
- Use semantic tags (`<role>`, `<objective>`, not `<section1>`)
- Nest appropriately (`<constraints><must>` not `<must>` alone)
- Keep consistent indentation
- Use attributes sparingly (`<step number="1">`)
- Close all tags properly

**Don't:**
- Mix XML and Markdown (use pure XML)
- Use excessive nesting (3-4 levels max)
- Create custom tags without reason
- Use HTML tags (`<div>`, `<span>`)

### Token Efficiency Comparison

**Markdown:**
```markdown
## Role

You are a backend developer...

## Objective

Implement authentication endpoints...

## Constraints

### Must
- Follow API contracts
- Write tests

### Must Not
- Skip error handling
```
**Token Count:** ~45 tokens

**XML:**
```xml
<role>
You are a backend developer...
</role>

<objective>
Implement authentication endpoints...
</objective>

<constraints>
<must>
- Follow API contracts
- Write tests
</must>
<must_not>
- Skip error handling
</must_not>
</constraints>
```
**Token Count:** ~34 tokens

**Savings:** ~25% reduction

---

## Documentation Best Practices

### Essential Reading Order

1. **Start Here:** `README.md` - Overview and quick start
2. **Core Principles:** `Context_Engineering.md` - The "Holy Bible"
3. **Architecture:** `ARCHITECTURE.md` - System design
4. **Skills:** `SKILLS_GUIDE.md` - Skills selection

### For Specific Tasks

- **Multi-agent workflows:** `PRACTICAL_WORKFLOW_GUIDE.md`
- **Manager setup:** `prompts/manager-task-delegation.md`
- **Quick reference:** This cheat sheet
- **Debugging:** `/debug` command or `debug-like-expert` skill

---

## Common Pitfalls to Avoid

### 1. Context Overflow
❌ Letting single agent accumulate 100 turns of context
✅ Use Task tool delegation, /whats-next at 75%

### 2. Over-Engineering
❌ Adding features, abstractions, "improvements" not requested
✅ Only implement what's asked, keep solutions simple

### 3. Premature "Done"
❌ Marking features complete without E2E tests
✅ Enforce all 5 completion criteria in Complex Mode

### 4. Poor Communication
❌ Free-form text updates, unclear status
✅ Structured JSON messages with clear schema

### 5. Skill Overload
❌ Loading 10 skills per agent "just in case"
✅ Assign 1-3 skills based on actual need

### 6. Ignored Blockers
❌ Continuing work when blocked by dependencies
✅ Report blockers immediately, track in session-progress.json

### 7. No Branch Isolation
❌ Multiple agents working on same branch
✅ One branch per agent per task

### 8. Skipping Reviews
❌ Merging code without review (Complex Mode)
✅ Senior Engineer reviews all code, blocks without E2E tests

### 9. Lost Context
❌ No handoff document at session end
✅ Create /whats-next, update session-progress.json

### 10. Inconsistent Patterns
❌ Each agent using different conventions
✅ Define coding standards, API contracts upfront

---

## See Also

- **Workflows:** [05-workflows.md](05-workflows.md)
- **Skills:** [03-skills.md](03-skills.md)
- **Advanced Features:** [07-advanced.md](07-advanced.md)
- **State Files:** [01-state-files.md](01-state-files.md)

---

[← Back to Index](index.md) | [Previous: Schemas](08-schemas.md) | [Next: Reference →](10-reference.md)
