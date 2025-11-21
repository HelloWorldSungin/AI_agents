# Skills Integration Guide

Technical documentation for integrating skills into the AI Agents Library composition system.

**Version:** 1.0.0

---

## Overview

This guide provides technical implementation details for:
1. How `compose-agent.py` loads and integrates skills
2. Token budget management and progressive disclosure
3. Skill loading strategies and optimization
4. Creating custom skills for your project

---

## Architecture

### Skills in the Composition Pipeline

The agent composition pipeline now includes skills as a distinct layer:

```
┌─────────────────────────────────────────┐
│   Project Context (Your Requirements)   │
│   • Business logic                       │
│   • API contracts                        │
│   • Team conventions                     │
├─────────────────────────────────────────┤
│   Skills (Domain Expertise) ← NEW       │
│   • Specialized workflows                │
│   • Tool integrations                    │
│   • Domain knowledge                     │
├─────────────────────────────────────────┤
│   Platform Augmentation (Specialized)    │
│   • Web/Mobile/Desktop expertise         │
│   • Framework knowledge                  │
│   • Platform best practices              │
├─────────────────────────────────────────┤
│   Base Agent (Universal)                 │
│   • Core software engineering            │
│   • Testing, debugging, git              │
│   • Security, performance                │
└─────────────────────────────────────────┘
```

---

## Configuration Format

### Adding Skills to Agent Configuration

In your `config.yml`, add a `skills` array to any agent:

```yaml
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:                                    # ← Skills configuration
      - "skills/core/artifacts-builder"
      - "skills/design/theme-factory"
    project_context:
      - ".ai-agents/context/architecture.md"
```

### Skill Path Resolution

Skills paths are resolved relative to the library root:

- **Absolute path from library**: `skills/core/artifacts-builder`
- **Full path on disk**: `/path/to/AI_agents/skills/core/artifacts-builder`
- **Skill file loaded**: `SKILL.md` within that directory

---

## compose-agent.py Modifications

### Current Implementation Status

**Phase 1** (This implementation):
- Skills directory structure created
- Documentation and catalog established
- Submodule/reference approach for Anthropic skills
- Template for custom skills

**Phase 2** (Next step):
- Modify `compose-agent.py` to load skills
- Implement progressive disclosure
- Add token budget tracking

### Required Changes to compose-agent.py

#### 1. Add Skills Loading Section

After the tools section (around line 144), add:

```python
# 5. Load skills
if 'skills' in agent_config and agent_config['skills']:
    components.append("# ========================================")
    components.append("# SKILLS")
    components.append("# ========================================\n")

    for skill in agent_config['skills']:
        skill_path = self.library_path / skill / "SKILL.md"
        if skill_path.exists():
            skill_content = self.load_skill(skill_path)
            components.append(f"\n## Skill: {skill}\n")
            components.append(skill_content)
            components.append("\n")
        else:
            print(f"Warning: Skill not found: {skill_path}")

    components.append("\n")
```

#### 2. Add Skill Loading Method

Add this method to the `AgentComposer` class:

```python
def load_skill(self, skill_path: Path) -> str:
    """
    Load a skill file with YAML frontmatter parsing.

    Args:
        skill_path: Path to SKILL.md file

    Returns:
        Formatted skill content with metadata
    """
    import yaml

    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()

                # Format with metadata
                formatted = []
                formatted.append(f"**Skill Name**: {frontmatter.get('name', 'Unknown')}\n")
                formatted.append(f"**Description**: {frontmatter.get('description', 'N/A')}\n")
                if 'license' in frontmatter:
                    formatted.append(f"**License**: {frontmatter['license']}\n")
                formatted.append("\n---\n\n")
                formatted.append(body)

                return "".join(formatted)

        # No frontmatter, return as-is
        return content

    except Exception as e:
        print(f"Error loading skill {skill_path}: {e}")
        return f"<!-- Error loading skill: {e} -->"
```

#### 3. Update Composition Order

The final composition order should be:

1. Header
2. Base Agent
3. Platform Augmentations
4. **Skills** (NEW)
5. Project Context
6. Tools
7. Project Configuration
8. Coordination Info
9. Memory Configuration

This ensures skills are loaded before project-specific context but after platform knowledge.

---

## Token Budget Management

### Progressive Disclosure Strategy

Skills use a three-tier loading approach to manage context efficiently:

#### Tier 1: Metadata (Always Loaded)
- Skill name and description from YAML frontmatter
- ~100 tokens per skill
- Always present in agent context

```yaml
name: artifacts-builder
description: Complex HTML artifact creation using React, Tailwind CSS, and shadcn/ui
```

#### Tier 2: Instructions (Conditionally Loaded)
- Full SKILL.md body content
- ~2,000-5,000 tokens per skill
- Loaded when skill is triggered by agent or task context

#### Tier 3: Resources (On-Demand)
- Scripts, references, assets
- Variable token count
- Loaded only when needed by agent

### Token Budget Guidelines

| Agent Type | Max Skills | Est. Token Cost | Rationale |
|------------|-----------|-----------------|-----------|
| Manager | 2-3 | 4,000-6,000 | Coordination-focused, needs overview |
| Software Developer | 3-5 | 6,000-10,000 | Primary implementer, needs tools |
| Frontend Developer | 4-6 | 8,000-12,000 | UI/UX focus, design skills needed |
| Backend Developer | 3-4 | 6,000-8,000 | API/service focus, fewer design skills |
| QA Tester | 2-3 | 4,000-6,000 | Testing-focused, specific skills |
| Architect | 2-3 | 4,000-6,000 | Design-focused, high-level skills |
| Mobile Developer | 4-5 | 8,000-10,000 | Platform-specific, design skills |

### Context Monitoring

Add token budget tracking to composition output:

```python
def calculate_skill_tokens(self, skills: List[str]) -> int:
    """Estimate token count for skills (rough approximation)."""
    total = 0
    for skill in skills:
        skill_path = self.library_path / skill / "SKILL.md"
        if skill_path.exists():
            content = self.load_markdown(skill_path)
            # Rough approximation: 4 chars per token
            total += len(content) // 4
    return total
```

---

## Skill Loading Strategies

### Strategy 1: Eager Loading (Phase 1 Implementation)

Load all assigned skills immediately during composition:

**Pros:**
- Simple implementation
- Predictable behavior
- Agent has all skills available from start

**Cons:**
- Higher initial token usage
- May load unused skills

**Use When:**
- Agent has few skills (2-3)
- Skills are frequently used
- Predictable workflow

### Strategy 2: Lazy Loading (Future Enhancement)

Load skills on-demand based on task context:

**Pros:**
- Lower initial token usage
- Only loads relevant skills
- Better context management

**Cons:**
- More complex implementation
- Requires task analysis
- Potential for missing skills

**Use When:**
- Agent has many skills (4+)
- Skills are task-specific
- Dynamic workflows

### Strategy 3: Hybrid Approach (Recommended Future State)

Load metadata for all skills, full instructions on-demand:

**Pros:**
- Balance of availability and efficiency
- Agent aware of all capabilities
- Loads details when needed

**Cons:**
- Most complex implementation
- Requires skill triggering logic

**Use When:**
- Production deployment
- Large skill libraries
- Multiple agent types

---

## Skill Discovery and Triggering

### Metadata-Based Discovery

Agents should be aware of available skills through metadata:

```markdown
## Available Skills

You have access to the following skills:

1. **artifacts-builder**: Complex HTML artifact creation using React, Tailwind CSS, and shadcn/ui
2. **theme-factory**: Toolkit for styling artifacts with professional themes
3. **webapp-testing**: Web application testing via Playwright

To use a skill, reference it by name when relevant to your task.
```

### Context-Based Triggering

Skills should load based on task context:

- **Keyword matching**: Task mentions "artifact", "component" → load `artifacts-builder`
- **Task type**: Creating tests → load `webapp-testing`
- **File type**: Working with .xlsx → load `xlsx` skill
- **Explicit request**: User asks for themed output → load `theme-factory`

---

## Creating Custom Skills

### Step 1: Initialize Skill Structure

```bash
# Use the template
cp -r skills/custom/template skills/custom/my-skill-name

# Or create from scratch
mkdir -p skills/custom/my-skill-name/{scripts,references,assets}
```

### Step 2: Create SKILL.md

```markdown
---
name: my-skill-name
description: Brief description of what this skill does and when to use it. Include triggering keywords and use cases.
license: Apache 2.0 (or your project license)
---

# Skill Name

## Overview

Clear explanation of the skill's purpose and capabilities.

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Instructions

### Step 1: Preparation

Detailed instructions...

### Step 2: Implementation

More instructions...

### Step 3: Validation

Final steps...

## Examples

### Example 1: Common Use Case

\`\`\`language
code example
\`\`\`

### Example 2: Advanced Use Case

\`\`\`language
advanced example
\`\`\`

## Supporting Resources

- **Scripts**: Located in `scripts/` - describe what each script does
- **References**: Documentation in `references/` - when to consult
- **Assets**: Templates in `assets/` - how to use

## Best Practices

- Best practice 1
- Best practice 2
- Best practice 3

## Troubleshooting

Common issues and solutions...
```

### Step 3: Add Supporting Resources

#### Scripts (scripts/)

Add executable scripts for deterministic operations:

```python
# scripts/helper_script.py
"""
Helper script description.

Usage:
    python scripts/helper_script.py --input file.txt --output result.txt
"""

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    # Implementation
    pass

if __name__ == '__main__':
    main()
```

#### References (references/)

Add documentation to be consulted as needed:

```markdown
# API Reference

## Endpoint Documentation

...
```

#### Assets (assets/)

Add templates, boilerplate, icons, fonts, etc.

### Step 4: Test the Skill

1. Add skill to test agent configuration
2. Compose agent with skill
3. Verify skill loads correctly
4. Test skill with real tasks
5. Iterate based on results

### Step 5: Document Usage

Update your project documentation:
- Add skill to project's skill catalog
- Document when to use the skill
- Add examples of successful usage
- Note any dependencies or requirements

---

## Best Practices

### For Skill Creation

1. **Be Concise** - Include only information the agent lacks
2. **Use Imperative Form** - Write instructions as commands
3. **Provide Examples** - Show concrete use cases
4. **Progressive Detail** - Start with overview, add detail progressively
5. **Test with Real Tasks** - Validate with actual agent workflows
6. **Monitor Token Usage** - Keep SKILL.md under 5,000 words

### For Skill Assignment

1. **Be Strategic** - Assign only relevant skills to each agent
2. **Avoid Overlap** - Don't assign duplicate capabilities
3. **Consider Token Budget** - Monitor total context usage
4. **Test Incrementally** - Add skills one at a time
5. **Monitor Performance** - Track impact on agent behavior

### For Skill Maintenance

1. **Keep Updated** - Reflect current tools and practices
2. **Gather Feedback** - Learn from agent usage patterns
3. **Refactor When Needed** - Split large skills into focused ones
4. **Version Control** - Track changes to skill instructions
5. **Document Changes** - Maintain changelog for skill updates

---

## Referencing Anthropic Skills

### Git Submodule Approach (Recommended)

Add the Anthropic skills repository as a submodule:

```bash
# From AI_agents repository root
git submodule add https://github.com/anthropics/skills.git skills/anthropic-skills
git submodule update --init --recursive
```

Reference in configuration:

```yaml
skills:
  - "skills/anthropic-skills/artifacts-builder"
  - "skills/anthropic-skills/webapp-testing"
```

### Direct Reference Approach (Alternative)

Document Anthropic skills in your catalog but don't include directly:

```yaml
# config.yml
skills:
  # Custom wrapper that loads Anthropic skill
  - "skills/custom/wrapped-artifacts-builder"
```

Create a wrapper skill that references the Anthropic skill:

```markdown
---
name: wrapped-artifacts-builder
description: Wrapper for Anthropic's artifacts-builder skill
---

This skill uses Anthropic's artifacts-builder.

See: https://github.com/anthropics/skills/tree/main/artifacts-builder

[Include key instructions here or reference the Anthropic skill documentation]
```

### License Compliance

When using Anthropic skills:

1. **Apache 2.0 Skills** (most example skills):
   - Free to use, modify, distribute
   - Include original license and copyright notice
   - Document modifications

2. **Source-Available Skills** (document skills):
   - Review specific license terms
   - May have restrictions on commercial use
   - Check LICENSE.txt in skill directory

---

## Troubleshooting

### Skill Not Loading

**Problem**: Skill path not found during composition

**Solution**:
- Verify skill path in config.yml is correct
- Check that SKILL.md exists in skill directory
- Ensure library path is correctly resolved

### Token Budget Exceeded

**Problem**: Agent composition exceeds token limits

**Solution**:
- Reduce number of assigned skills
- Use more focused, concise skills
- Implement lazy loading strategy
- Split agent responsibilities

### Skill Conflicts

**Problem**: Multiple skills provide overlapping capabilities

**Solution**:
- Choose most specific skill for task
- Document skill priorities in agent config
- Consider merging related skills
- Remove redundant skill assignments

### Skill Not Triggering

**Problem**: Agent not using assigned skill when expected

**Solution**:
- Improve skill description with clear triggering keywords
- Make skill purpose more explicit in SKILL.md
- Add skill awareness section to agent prompt
- Provide examples in skill documentation

---

## Future Enhancements

### Phase 2: Enhanced Loading

- Implement lazy loading based on task context
- Add skill triggering logic
- Token budget tracking and warnings

### Phase 3: Skill Management

- Skill dependency resolution
- Skill versioning support
- Skill conflict detection
- Skill usage analytics

### Phase 4: Advanced Features

- Dynamic skill discovery
- Skill composition (combining skills)
- Skill marketplace integration
- AI-assisted skill creation

---

## Examples

### Example 1: Frontend Developer with Multiple Skills

```yaml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "skills/core/artifacts-builder"
    - "skills/design/theme-factory"
    - "skills/core/webapp-testing"
  project_context:
    - ".ai-agents/context/ui-guidelines.md"
    - ".ai-agents/context/component-library.md"
```

**Token Budget**: ~15,000 tokens (Base: 3k + Platform: 2k + Skills: 8k + Context: 2k)

### Example 2: Manager with Communication Skills

```yaml
team_manager:
  base: "base/manager.md"
  skills:
    - "skills/communication/internal-comms"
  coordination:
    manages:
      - frontend_developer
      - backend_developer
      - qa_tester
```

**Token Budget**: ~8,000 tokens (Base: 4k + Skills: 3k + Coordination: 1k)

### Example 3: QA Tester with Testing Skills

```yaml
qa_tester:
  base: "base/qa-tester.md"
  skills:
    - "skills/core/webapp-testing"
  project_context:
    - ".ai-agents/context/test-plan.md"
```

**Token Budget**: ~9,000 tokens (Base: 3k + Skills: 4k + Context: 2k)

---

## References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills)
- [README.md](README.md) - Skills overview
- [CATALOG.md](CATALOG.md) - Available skills directory

---

## Support

For issues or questions:

1. Check this integration guide
2. Review skill-specific documentation
3. Consult the Anthropic skills repository
4. Open an issue in the main repository

---

**Ready to implement?** Follow the compose-agent.py modifications above to start integrating skills into your agent composition pipeline!
