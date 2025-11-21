# Custom Skill Template

This directory contains a template for creating custom project-specific skills.

## Quick Start

1. **Copy this template** to create a new skill:
   ```bash
   cp -r skills/custom/template skills/custom/your-skill-name
   ```

2. **Edit SKILL.md** with your skill's content:
   - Update the frontmatter (name, description)
   - Replace template sections with your content
   - Add concrete examples and instructions
   - Remove the "Notes for Skill Creators" section

3. **Add supporting resources** (optional):
   - `scripts/` - Executable code for deterministic operations
   - `references/` - Documentation to load as needed
   - `assets/` - Templates, icons, fonts, etc.

4. **Test your skill**:
   - Add to an agent configuration
   - Compose the agent
   - Validate with real tasks
   - Iterate based on results

## Template Structure

```
template/
├── SKILL.md              # Main skill file (comprehensive template)
├── scripts/              # For executable scripts
├── references/           # For documentation files
├── assets/              # For template files and resources
└── README.md            # This file
```

## What Makes a Good Skill?

### Essential Qualities

1. **Clear Purpose** - Agents know exactly when to use it
2. **Concise Instructions** - Include only what agents don't already know
3. **Concrete Examples** - Show real implementations, not just concepts
4. **Appropriate Specificity** - Match detail level to task requirements
5. **Progressive Disclosure** - Metadata first, details on-demand

### Common Use Cases for Custom Skills

- **Company-Specific Workflows** - Your organization's unique processes
- **Internal Tool Integration** - Proprietary tools and systems
- **Domain Expertise** - Industry-specific knowledge
- **Custom Frameworks** - Your team's specific tech stack
- **Business Logic** - Company policies and procedures
- **Project Patterns** - Recurring project-specific patterns

## Skill Creation Process

### 1. Define Scope

- What problem does this skill solve?
- When should agents use this skill?
- What knowledge or procedures should it contain?
- What resources does it need?

### 2. Gather Resources

- Collect existing documentation
- Identify reusable scripts or code
- Gather templates and examples
- Document common patterns

### 3. Structure Content

- Write clear, concise instructions
- Create concrete examples
- Document troubleshooting steps
- List best practices

### 4. Bundle Resources

- Add scripts for repetitive operations
- Include reference documentation
- Provide templates and assets
- Ensure everything is discoverable

### 5. Test and Iterate

- Test with target agents
- Monitor actual usage
- Refine based on feedback
- Update documentation

## Token Budget Guidelines

Keep your skill efficient:

- **Target**: 2,000-5,000 tokens for SKILL.md body
- **Metadata**: ~50-100 tokens (always loaded)
- **Supporting Resources**: Load on-demand (variable)
- **Total**: Aim for under 10,000 tokens including resources

**Optimization Tips**:
- Reference external docs instead of including everything
- Use concise examples that demonstrate key concepts
- Bundle repetitive code in scripts
- Load references only when needed

## Examples of Good Custom Skills

### Example 1: Company API Integration

```yaml
name: company-api-client
description: Guide for integrating with CompanyName's internal API. Use when building services that need to communicate with our internal systems. Includes authentication, request patterns, error handling, and common endpoints.
```

This skill would include:
- API authentication procedures
- Common request patterns
- Error handling strategies
- Scripts for generating client code
- Reference documentation for all endpoints

### Example 2: Deployment Workflow

```yaml
name: deployment-process
description: Step-by-step guide for deploying applications to CompanyName infrastructure. Use when preparing to deploy code to staging or production. Covers pre-deployment checks, deployment procedures, rollback steps, and validation.
```

This skill would include:
- Pre-deployment checklist
- Deployment commands and scripts
- Rollback procedures
- Validation and monitoring steps
- Incident response contacts

### Example 3: Code Review Standards

```yaml
name: code-review-standards
description: CompanyName's code review guidelines and checklist. Use when reviewing pull requests or preparing code for review. Includes quality gates, common issues, and review templates.
```

This skill would include:
- Review checklist
- Quality gate criteria
- Common issues and solutions
- PR template
- Escalation procedures

## Best Practices

### Do's

✓ Start with clear triggering keywords in description
✓ Use imperative form ("Do this") for instructions
✓ Provide concrete, runnable examples
✓ Include troubleshooting for common issues
✓ Test with real agent workflows
✓ Keep token count reasonable
✓ Version your skills
✓ Document changes

### Don'ts

✗ Include information agents already know
✗ Write vague, general guidance
✗ Provide only theoretical explanations
✗ Create overly complex mega-skills
✗ Skip testing with actual agents
✗ Exceed 10,000 tokens without good reason
✗ Forget to update documentation
✗ Leave placeholder content

## Integration with Agent Configurations

### Adding Your Skill to Agents

```yaml
# .ai-agents/config.yml
agents:
  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      - "skills/custom/your-skill-name"  # Your custom skill
    project_context:
      - ".ai-agents/context/architecture.md"
```

### Composing with Your Skill

```bash
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent backend_developer
```

## Troubleshooting

### Skill Not Loading

**Problem**: Skill not found during composition

**Solution**:
- Verify skill is in `skills/custom/your-skill-name/`
- Ensure `SKILL.md` exists in skill directory
- Check path in config.yml matches directory name
- Run compose script with `--library` flag if needed

### Agent Not Using Skill

**Problem**: Agent doesn't apply skill when expected

**Solution**:
- Improve skill description with clear triggering keywords
- Make "When to Use" section more specific
- Add relevant examples
- Verify skill is actually loaded in composed agent
- Test with explicit references to skill context

### Token Budget Exceeded

**Problem**: Composed agent exceeds token limits

**Solution**:
- Reduce skill content to essentials
- Move detailed documentation to references/
- Use more concise examples
- Consider splitting into multiple focused skills
- Load resources on-demand instead of including inline

## Additional Resources

- [Main Skills README](../../README.md) - Overview of skills system
- [Integration Guide](../../INTEGRATION.md) - Technical implementation details
- [Skills Catalog](../../CATALOG.md) - Available skills directory
- [Anthropic Skills Docs](https://docs.anthropic.com/en/docs/skills) - Official documentation
- [Anthropic Skills Repo](https://github.com/anthropics/skills) - Example skills

## Support

For help with creating custom skills:

1. Review this template thoroughly
2. Check the Integration Guide for technical details
3. Study example skills in the Anthropic repository
4. Test incrementally with real agent tasks
5. Consult your team for domain-specific guidance

---

**Ready to create your first custom skill?** Follow the Quick Start steps above and start enhancing your agents with project-specific capabilities!
