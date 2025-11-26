# Custom Skills Guide

## Introduction

### What Are Custom Skills?

Custom skills are project-specific or organization-specific knowledge modules that extend your agents with capabilities tailored to your unique workflows, tools, and processes. While Anthropic's skill library provides general-purpose capabilities (like webapp testing, API documentation, or code review), custom skills codify your team's specific:

- Deployment procedures
- Internal tool usage patterns
- Coding standards and conventions
- Business logic and domain knowledge
- Company-specific workflows

### When to Create Custom Skills vs. Using Anthropic Skills

**Use Anthropic Skills When:**
- The capability is general-purpose (testing, debugging, documentation)
- Best practices are industry-standard
- No company-specific context is required
- The skill exists in the Anthropic library

**Create Custom Skills When:**
- You have unique workflows or processes
- Internal tools or APIs need specific usage patterns
- Company policies or standards must be followed
- Domain-specific knowledge is required
- Anthropic skills don't cover your use case
- You need to override or extend Anthropic skills

**Example Decision Matrix:**

| Task | Use Anthropic Skill | Create Custom Skill |
|------|---------------------|---------------------|
| Write unit tests for Python code | Yes (python-testing) | No |
| Deploy to your company's internal Kubernetes cluster | No | Yes (custom deployment) |
| Review code for security issues | Yes (code-review) | Maybe (extend with company policies) |
| Create REST API endpoints | Yes (api-design) | Maybe (add company conventions) |
| Generate incident reports | No | Yes (company-specific format) |

### Benefits of Codifying Workflows as Skills

**Consistency:** Every agent follows the same procedures, reducing errors and variations.

**Knowledge Sharing:** Tribal knowledge becomes codified and accessible to all agents and team members.

**Onboarding:** New team members can use agents that already understand company processes.

**Evolution:** Update a skill once, and all agents using it benefit immediately.

**Automation:** Repetitive workflows become consistently executable without manual documentation lookup.

**Compliance:** Ensure regulatory or policy requirements are always followed.

## Creating Your First Custom Skill

### Step 1: Identify a Workflow to Codify

Start with a workflow that is:
- **Repetitive**: Done regularly by your team
- **Well-defined**: Clear steps and outcomes
- **Valuable**: Automating it saves significant time
- **Documented**: Existing docs you can convert to skill format

Good first candidates:
- Deployment checklists
- Code review criteria
- API endpoint creation procedures
- Database migration workflows

### Step 2: Gather Information

Collect:
1. **Existing documentation** - Wikis, runbooks, SOPs
2. **Common commands** - Scripts, CLI commands, API calls
3. **Examples** - Past PRs, completed tasks, successful outcomes
4. **Edge cases** - Known gotchas and troubleshooting steps
5. **Team input** - Review with experts who perform this workflow

### Step 3: Use the Template

Copy the template to create your skill:

```bash
cd /path/to/AI_agents
cp -r skills/custom/template skills/custom/your-skill-name
```

### Step 4: Fill in the Template

Work through each section systematically:

#### Frontmatter
```yaml
---
name: your-skill-name
description: Brief description with triggering keywords
version: 1.0.0
author: Your Name/Team
category: custom
token_estimate: ~2500
---
```

**Tips:**
- Name should be kebab-case, descriptive
- Description should include trigger words agents will recognize
- Token estimate: run `wc -w SKILL.md` and multiply by ~1.3

#### Purpose Section
Write 2-3 sentences explaining:
- What problem this solves
- What capabilities it provides
- Who benefits from it

#### When to Use This Skill
List 3-5 specific scenarios. Be concrete:

Good example:
- "When creating a new REST API endpoint that will be publicly accessible"
- "When deploying a service update to production during business hours"

Avoid vague examples:
- "When working with APIs"
- "When deploying code"

#### Instructions
Break the workflow into 3-5 clear steps. Use imperative form:

Good:
```markdown
### Step 1: Verify Prerequisites

Check that all required tools are available:
- Run `kubectl version` to verify cluster access
- Confirm staging deployment succeeded
- Ensure rollback plan is documented
```

Avoid:
```markdown
### Step 1: Prerequisites

You should verify that prerequisites are met...
```

#### Examples
Provide at least 2 concrete examples:
1. **Basic example**: Common, straightforward scenario
2. **Advanced example**: More complex situation with edge cases

Include actual code, commands, or configuration.

### Step 5: Test Your Skill

Create a test agent configuration:

```yaml
# .ai-agents/config.yml
agents:
  test_agent:
    base: "base/software-developer.md"
    skills:
      - "skills/custom/your-skill-name"
```

Compose the agent:

```bash
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent test_agent \
  --output .ai-agents/composed/test_agent.md
```

Review the composed agent:

```bash
cat .ai-agents/composed/test_agent.md | grep -A 50 "your-skill-name"
```

Test with relevant tasks and iterate based on results.

### Step 6: Add to Your Project

Once tested, add the skill to your production agents:

```yaml
agents:
  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      - "skills/custom/your-skill-name"  # Your new skill
      - "skills/core/python-testing"     # Anthropic skills
    project_context:
      - ".ai-agents/context/architecture.md"
```

Recompose and deploy your agents.

## Custom Skill Examples

### Example 1: Production Deployment Workflow

**Scenario:** Your team deploys services to AWS ECS with specific safety checks and approval requirements.

**File:** `skills/custom/examples/deployment-workflow.md`

**Key Features:**
- Pre-deployment environment checks
- Staged rollout procedures
- Rollback triggers and steps
- Post-deployment validation
- Notification requirements

**Triggering scenarios:**
- "Deploy the user service to production"
- "Roll out version 2.3.0 to production"
- "Update production with the latest changes"

**Token estimate:** ~3,500 tokens

---

### Example 2: Code Review Checklist

**Scenario:** Your team has specific code review standards beyond general best practices.

**File:** `skills/custom/examples/code-review-checklist.md`

**Key Features:**
- Company-specific quality gates
- Security requirements (PII handling, authentication)
- Performance criteria (query limits, caching)
- Documentation standards
- Testing coverage requirements

**Triggering scenarios:**
- "Review this pull request"
- "Check if this code meets our standards"
- "Prepare this code for review"

**Token estimate:** ~2,800 tokens

---

### Example 3: API Endpoint Creator

**Scenario:** Your team follows specific conventions for REST API design and implementation.

**File:** `skills/custom/examples/api-endpoint-creator.md`

**Key Features:**
- URL structure conventions (`/api/v1/resource`)
- Standard error response format
- Authentication/authorization patterns
- Request/response validation
- OpenAPI documentation requirements
- Testing patterns for endpoints

**Triggering scenarios:**
- "Create a new API endpoint for user profiles"
- "Add a REST endpoint to fetch orders"
- "Implement the /api/v1/products endpoint"

**Token estimate:** ~3,200 tokens

---

### Example 4: Database Migration

**Scenario:** Your team uses Alembic/Flyway with specific safety procedures for database changes.

**File:** `skills/custom/examples/database-migration.md`

**Key Features:**
- Migration creation procedures
- Backward compatibility requirements
- Backup procedures before applying
- Staged application (dev → staging → prod)
- Rollback script requirements
- Data validation after migration

**Triggering scenarios:**
- "Create a database migration to add the user_preferences table"
- "Add a new column to the orders table"
- "Migrate the database schema for the new feature"

**Token estimate:** ~3,000 tokens

---

### Example 5: Incident Response

**Scenario:** Your team has a defined incident response process with communication templates and investigation steps.

**File:** `skills/custom/examples/incident-response.md`

**Key Features:**
- Severity classification
- Initial response checklist
- Communication templates (Slack, email, status page)
- Investigation procedures
- Mitigation strategies
- Post-incident review format

**Triggering scenarios:**
- "We have a production outage"
- "Users are reporting errors with authentication"
- "Handle this incident following our process"

**Token estimate:** ~3,500 tokens

## Best Practices for Custom Skills

### 1. Keep Skills Focused and Modular

**Do:** Create separate skills for distinct workflows
- `deployment-workflow` - Production deployment
- `staging-deployment` - Staging environment deployment
- `rollback-procedure` - Emergency rollback

**Don't:** Create mega-skills that try to do everything
- `deployment-and-rollback-and-monitoring-and-alerts` ❌

**Benefits:**
- Easier to maintain and update
- Lower token cost (load only what's needed)
- Better agent performance (clearer triggering)
- Reusable across different agents

### 2. Use Clear Step-by-Step Instructions

**Effective Format:**

```markdown
### Step 1: Verify Cluster Access

Check Kubernetes cluster connectivity:

1. Run `kubectl cluster-info` to verify connection
2. Confirm you're in the correct context: `kubectl config current-context`
3. Expected context: `arn:aws:eks:us-east-1:123456789:cluster/prod-cluster`

If connection fails:
- Check VPN connection
- Verify AWS credentials: `aws sts get-caller-identity`
- Contact DevOps if issues persist
```

**Why it works:**
- Concrete commands to run
- Expected outputs specified
- Error handling included
- Clear success criteria

### 3. Include Examples and Common Pitfalls

**Examples should be:**
- **Complete**: Runnable without modification
- **Realistic**: Based on actual usage
- **Annotated**: Comments explaining key points

**Common Pitfalls should include:**
- **Symptoms**: How to recognize the issue
- **Cause**: Why it happens
- **Solution**: How to resolve it
- **Prevention**: How to avoid it

### 4. Consider Token Budget

**Token Efficiency Strategies:**

1. **Core Instructions** (2,000-3,000 tokens)
   - Always loaded
   - Essential workflow steps
   - Key decision points

2. **Examples** (500-1,000 tokens)
   - Load for reference
   - Concrete demonstrations

3. **Supporting Resources** (variable)
   - Load on-demand
   - Detailed API docs
   - Extended troubleshooting

**Measuring Token Usage:**

```bash
# Rough estimate (words * 1.3)
wc -w skills/custom/your-skill-name/SKILL.md

# More accurate (use tiktoken)
python -c "import tiktoken; enc = tiktoken.get_encoding('cl100k_base'); print(len(enc.encode(open('skills/custom/your-skill-name/SKILL.md').read())))"
```

**Optimization Tips:**
- Reference external docs instead of including everything
- Use concise examples
- Bundle repetitive code in scripts
- Load detailed references only when needed

### 5. Version Control for Skills

**Version Numbering (Semantic Versioning):**

- **Major** (1.0.0 → 2.0.0): Breaking changes, workflow restructuring
- **Minor** (1.0.0 → 1.1.0): New features, additional examples, non-breaking updates
- **Patch** (1.0.0 → 1.0.1): Bug fixes, typos, clarifications

**Track Changes:**

```markdown
## Version History

### Version 1.2.0 (2025-01-15)
- Added rollback procedure for database migrations
- Updated validation steps for API v2
- Fixed error in backup command

### Version 1.1.0 (2024-12-10)
- Added examples for multi-region deployments
- Included troubleshooting for ECS task failures

### Version 1.0.0 (2024-11-01)
- Initial creation
- Core deployment workflow established
```

**Version Control Best Practices:**
- Commit skills to git with descriptive messages
- Tag releases: `git tag skill/deployment-workflow-v1.2.0`
- Document breaking changes clearly
- Maintain backward compatibility when possible

## Integration Patterns

### How Custom Skills Interact with Anthropic Skills

Custom skills complement Anthropic skills:

**Scenario:** Building a new REST API endpoint

**Skill Combination:**
1. **api-endpoint-creator** (custom) - Company conventions, URL structure, auth patterns
2. **api-design** (Anthropic) - General REST API best practices
3. **python-testing** (Anthropic) - Test creation for the endpoint
4. **code-review** (Anthropic) - General code review principles

**Agent behavior:**
- Uses custom skill for company-specific patterns
- Falls back to Anthropic skills for general best practices
- Combines both for comprehensive implementation

### Skills That Reference Other Skills

Skills can build on each other:

```markdown
## Related Skills

This skill works with:

- **database-migration**: Use after creating models to update the database schema
- **api-documentation**: Use to document the newly created endpoint
- **integration-testing**: Use to create end-to-end tests for the endpoint

**Typical Workflow:**
1. Use this skill (api-endpoint-creator) to scaffold the endpoint
2. Use database-migration if schema changes are needed
3. Use integration-testing to create comprehensive tests
4. Use api-documentation to update OpenAPI specs
```

### Conditional Skill Usage

Skills can guide agents on when to use other skills:

```markdown
## When to Use Additional Skills

**If adding authentication:**
Load the `auth-patterns` skill for company authentication standards.

**If handling PII:**
Load the `data-privacy` skill to ensure compliance with privacy policies.

**If this is a payment endpoint:**
Load the `payment-processing` skill for PCI compliance requirements.
```

## Testing Custom Skills

### How to Test a Skill Before Deploying

#### 1. Isolated Testing

Create a minimal test configuration:

```yaml
# test-config.yml
agents:
  skill_tester:
    base: "base/software-developer.md"
    skills:
      - "skills/custom/your-new-skill"
```

Compose:

```bash
python scripts/compose-agent.py \
  --config test-config.yml \
  --agent skill_tester \
  --output test-agent.md
```

Review the composed agent to verify:
- Skill loaded correctly
- No syntax errors
- Content makes sense in context

#### 2. Task-Based Testing

Use the skill with actual tasks:

```bash
# Use your preferred AI agent CLI
claude --agent test-agent.md "Create a new API endpoint for user profiles"
```

Observe:
- Does the agent reference the skill?
- Does it follow the procedures correctly?
- Are the outputs as expected?

#### 3. Comparative Testing

Test with and without the skill:

```bash
# Without skill
claude --agent base-agent.md "Deploy to production"

# With skill
claude --agent agent-with-skill.md "Deploy to production"
```

Compare approaches:
- Does the skill improve accuracy?
- Does it follow company procedures?
- Is the output more consistent?

### Iterating Based on Agent Usage

**Monitoring Usage:**

1. **Explicit References**: Does the agent mention using the skill?
2. **Procedure Adherence**: Does it follow the steps correctly?
3. **Edge Cases**: Does it handle exceptions properly?
4. **Token Efficiency**: Is the skill concise enough?

**Common Issues and Fixes:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| Skill not triggered | Agent doesn't use skill when it should | Improve description keywords |
| Incomplete usage | Agent starts but doesn't complete workflow | Clarify step boundaries |
| Wrong context | Agent uses skill inappropriately | Refine "When to Use" section |
| Token bloat | Composed agent too large | Move details to references |
| Confusion | Agent misinterprets instructions | Add more examples, clarify wording |

### Measuring Skill Effectiveness

**Qualitative Metrics:**

- **Accuracy**: Does the agent perform tasks correctly with the skill?
- **Consistency**: Do multiple agents use the skill the same way?
- **Completeness**: Does the agent complete all workflow steps?

**Quantitative Metrics:**

- **Usage frequency**: How often is the skill referenced?
- **Error reduction**: Fewer mistakes compared to without skill?
- **Time savings**: Faster task completion?

**Feedback Loop:**

1. Deploy skill to test agents
2. Monitor usage in real workflows
3. Collect feedback from team
4. Identify gaps or confusion
5. Update skill
6. Retest and redeploy

## Sharing Custom Skills

### When to Promote Custom Skills to the Library

Consider promoting a custom skill to the shared library when:

**Broad Applicability:**
- Multiple teams or projects can use it
- It solves a common problem
- Limited company-specific details

**High Quality:**
- Well-tested and proven effective
- Clear documentation
- Good examples
- Handles edge cases

**Maintainability:**
- Someone commits to maintaining it
- Updates can be coordinated
- Version management is clear

**Examples:**

| Keep as Custom | Promote to Library |
|----------------|-------------------|
| AWS deployment to your specific account/region | General AWS ECS deployment patterns |
| Your company's exact code review checklist | Code review framework adaptable by teams |
| Internal API client for proprietary system | REST API client creation patterns |

### Contributing Back to the Community

If your custom skill has broad appeal beyond your organization:

**1. Generalize the Skill**

Remove company-specific details:
- Replace company names with placeholders
- Generalize tool versions
- Abstract internal systems
- Remove proprietary business logic

**2. Document Thoroughly**

- Clear examples for multiple scenarios
- Comprehensive troubleshooting
- Explanation of design decisions
- Token budget guidance

**3. Test Broadly**

- Test with different projects
- Validate with different tech stacks
- Confirm examples work standalone

**4. Submit to Anthropic**

Follow contribution guidelines:
- Review Anthropic's skills repository
- Follow their format and conventions
- Submit PR with clear description
- Be responsive to feedback

### Licensing Considerations

**For Internal/Custom Skills:**
- Typically use company's default license
- May contain proprietary information
- Restricted to internal use

**For Library Skills:**
- Use permissive license (MIT, Apache 2.0)
- Ensure no proprietary details included
- Clear copyright and attribution
- Check company policy on open source contributions

**License Template:**

```markdown
---
name: your-skill-name
description: Skill description
version: 1.0.0
author: Your Name/Team
license: Apache 2.0
---
```

## Quick Reference

### Skill Creation Checklist

- [ ] Identified a well-defined, repetitive workflow
- [ ] Gathered existing documentation and examples
- [ ] Copied template to new skill directory
- [ ] Updated frontmatter (name, description, version)
- [ ] Wrote clear purpose statement (2-3 sentences)
- [ ] Listed specific "When to Use" scenarios
- [ ] Created step-by-step instructions in imperative form
- [ ] Included at least 2 concrete examples
- [ ] Documented common pitfalls and troubleshooting
- [ ] Listed related skills and integration points
- [ ] Estimated token budget
- [ ] Removed "Notes for Skill Creators" section
- [ ] Tested with isolated test agent
- [ ] Validated with real tasks
- [ ] Iterated based on usage
- [ ] Added to production agent configurations
- [ ] Documented in project skill catalog

### Common Commands

```bash
# Create new skill from template
cp -r skills/custom/template skills/custom/your-skill-name

# Estimate token usage (rough)
wc -w skills/custom/your-skill-name/SKILL.md

# Compose agent with skill
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent your_agent \
  --output .ai-agents/composed/your_agent.md

# Verify skill loaded
grep -A 20 "your-skill-name" .ai-agents/composed/your_agent.md

# Version and tag
git add skills/custom/your-skill-name/
git commit -m "feat: Add your-skill-name custom skill v1.0.0"
git tag skill/your-skill-name-v1.0.0
```

### Skill Type Decision Tree

```
Need to add capability to agent?
├─ Is it general-purpose and industry-standard?
│  ├─ Yes → Use Anthropic skill
│  └─ No → ↓
├─ Does it involve company-specific processes?
│  ├─ Yes → Create custom skill
│  └─ No → ↓
├─ Does it codify tribal knowledge or best practices?
│  ├─ Yes → Create custom skill
│  └─ No → ↓
└─ Is it already documented elsewhere?
   ├─ Yes → Reference in project context
   └─ No → Create custom skill
```

## Additional Resources

- **Template**: `/skills/custom/template/SKILL.md` - Comprehensive skill template
- **Template README**: `/skills/custom/template/README.md` - Template usage guide
- **Examples**: `/skills/custom/examples/` - Working skill examples
- **Integration Guide**: `/skills/PROJECT_INTEGRATION.md` - Project-specific skills
- **Quick Start**: `/skills/custom/QUICK_START.md` - 5-minute skill creation
- **Skills Catalog**: `/skills/CATALOG.md` - All available skills
- **Anthropic Docs**: [https://docs.anthropic.com/en/docs/skills](https://docs.anthropic.com/en/docs/skills)
- **Anthropic Skills Repo**: [https://github.com/anthropics/skills](https://github.com/anthropics/skills)

---

**Ready to enhance your agents with custom capabilities?** Start with the Quick Start guide, use the template, and create skills that codify your team's unique expertise!
