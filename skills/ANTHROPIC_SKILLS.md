# Anthropic Skills Integration

Instructions for integrating skills from the [Anthropic Skills Repository](https://github.com/anthropics/skills) into your AI Agents Library.

---

## Overview

Anthropic provides a collection of high-quality skills under the Apache 2.0 license (example skills) and source-available licenses (document skills). Rather than duplicating these skills, we reference them directly.

---

## Integration Approach: Git Submodule (Recommended)

### Why Git Submodule?

- **Stay Updated**: Easy to pull latest skill improvements from Anthropic
- **No Duplication**: Don't maintain copies of upstream code
- **Clear Attribution**: Maintains connection to original source
- **Selective Loading**: Choose which skills to use in configurations

---

## Setup Instructions

### Step 1: Add Anthropic Skills as Submodule

From the AI Agents Library root directory:

```bash
# Navigate to your AI Agents Library
cd /path/to/AI_agents

# Add Anthropic skills as a submodule
git submodule add https://github.com/anthropics/skills.git skills/anthropic

# Initialize and update the submodule
git submodule update --init --recursive

# Commit the submodule addition
git add .gitmodules skills/anthropic
git commit -m "Add Anthropic skills as submodule"
```

### Step 2: Verify Installation

```bash
# Check that skills are available
ls skills/anthropic

# Should see directories like:
# artifacts-builder/
# webapp-testing/
# mcp-builder/
# skill-creator/
# internal-comms/
# theme-factory/
# docx/
# pdf/
# pptx/
# xlsx/
# etc.
```

### Step 3: Update Submodule (Periodically)

To get the latest skills from Anthropic:

```bash
# From AI Agents Library root
cd skills/anthropic
git pull origin main
cd ../..

# Commit the submodule update
git add skills/anthropic
git commit -m "Update Anthropic skills to latest version"
```

---

## Using Anthropic Skills in Agent Configurations

### Configuration Format

Reference Anthropic skills using the `skills/anthropic/` prefix:

```yaml
# config.yml
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "skills/anthropic/artifacts-builder"
      - "skills/anthropic/theme-factory"
    project_context:
      - ".ai-agents/context/architecture.md"

  qa_tester:
    base: "base/qa-tester.md"
    skills:
      - "skills/anthropic/webapp-testing"

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      - "skills/anthropic/mcp-builder"

  team_manager:
    base: "base/manager.md"
    skills:
      - "skills/anthropic/internal-comms"
      - "skills/anthropic/docx"
      - "skills/anthropic/xlsx"
```

### Compose Agents with Anthropic Skills

```bash
# Compose specific agent
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent frontend_developer

# Compose all agents
python scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --all
```

The composition script will automatically load skills from the `skills/anthropic/` submodule.

---

## Available Anthropic Skills

### Core Development Skills

| Skill | Path | Description |
|-------|------|-------------|
| artifacts-builder | `skills/anthropic/artifacts-builder` | React/Tailwind/shadcn artifacts |
| webapp-testing | `skills/anthropic/webapp-testing` | Playwright web testing |
| mcp-builder | `skills/anthropic/mcp-builder` | MCP server development |
| skill-creator | `skills/anthropic/skill-creator` | Skill creation guide |

### Communication Skills

| Skill | Path | Description |
|-------|------|-------------|
| internal-comms | `skills/anthropic/internal-comms` | Internal communications |

### Design Skills

| Skill | Path | Description |
|-------|------|-------------|
| theme-factory | `skills/anthropic/theme-factory` | Professional theming |
| algorithmic-art | `skills/anthropic/algorithmic-art` | Generative art with p5.js |
| canvas-design | `skills/anthropic/canvas-design` | Visual art generation |
| slack-gif-creator | `skills/anthropic/slack-gif-creator` | Animated GIF creation |

### Document Skills

| Skill | Path | Description |
|-------|------|-------------|
| docx | `skills/anthropic/docx` | Word document creation/editing |
| pdf | `skills/anthropic/pdf` | PDF manipulation |
| xlsx | `skills/anthropic/xlsx` | Excel spreadsheet work |
| pptx | `skills/anthropic/pptx` | PowerPoint presentations |

See [CATALOG.md](CATALOG.md) for detailed descriptions and agent recommendations.

---

## Alternative Approach: Direct Clone

If you prefer not to use git submodules:

### Option 1: Clone Alongside Library

```bash
# From your project root
cd /path/to/your-project/.ai-agents
git clone https://github.com/anthropics/skills.git anthropic-skills

# Reference in config
skills:
  - "../anthropic-skills/artifacts-builder"
```

### Option 2: Global Installation

```bash
# Clone to a common location
git clone https://github.com/anthropics/skills.git ~/anthropic-skills

# Create symlink from library
cd /path/to/AI_agents/skills
ln -s ~/anthropic-skills anthropic

# Reference normally
skills:
  - "skills/anthropic/artifacts-builder"
```

### Option 3: Copy Specific Skills

```bash
# Copy only the skills you need
cp -r /path/to/anthropic-skills/artifacts-builder /path/to/AI_agents/skills/core/
cp -r /path/to/anthropic-skills/webapp-testing /path/to/AI_agents/skills/core/

# Reference as local skills
skills:
  - "skills/core/artifacts-builder"
  - "skills/core/webapp-testing"
```

**Note**: If copying, you must maintain proper attribution and license compliance.

---

## License Compliance

### Apache 2.0 Skills (Most Example Skills)

**License**: Apache 2.0
**Permissions**: Commercial use, modification, distribution, patent use
**Requirements**:
- Include LICENSE file
- Include NOTICE file
- State changes made
- Include copyright notice

**Skills Under Apache 2.0**:
- artifacts-builder
- webapp-testing
- mcp-builder
- skill-creator
- internal-comms
- theme-factory
- algorithmic-art
- canvas-design
- slack-gif-creator
- brand-guidelines

### Source-Available Skills (Document Skills)

**License**: Source-available (see individual LICENSE.txt)
**Skills**:
- docx
- pdf
- xlsx
- pptx

**Requirements**: Review LICENSE.txt in each skill directory for specific terms.

### Attribution

When using Anthropic skills:

1. **Preserve LICENSE files** in each skill directory
2. **Maintain copyright notices** in skill files
3. **Document usage** in your project documentation
4. **Link to source**: Reference https://github.com/anthropics/skills

Example attribution in your README:

```markdown
## Skills Attribution

This project uses skills from the [Anthropic Skills Repository](https://github.com/anthropics/skills):

- artifacts-builder (Apache 2.0)
- webapp-testing (Apache 2.0)
- mcp-builder (Apache 2.0)
- docx (source-available, see LICENSE)
- xlsx (source-available, see LICENSE)

See individual skill directories for complete license information.
```

---

## Troubleshooting

### Submodule Not Initialized

**Problem**: `skills/anthropic` directory is empty

**Solution**:
```bash
git submodule update --init --recursive
```

### Submodule Out of Sync

**Problem**: Submodule points to old commit

**Solution**:
```bash
cd skills/anthropic
git checkout main
git pull origin main
cd ../..
git add skills/anthropic
git commit -m "Update Anthropic skills submodule"
```

### Skill Not Found During Composition

**Problem**: compose-agent.py can't find Anthropic skill

**Solution**:
1. Verify submodule is initialized: `ls skills/anthropic`
2. Check path in config.yml: `skills/anthropic/skill-name`
3. Ensure SKILL.md exists: `ls skills/anthropic/skill-name/SKILL.md`
4. Verify library path in compose script

### Conflicts with Custom Skills

**Problem**: Custom skill has same name as Anthropic skill

**Solution**:
- Custom skills go in `skills/custom/`
- Anthropic skills are in `skills/anthropic/`
- Use full paths in config to disambiguate:
  ```yaml
  skills:
    - "skills/custom/my-skill"      # Your custom skill
    - "skills/anthropic/their-skill" # Anthropic skill
  ```

---

## Best Practices

### 1. Pin Submodule Versions for Stability

```bash
# After finding a stable version
cd skills/anthropic
git checkout <specific-commit-or-tag>
cd ../..
git add skills/anthropic
git commit -m "Pin Anthropic skills to stable version"
```

### 2. Test After Updates

When updating the Anthropic skills submodule:

1. Update submodule
2. Re-compose affected agents
3. Test agent behavior
4. Verify skills still work as expected
5. Commit if successful, rollback if issues found

### 3. Document Which Skills You Use

In your project's `.ai-agents/config.yml` or documentation:

```yaml
# Document why each skill is assigned
agents:
  frontend_developer:
    skills:
      - "skills/anthropic/artifacts-builder"  # For React component creation
      - "skills/anthropic/theme-factory"      # For consistent styling
```

### 4. Monitor Token Budgets

Anthropic skills vary in size. Monitor composed agent token counts:

```bash
python scripts/compose-agent.py --config config.yml --agent frontend_developer

# Output includes token analysis:
# Tokens: 8,234 / 12,000 recommended
# Context usage: 4.12%
```

### 5. Contribute Improvements Back

If you find issues or improvements for Anthropic skills:

1. Fork the Anthropic skills repository
2. Create a branch with your improvements
3. Submit a pull request to Anthropic
4. Share improvements with the community

---

## Cloning Projects That Use This Library

When someone clones a project that uses the AI Agents Library with Anthropic skills:

```bash
# Clone the project
git clone <project-url>
cd project

# Initialize submodules (if project uses library as submodule)
git submodule update --init --recursive

# This will automatically initialize:
# - AI Agents Library submodule
# - Anthropic skills submodule (nested within library)

# Verify everything is set up
ls .ai-agents/library/skills/anthropic
```

---

## Migration from Copied Skills

If you previously copied Anthropic skills directly, migrate to submodule approach:

```bash
# 1. Remove copied skills
rm -rf skills/core/artifacts-builder
rm -rf skills/core/webapp-testing
# ... etc

# 2. Add submodule
git submodule add https://github.com/anthropics/skills.git skills/anthropic

# 3. Update configurations to use new paths
# Change: skills/core/artifacts-builder
# To:     skills/anthropic/artifacts-builder

# 4. Test composition
python scripts/compose-agent.py --config config.yml --all

# 5. Commit changes
git add .
git commit -m "Migrate to Anthropic skills submodule"
```

---

## Summary

**Recommended Setup**:
1. Add Anthropic skills as git submodule: `git submodule add https://github.com/anthropics/skills.git skills/anthropic`
2. Reference in configs: `skills/anthropic/skill-name`
3. Update periodically: `cd skills/anthropic && git pull origin main`
4. Maintain proper attribution and license compliance

**Benefits**:
- Easy updates
- No duplication
- Clear attribution
- Selective usage
- Community improvements

For detailed skill descriptions and agent assignments, see [CATALOG.md](CATALOG.md).

For technical implementation details, see [INTEGRATION.md](INTEGRATION.md).

---

**Questions or Issues?**

- Check [Anthropic Skills Repository](https://github.com/anthropics/skills)
- Review [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills)
- Consult [Integration Guide](INTEGRATION.md)
- Open an issue in this repository
