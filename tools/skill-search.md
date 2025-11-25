# Skill Search Tool

> **Purpose**: Enables on-demand discovery and loading of deferred skills to optimize token usage.
> **Based on**: [Anthropic's Advanced Tool Use - Tool Search Tool](https://www.anthropic.com/engineering/advanced-tool-use)

## Overview

The Skill Search Tool implements Anthropic's deferred loading pattern, allowing agents to discover and load skills on-demand rather than loading everything upfront. This reduces initial context size by 40-60% and improves accuracy by presenting only relevant capabilities.

## How It Works

1. **At Composition Time**: Primary skills are loaded immediately (`always_loaded`), while secondary skills are cataloged in a manifest (`deferred`)
2. **At Runtime**: Agent sees a lightweight manifest of available skills instead of full skill content
3. **On Demand**: When a task requires a deferred skill, the agent requests it and it's loaded into context

## Usage

### Discovering Available Skills

When you need a capability not in your current context, check the "Available On-Demand Skills" section in your prompt. This shows:

- **Skill Name**: The identifier for the skill
- **Description**: What the skill enables you to do
- **Trigger Keywords**: Terms that indicate when this skill might be useful

### Requesting a Skill

To load a deferred skill, communicate your need clearly:

```
"I need to use the [skill-name] skill to complete this task."
```

Or reference the capability:

```
"This task requires PDF generation capabilities. Loading the documents/pdf skill."
```

## Configuration

### Agent Config (config.yml)

```yaml
agents:
  frontend_developer:
    skills:
      # Primary skills - always loaded
      always_loaded:
        - "core/web-artifacts-builder"

      # Secondary skills - loaded on demand
      deferred:
        - "documents/pdf"  # Simple format
        - path: "design/theme-factory"  # Extended format
          description: "Create and manage UI themes with dark mode support"
          triggers:
            - "theme"
            - "dark mode"
            - "color scheme"
            - "styling"
```

### Schema Support

The agent schema (v2.0.0) supports both formats:

**Legacy (backward compatible)**:
```yaml
skills:
  - "core/web-artifacts-builder"
  - "documents/pdf"
```

**Advanced (with deferred loading)**:
```yaml
skills:
  always_loaded:
    - "core/web-artifacts-builder"
  deferred:
    - "documents/pdf"
    - path: "design/theme-factory"
      description: "UI theming capabilities"
      triggers: ["theme", "dark mode"]
```

## Benefits

| Metric | Without Deferred Loading | With Deferred Loading |
|--------|-------------------------|----------------------|
| Initial tokens | 10K-15K | 4K-6K |
| Skill selection accuracy | ~49% | ~74% |
| Context available for work | Limited | Maximized |

## Best Practices

1. **Keep primary skills minimal**: Only `always_loaded` skills the agent needs for most tasks
2. **Add good descriptions**: Help the agent understand when to request each skill
3. **Use trigger keywords**: Include common terms that indicate need for the skill
4. **Group related skills**: If skills are often used together, consider combining them

## Integration with Compose Tool

The `compose-agent.py` script automatically:

1. Loads `always_loaded` skills into the agent prompt
2. Generates a skill manifest table for `deferred` skills
3. Creates a `{agent}-deferred-skills.json` file for runtime skill loading
4. Reports token savings from deferred loading

## Example Output

When composing an agent with deferred skills:

```
Composing frontend_developer...
  ℹ️  Deferred 3 skill(s), saving ~4,500 tokens
✓ Saved deferred skills manifest: .ai-agents/composed/frontend_developer-deferred-skills.json
✓ Saved: .ai-agents/composed/frontend_developer.md
  Tokens: 5,234 / 12,000 recommended
  Context usage: 2.62%
```

## Runtime Loading (Future)

For orchestration systems that support dynamic skill injection:

```python
# Load deferred skill at runtime
def load_deferred_skill(agent_name: str, skill_name: str) -> str:
    manifest_path = f".ai-agents/composed/{agent_name}-deferred-skills.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    for skill in manifest['deferred_skills']:
        if skill['name'] == skill_name:
            skill_path = resolve_skill_path(skill['path'])
            return load_markdown(skill_path)

    return None
```

## Related Features

- **Tool Use Examples**: Add `input_examples` to tools for improved parameter accuracy
- **Cache Control**: Structure prompts for Anthropic's prompt caching
- **Programmatic Tool Calling**: Use `allowed_callers` for code-based orchestration
