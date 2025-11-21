# Quick Start: Create Your First Custom Skill in 5 Minutes

This guide gets you from zero to a working custom skill in 5 minutes.

## Prerequisites

- AI Agents Library set up in your project
- A workflow you want to codify (deployment, code review, etc.)
- 5 minutes

## Step 1: Copy the Template (30 seconds)

```bash
# Navigate to your project's AI agents directory
cd .ai-agents

# Create your skill from template
cp -r library/skills/custom/template skills/custom/my-first-skill

# Or if library is elsewhere:
# cp -r /path/to/AI_agents/skills/custom/template skills/custom/my-first-skill
```

## Step 2: Update the Frontmatter (1 minute)

Open `skills/custom/my-first-skill/SKILL.md` and update the header:

```yaml
---
name: my-first-skill
description: Brief description of what this skill does and when to use it. Include trigger keywords agents will recognize.
version: 1.0.0
author: Your Name
category: custom
token_estimate: ~500
---
```

**Tips:**
- `name`: Use kebab-case, be descriptive
- `description`: Include words agents will see in user requests
- `version`: Start with 1.0.0
- `token_estimate`: Rough guess (refine later)

## Step 3: Fill in Key Sections (3 minutes)

### Purpose (30 seconds)

Replace the placeholder with 2-3 sentences:

```markdown
## Purpose

This skill provides [what it does]. It helps [who benefits] by [how it helps]. Use this when [key scenario].
```

**Example:**
```markdown
## Purpose

This skill provides step-by-step guidance for deploying our application to production. It helps developers and DevOps engineers by ensuring all safety checks are performed and proper procedures followed. Use this when deploying code changes to production servers.
```

### When to Use (1 minute)

List 3-5 specific scenarios:

```markdown
## When to Use This Skill

Use this skill when:

- [Specific scenario 1]
- [Specific scenario 2]
- [Specific scenario 3]

Do NOT use this skill when:

- [Anti-pattern 1]
- [Anti-pattern 2]
```

**Example:**
```markdown
## When to Use This Skill

Use this skill when:

- Deploying a new version to production
- Rolling back a problematic deployment
- Performing emergency hotfix deployment
- Deploying during maintenance window

Do NOT use this skill when:

- Deploying to development or staging (use simpler process)
- Making configuration-only changes (use config update process)
```

### Instructions (1 minute)

Provide 3-5 clear steps:

```markdown
## Instructions

### Step 1: [Preparation]

[What to do first]

```bash
# Example command
command --option
```

### Step 2: [Main Action]

[Core workflow step]

### Step 3: [Verification]

[How to confirm success]
```

**Example:**
```markdown
## Instructions

### Step 1: Pre-Deployment Checks

Verify tests passed and staging is healthy:

```bash
# Check CI status
gh run list --branch main --limit 1

# Verify staging
curl https://staging.api.com/health
```

### Step 2: Deploy to Production

Execute deployment:

```bash
kubectl set image deployment/app app=myapp:v2.1.0 -n production
kubectl rollout status deployment/app -n production
```

### Step 3: Verify Deployment

Check application health:

```bash
curl https://api.com/health
# Monitor error rates in dashboard
```
```

### Examples (30 seconds)

Add ONE simple example:

```markdown
## Examples

### Example 1: Standard Deployment

**Context:** Deploying bug fix to production

**Steps:**
1. Run pre-deployment checks
2. Deploy with kubectl
3. Verify health endpoints

**Outcome:** Deployment successful, no errors
```

## Step 4: Clean Up Template Sections (30 seconds)

**Remove or simplify** sections you don't need yet:
- Common Pitfalls (add later)
- Troubleshooting (add as you learn)
- "Notes for Skill Creators" section (always remove this)

Keep it simple for your first version. You'll expand as you use it.

## Step 5: Test Your Skill (1 minute)

Add to an agent config:

```yaml
# .ai-agents/config.yml
agents:
  test_agent:
    base: "base/software-developer.md"
    skills:
      - "skills/custom/my-first-skill"
    output: ".ai-agents/composed/test-agent.md"
```

Compose the agent:

```bash
cd .ai-agents
python library/scripts/compose-agent.py \
  --config config.yml \
  --agent test_agent

# Verify skill is included
grep -A 10 "my-first-skill" composed/test-agent.md
```

If you see your skill content, it worked!

## Step 6: Use and Iterate

Use the agent with tasks related to your skill:

```bash
# Test with relevant task
claude --agent composed/test-agent.md "Deploy the application to production"
```

Observe:
- Does the agent reference your skill?
- Does it follow your procedures?
- What's missing or unclear?

**Iterate:**
1. Update the skill based on usage
2. Recompose the agent
3. Test again
4. Repeat until effective

## Quick Reference Card

```markdown
# Minimum Viable Skill Checklist

- [ ] Copied template
- [ ] Updated frontmatter (name, description, version)
- [ ] Wrote purpose (2-3 sentences)
- [ ] Listed 3-5 "When to Use" scenarios
- [ ] Provided 3-5 instruction steps
- [ ] Included 1 simple example
- [ ] Removed "Notes for Skill Creators" section
- [ ] Added to test agent config
- [ ] Composed agent successfully
- [ ] Tested with relevant task
```

## Example: Complete 5-Minute Skill

Here's a complete skill created in 5 minutes:

```markdown
---
name: run-unit-tests
description: Run unit test suite for the project. Use when testing code changes, before committing, or during code review.
version: 1.0.0
author: QA Team
category: custom
token_estimate: ~800
---

# Run Unit Tests Skill

## Purpose

This skill provides instructions for running our project's unit test suite. It helps developers verify their changes don't break existing functionality before committing code.

## When to Use This Skill

Use this skill when:

- Testing code changes before committing
- Verifying a bug fix doesn't introduce regressions
- Running tests as part of code review
- Debugging test failures

Do NOT use this skill when:

- Running integration tests (use integration-test skill)
- Running E2E tests (use e2e-test skill)

## Instructions

### Step 1: Ensure Environment is Ready

Make sure dependencies are installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Verify test framework
pytest --version
```

### Step 2: Run Tests

Execute the test suite:

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_user.py
```

### Step 3: Review Results

Check test output:

```bash
# All tests should pass
# Coverage should be > 80%

# View coverage report
open htmlcov/index.html
```

## Examples

### Example 1: Running Tests Before Commit

**Context:** Made changes to user authentication module

**Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Run auth tests: `pytest tests/unit/auth/`
3. Verify all pass (25/25 passed)

**Outcome:** Tests pass, ready to commit
```

**Time to create:** 5 minutes
**Usefulness:** Immediately valuable
**Iterations:** Will expand based on usage

## Common Questions

### "My skill feels incomplete"

That's OK! Start simple and iterate. Add sections as you learn what's needed.

### "How do I know if it's working?"

Test it! If the agent references your skill and follows your procedures, it's working.

### "Should I include everything?"

No! Start with minimum viable skill. Add complexity only when needed.

### "How detailed should instructions be?"

Detailed enough for someone who knows the tools but not your specific process. If team members can follow it, agents can too.

### "What if I need to update it?"

Update anytime! Increment the version, document changes in Version History, recompose agents.

## Next Steps

After your first skill:

1. **Use it regularly** - Best feedback comes from actual usage
2. **Get team feedback** - Share with colleagues for input
3. **Add examples** - Document real usage scenarios
4. **Expand gradually** - Add troubleshooting, pitfalls as you encounter them
5. **Create more skills** - Apply what you learned to other workflows

## Resources

**For more depth:**
- [Custom Skills Guide](../CUSTOM_SKILLS_GUIDE.md) - Comprehensive guide
- [Template](template/SKILL.md) - Full template with all sections
- [Examples](examples/) - Production-ready example skills
- [Project Integration](../PROJECT_INTEGRATION.md) - Integrating into projects

**Quick commands:**

```bash
# Create skill
cp -r library/skills/custom/template skills/custom/my-skill

# Add to config
# Edit .ai-agents/config.yml, add to agent's skills list

# Compose agent
python library/scripts/compose-agent.py --config config.yml --agent my_agent

# Test
claude --agent composed/my_agent.md "Relevant task"
```

## 5-Minute Challenge

Can you create a useful skill in 5 minutes? Try it:

**Ideas for your first skill:**
- Deployment procedure
- Test running process
- Code review checklist
- Database backup process
- Monitoring dashboard setup
- Ticket creation workflow

**Set a timer and go!**

---

**Congratulations!** You've created your first custom skill. Now use it, iterate on it, and create more to enhance your agents' capabilities.

Remember: Perfect is the enemy of good. Start simple, make it useful, iterate based on real usage. Your skills will evolve with your team's needs.

Happy skill creating! 🚀
