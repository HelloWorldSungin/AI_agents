# Skills Integration

A curated collection of specialized skills that enhance agent capabilities for domain-specific tasks, workflows, and tool integrations.

**Version:** 1.0.0

---

## What are Skills?

Skills are modular instruction packages that extend AI agent capabilities with specialized knowledge, workflows, and tool integrations. Unlike tools (which are actions agents can perform), skills are domain-specific onboarding guides that transform agents into specialized experts.

### Skills vs Tools: Key Differences

| Aspect | Skills | Tools |
|--------|--------|-------|
| **Purpose** | Knowledge & workflows | Actions & operations |
| **Content** | Instructions, procedures, domain expertise | Function definitions, APIs |
| **Loading** | Dynamic, progressive disclosure | Static, always available |
| **Structure** | Markdown + resources (scripts, docs, assets) | JSON schemas, function signatures |
| **Usage** | Triggered by task context | Called explicitly by agents |

### What Skills Provide

1. **Specialized Workflows** - Step-by-step procedures for domain-specific tasks
2. **Tool Integrations** - Guidance for using external tools and APIs
3. **Domain Expertise** - Industry knowledge, best practices, business logic
4. **Bundled Resources** - Scripts, templates, documentation, assets

---

## Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md              # Main skill file (required)
│   ├── YAML frontmatter  # name, description, license
│   └── Markdown body     # Instructions and guidance
├── scripts/              # Executable code (optional)
├── references/           # Documentation (optional)
└── assets/               # Templates, icons, fonts (optional)
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Brief description of what the skill does and when to use it
license: Apache 2.0 (or other)
---

# Skill Instructions

Detailed instructions for using this skill...
```

---

## Skills Directory Organization

```
skills/
├── core/                 # Development & technical skills
│   ├── artifacts-builder/
│   ├── webapp-testing/
│   ├── mcp-builder/
│   └── skill-creator/
│
├── communication/        # Communication & documentation skills
│   └── internal-comms/
│
├── design/              # Design & creative skills
│   └── theme-factory/
│
├── documents/           # Document manipulation skills
│   ├── docx/
│   ├── pdf/
│   ├── xlsx/
│   └── pptx/
│
└── custom/              # Project-specific custom skills
    └── template/        # Template for creating new skills
```

---

## How to Use Skills in Agent Configurations

### 1. Reference Skills in config.yml

```yaml
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "skills/core/artifacts-builder"
      - "skills/design/theme-factory"
    project_context:
      - ".ai-agents/context/architecture.md"
```

### 2. Compose Agent with Skills

```bash
python scripts/compose-agent.py --config .ai-agents/config.yml --agent frontend_developer
```

The composition script will:
1. Load base agent prompt
2. Add platform augmentations
3. Inject skill instructions
4. Include project context

### 3. Token Budget Considerations

Skills use **progressive disclosure** to manage context efficiently:

- **Metadata** (~100 words): Always in context
- **SKILL.md body** (<5k words): Loaded when skill is triggered
- **Bundled resources**: Loaded as needed

**Best Practices:**
- Assign only relevant skills to each agent
- Monitor context usage during agent execution
- Use skill metadata to determine when to load full instructions

---

## Available Skills

See [CATALOG.md](CATALOG.md) for the complete directory of available skills, organized by category with descriptions and recommended agent types.

---

## Creating Custom Skills

To create custom project-specific skills:

1. Use the skill template:
   ```bash
   cp -r skills/custom/template skills/custom/my-skill
   ```

2. Edit `SKILL.md` with your skill's instructions

3. Add any supporting resources:
   - Scripts in `scripts/`
   - Documentation in `references/`
   - Templates in `assets/`

4. Reference in your agent configuration

See [custom/template/SKILL.md](custom/template/SKILL.md) for a starter template.

For detailed guidance on creating effective skills, use the `skill-creator` skill from Anthropic.

---

## Anthropic Skills Attribution

This library integrates skills from the [Anthropic Skills Repository](https://github.com/anthropics/skills), which are available under the following licenses:

- **Example Skills**: Apache 2.0 License
- **Document Skills** (docx, pdf, xlsx, pptx): Source-available license

All skills from Anthropic are used as reference implementations and credited appropriately. See individual skill directories for specific license information.

---

## Integration Details

For technical details on how skills are loaded and composed into agents, see [INTEGRATION.md](INTEGRATION.md).

For the complete catalog of available skills, see [CATALOG.md](CATALOG.md).

---

## Key Principles

### 1. Concise is Key

Context windows are shared resources. Skills should include only information the agent lacks, with concise examples preferred over verbose explanations.

### 2. Progressive Disclosure

Skills load in layers:
1. Metadata (always available)
2. Instructions (when triggered)
3. Resources (as needed)

### 3. Appropriate Degrees of Freedom

Skills should match specificity to task requirements:
- **High freedom**: Multiple valid approaches
- **Medium freedom**: Preferred patterns with some variation
- **Low freedom**: Fragile operations requiring specific sequences

---

## Best Practices

1. **Assign Skills Strategically** - Give each agent only the skills they need
2. **Monitor Context Usage** - Track when skills are loaded and their impact
3. **Test Incrementally** - Add skills one at a time and verify functionality
4. **Keep Skills Focused** - Each skill should have a clear, singular purpose
5. **Bundle Resources Appropriately** - Use scripts for deterministic operations
6. **Update Documentation** - Keep skill descriptions current with usage

---

## Examples

### Frontend Developer with Design Skills

```yaml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "skills/core/artifacts-builder"
    - "skills/design/theme-factory"
  project_context:
    - ".ai-agents/context/ui-guidelines.md"
```

### QA Tester with Testing Skills

```yaml
qa_tester:
  base: "base/qa-tester.md"
  skills:
    - "skills/core/webapp-testing"
  project_context:
    - ".ai-agents/context/test-plan.md"
```

### Backend Developer with MCP Skills

```yaml
backend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  skills:
    - "skills/core/mcp-builder"
  project_context:
    - ".ai-agents/context/api-contracts.md"
```

---

## Support

- **Issues**: Report skill-related issues in the main repository
- **Custom Skills**: Use the template in `custom/template/`
- **Contributions**: Follow the skill creation guidelines in INTEGRATION.md

---

## Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills)
- [CATALOG.md](CATALOG.md) - Complete skill directory
- [INTEGRATION.md](INTEGRATION.md) - Technical integration guide

---

**Ready to enhance your agents?** Check out [CATALOG.md](CATALOG.md) to browse available skills and see which ones best fit your agent team!
