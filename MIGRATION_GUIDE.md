# Skills Migration Guide

A step-by-step guide for adding Skills to existing AI Agents Library projects.

**Version**: 1.0.0
**Last Updated**: 2025-11-20
**Target Audience**: Existing AI Agents Library users

---

## Table of Contents

1. [Overview](#overview)
2. [Is Migration Necessary?](#is-migration-necessary)
3. [Backward Compatibility](#backward-compatibility)
4. [Migration Paths](#migration-paths)
5. [Step-by-Step Migration](#step-by-step-migration)
6. [Before and After Examples](#before-and-after-examples)
7. [Common Migration Issues](#common-migration-issues)
8. [Rollback Procedure](#rollback-procedure)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## Overview

The Skills Integration feature enhances the AI Agents Library with specialized capabilities through Anthropic Skills. This guide helps you migrate existing projects to take advantage of skills while maintaining full compatibility with your current setup.

### What's New

**Skills Integration (v1.0.0)** adds:
- 14 curated Anthropic Skills for specialized tasks
- Custom skills framework for project-specific workflows
- Enhanced compose-agent.py with skill loading
- Token budget management for skills
- Comprehensive documentation

### What Hasn't Changed

Your existing setup continues to work:
- Base agents unchanged
- Platform augmentations unchanged
- Project context handling unchanged
- Tools unchanged
- Composition process compatible

---

## Is Migration Necessary?

### Short Answer: No

**Skills are optional**. Your existing agents work without any changes.

### Should You Migrate?

**Consider migrating if**:
- ✅ You need specialized workflows (React components, testing, MCP servers)
- ✅ You want consistent application of best practices
- ✅ You need domain-specific expertise
- ✅ You want to enhance agent capabilities

**Skip migration if**:
- ✅ Your current agents meet all needs
- ✅ Token budget is already constrained
- ✅ You prefer minimal configurations
- ✅ You want to wait and see

### Migration Risk Level: **LOW**

- Backward compatible: 100%
- Breaking changes: 0
- Required changes: 0
- Optional enhancements: Many

---

## Backward Compatibility

### Guarantee

**100% backward compatible**. All existing agents continue to work without modification.

### What Still Works

```yaml
# Your existing configuration (NO CHANGES NEEDED)
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    project_context:
      - ".ai-agents/context/architecture.md"
    tools:
      - "tools/git-tools.md"
    # No skills field - agent works exactly as before
```

**Result**: Agent works identically to previous version.

### Composition Script

The `compose-agent.py` script:
- Detects presence/absence of skills field
- Handles agents with no skills gracefully
- Maintains same output format
- Compatible with all existing configs

---

## Migration Paths

Choose the path that fits your needs:

### Path 1: No Migration (Stay As-Is)

**Best For**: Teams satisfied with current setup

**Steps**: None required

**Pros**:
- No work needed
- No risk
- Simpler configuration

**Cons**:
- Miss out on specialized capabilities
- No access to curated workflows

---

### Path 2: Gradual Migration (Recommended)

**Best For**: Most teams

**Timeline**: 2-4 weeks

**Approach**:
1. Week 1: Add skills to one agent
2. Week 2: Test and evaluate
3. Week 3: Add skills to other agents
4. Week 4: Optimize based on results

**Pros**:
- Low risk
- Learn incrementally
- Easy rollback
- Controlled testing

**Cons**:
- Takes time
- Requires monitoring

---

### Path 3: Full Migration (Fast)

**Best For**: Teams wanting immediate skills access

**Timeline**: 1-3 days

**Approach**:
1. Day 1: Update all configurations
2. Day 2: Compose and test all agents
3. Day 3: Deploy and monitor

**Pros**:
- Fast implementation
- Immediate benefits
- Consistent team setup

**Cons**:
- Higher initial effort
- More testing needed
- Potential token budget issues

---

## Step-by-Step Migration

### Phase 1: Preparation (15 minutes)

#### Step 1: Update Library

```bash
cd your-project/.ai-agents/library
git pull origin main

# Or if using submodule
cd your-project
git submodule update --remote .ai-agents/library
```

**Verify update**:
```bash
ls -la .ai-agents/library/skills/
# Should see: core/, communication/, design/, documents/, custom/
```

---

#### Step 2: Review Available Skills

```bash
cat .ai-agents/library/skills/CATALOG.md
```

**Identify skills relevant to your agents**:
- Frontend developers → artifacts-builder, theme-factory
- Backend developers → mcp-builder
- QA testers → webapp-testing
- Managers → internal-comms, xlsx, pptx

---

#### Step 3: Backup Current Configuration

```bash
cp .ai-agents/config.yml .ai-agents/config.yml.backup
echo "Backup created: $(date)" >> .ai-agents/migration.log
```

---

### Phase 2: Configuration Update (10-30 minutes)

#### Step 4: Choose Migration Strategy

**Option A: Start with One Agent**

```yaml
# Update one agent only
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:  # NEW
      - "core/artifacts-builder"  # Start with one skill
    project_context:
      - ".ai-agents/context/architecture.md"
```

**Option B: Update Multiple Agents**

```yaml
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:  # NEW
      - "core/artifacts-builder"
      - "design/theme-factory"
    # ... rest of config

  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:  # NEW
      - "core/mcp-builder"
    # ... rest of config

  qa_tester:
    base: "base/qa-tester.md"
    skills:  # NEW
      - "core/webapp-testing"
    # ... rest of config
```

---

#### Step 5: Validate Configuration

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.ai-agents/config.yml'))"

# If no output, YAML is valid
```

---

### Phase 3: Composition (5-10 minutes)

#### Step 6: Compose Agents with Skills

```bash
cd .ai-agents/library

# Compose single agent (if Option A)
python3 scripts/compose-agent.py \
  --config ../../config.yml \
  --agent frontend_developer \
  --output ../../composed

# Or compose all agents (if Option B)
python3 scripts/compose-agent.py \
  --config ../../config.yml \
  --all \
  --output ../../composed
```

**Expected output**:
```
Library path: /Users/you/project/.ai-agents/library
Project path: /Users/you/project

Composing frontend_developer...
✓ Saved: frontend_developer.md
  Tokens: 11,200 / 12,000 recommended
  Context usage: 5.60%
```

---

#### Step 7: Review Token Budgets

**Check for warnings**:

| Token Count | Status | Action |
|-------------|--------|--------|
| < 9,000 | ✅ Green | No action needed |
| 9,000-10,500 | ⚠️ Yellow | Review, acceptable |
| 10,500-12,000 | ⚠️ Orange | Consider removing 1 skill |
| > 12,000 | 🔴 Red | Remove 1-2 skills |

**If over budget**:
```bash
# Remove least essential skill from config.yml
# Example: Remove theme-factory if artifacts-builder is more critical
```

---

### Phase 4: Testing (30-60 minutes)

#### Step 8: Verify Composed Files

```bash
# Check skills were included
grep -c "Skill: core/artifacts-builder" .ai-agents/composed/frontend_developer.md
# Should be > 0

# View skill content
sed -n '/## Skill: core/,/## /p' .ai-agents/composed/frontend_developer.md | head -50
```

---

#### Step 9: Test with Sample Tasks

**Frontend Developer**:
```
Task: Create a React button component with Tailwind CSS
Expected: Agent uses artifacts-builder skill workflow
```

**Backend Developer**:
```
Task: Design an MCP server for the GitHub API
Expected: Agent uses mcp-builder skill guidance
```

**QA Tester**:
```
Task: Test the login form at localhost:3000
Expected: Agent uses webapp-testing skill (Playwright)
```

---

#### Step 10: Monitor Token Usage

**During conversation**:
- Watch for context warnings
- Monitor agent performance
- Track skill usage

**After 5-10 conversations**:
```markdown
# Document in project log
Skill Usage Assessment:
- artifacts-builder: Used in 8/10 conversations ✅ KEEP
- theme-factory: Used in 3/10 conversations ⚠️ REVIEW
- webapp-testing: Used in 9/10 conversations ✅ KEEP
```

---

### Phase 5: Optimization (Ongoing)

#### Step 11: Refine Skill Selection

**Based on usage data**:

```yaml
# Before (too many skills)
frontend_developer:
  skills:
    - "core/artifacts-builder"    # Used: 90%
    - "design/theme-factory"      # Used: 40%
    - "core/webapp-testing"       # Used: 10%
    - "design/canvas-design"      # Used: 2%

# After (optimized)
frontend_developer:
  skills:
    - "core/artifacts-builder"    # Keep - high usage
    - "design/theme-factory"      # Keep - medium usage
  # Removed webapp-testing (move to QA agent)
  # Removed canvas-design (rarely used)
```

---

#### Step 12: Document Changes

```markdown
# .ai-agents/MIGRATION_LOG.md

## Skills Migration - 2025-11-20

### Changes Made
- Added artifacts-builder to frontend_developer
- Added mcp-builder to backend_developer
- Added webapp-testing to qa_tester

### Token Budget Impact
- Frontend: 8,000 → 11,200 tokens (+3,200)
- Backend: 7,500 → 12,000 tokens (+4,500)
- QA: 5,000 → 9,000 tokens (+4,000)
- Total: 20,500 → 32,200 tokens (+11,700)

### Results
- All agents working as expected
- Skills being utilized effectively
- No performance issues
- Team feedback: positive

### Next Steps
- Monitor usage for 2 weeks
- Consider adding theme-factory to mobile developer
- Review token budgets monthly
```

---

## Before and After Examples

### Example 1: Frontend Developer

**Before (No Skills)**:

```yaml
# config.yml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/api-contracts.md"
  tools:
    - "tools/git-tools.md"
    - "tools/testing-tools.md"

# Token Budget: ~8,000 tokens
# Capabilities: General React development
```

**After (With Skills)**:

```yaml
# config.yml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:  # NEW
    - "core/artifacts-builder"  # React component workflows
    - "design/theme-factory"    # Professional styling
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/api-contracts.md"
  tools:
    - "tools/git-tools.md"
    - "tools/testing-tools.md"

# Token Budget: ~11,500 tokens
# Capabilities: React development + structured workflows + theming
```

**Impact**:
- +3,500 tokens
- Structured component creation workflow
- Consistent styling patterns
- Better artifact generation

---

### Example 2: QA Tester

**Before (No Skills)**:

```yaml
# config.yml
qa_tester:
  base: "base/qa-tester.md"
  project_context:
    - ".ai-agents/context/test-plan.md"
  tools:
    - "tools/testing-tools.md"

# Token Budget: ~5,000 tokens
# Capabilities: Manual testing guidance
```

**After (With Skills)**:

```yaml
# config.yml
qa_tester:
  base: "base/qa-tester.md"
  skills:  # NEW
    - "core/webapp-testing"  # Playwright automation
    - "documents/xlsx"       # Test data management
  project_context:
    - ".ai-agents/context/test-plan.md"
  tools:
    - "tools/testing-tools.md"

# Token Budget: ~9,000 tokens
# Capabilities: Automated testing + data management + reporting
```

**Impact**:
- +4,000 tokens
- Playwright-based automation
- Better test data handling
- Professional reporting

---

### Example 3: Team Manager

**Before (No Skills)**:

```yaml
# config.yml
team_manager:
  base: "base/manager.md"
  project_context:
    - ".ai-agents/context/architecture.md"
  tools:
    - "tools/communication-tools.md"
  coordination:
    manages:
      - "frontend_developer"
      - "backend_developer"
      - "qa_tester"

# Token Budget: ~5,000 tokens
# Capabilities: Basic coordination
```

**After (With Skills)**:

```yaml
# config.yml
team_manager:
  base: "base/manager.md"
  skills:  # NEW
    - "communication/internal-comms"  # Professional communications
    - "documents/xlsx"                # Metrics tracking
    - "documents/pptx"                # Presentations
  project_context:
    - ".ai-agents/context/architecture.md"
  tools:
    - "tools/communication-tools.md"
  coordination:
    manages:
      - "frontend_developer"
      - "backend_developer"
      - "qa_tester"

# Token Budget: ~12,000 tokens
# Capabilities: Professional comms + metrics + presentations
```

**Impact**:
- +7,000 tokens
- Structured communication formats (3P updates, newsletters)
- Data-driven metrics
- Professional presentations

---

### Example 4: Minimal Impact (Backend Developer)

**Before**:

```yaml
backend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/database-schema.md"
  tools:
    - "tools/git-tools.md"

# Token Budget: ~7,500 tokens
```

**After**:

```yaml
backend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  skills:  # NEW - Just one skill
    - "core/mcp-builder"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/database-schema.md"
  tools:
    - "tools/git-tools.md"

# Token Budget: ~12,000 tokens
```

**Impact**: Moderate
- +4,500 tokens
- MCP server development workflow
- API integration patterns
- Best practices for external services

---

## Common Migration Issues

### Issue 1: Skill Not Found

**Symptom**:
```
Warning: Skill not found: core/artifacts-builder
  Searched in library: skills/core/artifacts-builder.md
  Searched in project: .ai-agents/skills/core/artifacts-builder.md
```

**Cause**: Skills directory not present or outdated library

**Solution**:
```bash
# Update library
cd .ai-agents/library
git pull origin main

# Verify skills exist
ls -la skills/core/
```

---

### Issue 2: Token Budget Exceeded

**Symptom**:
```
⚠️  WARNING: Agent prompt exceeds recommended size!
Recommendation: 2,000 tokens over budget

Suggestions to reduce token usage:
- Consider removing 2 skill(s)
```

**Cause**: Too many skills added at once

**Solution**:
```yaml
# Prioritize skills
frontend_developer:
  skills:
    # Keep only essential skills
    - "core/artifacts-builder"  # Most important
    # - "design/theme-factory"  # Remove to free 2,500 tokens
    # - "core/webapp-testing"   # Move to QA tester
```

---

### Issue 3: Agent Performance Degraded

**Symptom**: Agent slower or less effective after adding skills

**Cause**: Skills conflicting or not relevant to tasks

**Solution**:
1. Remove skills one by one
2. Test after each removal
3. Keep only skills that improve performance
4. Consider creating specialized agent variants

---

### Issue 4: Skills Not Being Used

**Symptom**: Agent has skills but doesn't reference them

**Diagnosis**:
```bash
# Check skill is loaded
grep "Skill: core/artifacts-builder" .ai-agents/composed/agent.md
```

**Possible Causes**:
- Skill loaded but not relevant to task
- Skill content too vague
- Agent doesn't recognize when to use skill

**Solution**:
- Ensure task matches skill's use case
- Review skill content for clarity
- Add examples to custom skills

---

### Issue 5: Configuration Syntax Error

**Symptom**:
```
Error: Invalid YAML syntax
```

**Cause**: Incorrect indentation or formatting

**Solution**:
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.ai-agents/config.yml'))"

# Common issues:
# - Inconsistent indentation (use 2 spaces)
# - Missing colons
# - Incorrect list formatting
```

**Example Fix**:
```yaml
# Wrong (inconsistent indentation)
frontend_developer:
  skills:
  - "core/artifacts-builder"
    - "design/theme-factory"  # Extra indentation

# Right
frontend_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"
```

---

## Rollback Procedure

### If Something Goes Wrong

Don't panic! Rollback is simple and safe.

### Quick Rollback

```bash
# Restore backup configuration
cp .ai-agents/config.yml.backup .ai-agents/config.yml

# Recompose agents
cd .ai-agents/library
python3 scripts/compose-agent.py --config ../../config.yml --all

# Verify
echo "Rollback complete. Your agents are back to pre-migration state."
```

---

### Partial Rollback

**Remove skills from one agent**:

```yaml
# Edit config.yml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  # skills:  # Comment out or remove
  #   - "core/artifacts-builder"
  #   - "design/theme-factory"
  project_context:
    - ".ai-agents/context/architecture.md"
```

**Recompose**:
```bash
python3 scripts/compose-agent.py \
  --config ../../config.yml \
  --agent frontend_developer
```

---

### Document Rollback

```markdown
# .ai-agents/MIGRATION_LOG.md

## Rollback - 2025-11-20

### Reason
Token budget exceeded, causing context issues

### Action Taken
Removed all skills from frontend_developer, restored to baseline

### Result
Agent functioning normally, token budget back to 8,000

### Lessons Learned
Start with 1 skill, not 3. Test thoroughly before adding more.

### Next Steps
Will try adding just artifacts-builder skill tomorrow
```

---

## Best Practices

### 1. Start Small

```yaml
# Phase 1: Add one skill
frontend_developer:
  skills:
    - "core/artifacts-builder"

# Test for 1 week

# Phase 2: Add second skill (if Phase 1 successful)
frontend_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"
```

---

### 2. Monitor and Measure

**Track skill effectiveness**:

```markdown
# Weekly Skill Review Template

## Week of 2025-11-20

### Frontend Developer
- artifacts-builder
  - Times used: 12
  - Tasks successful: 11
  - Tasks failed: 1
  - Value: HIGH ✅ KEEP

- theme-factory
  - Times used: 4
  - Tasks successful: 4
  - Tasks failed: 0
  - Value: MEDIUM ⚠️ MONITOR

### Decision
Keep both skills, review again next week
```

---

### 3. Team Communication

**Inform your team**:

```markdown
# Team Announcement

## Skills Added to Agents - 2025-11-20

We've enhanced our AI agents with specialized skills:

- **Frontend Developer**: Now has React component building workflow
- **QA Tester**: Now can automate browser testing with Playwright
- **Team Manager**: Now can create professional status reports

### What This Means
- Agents may work differently (better!)
- Token budgets increased slightly
- More specialized guidance available

### What You Need to Do
- Nothing! Just use agents as before
- Report any issues to #ai-agents channel

### Questions?
See: .ai-agents/library/SKILLS_GUIDE.md
```

---

### 4. Version Control

**Commit configuration changes**:

```bash
git add .ai-agents/config.yml
git commit -m "feat: Add skills to frontend and QA agents

- frontend_developer: Added artifacts-builder and theme-factory
- qa_tester: Added webapp-testing
- Token budgets adjusted accordingly

Refs: SKILLS_GUIDE.md for details"

git push
```

---

### 5. Document Everything

**Create migration documentation**:

```markdown
# .ai-agents/SKILLS_MIGRATION.md

## Migration Summary

**Date**: 2025-11-20
**Version**: Library v1.0.0 → v1.0.0 (with skills)
**Migration Path**: Gradual (2 weeks)

### Agents Modified
1. frontend_developer
2. qa_tester
3. team_manager

### Agents Unchanged
1. backend_developer (no relevant skills yet)

### Token Budget Changes
| Agent | Before | After | Delta |
|-------|--------|-------|-------|
| Frontend | 8,000 | 11,500 | +3,500 |
| QA | 5,000 | 9,000 | +4,000 |
| Manager | 5,000 | 12,000 | +7,000 |
| **Total** | **18,000** | **32,500** | **+14,500** |

### Results
- All agents functioning well
- Skills being utilized
- No performance issues
- Team satisfaction: 👍

### Resources
- [SKILLS_GUIDE.md](library/SKILLS_GUIDE.md)
- [CATALOG.md](library/skills/CATALOG.md)
- [TESTING_REPORT.md](library/TESTING_REPORT.md)
```

---

## FAQ

### Q: Do I have to migrate?

**A**: No. Skills are completely optional. Your agents work fine without them.

---

### Q: Will migration break my existing agents?

**A**: No. The update is 100% backward compatible. Agents without skills work exactly as before.

---

### Q: How long does migration take?

**A**:
- Updating one agent: 10-15 minutes
- Full team migration: 1-3 hours
- Testing and optimization: 1-2 weeks

---

### Q: What if I add skills and don't like them?

**A**: Simply remove the `skills:` section from your config and recompose. Rollback is instant and safe.

---

### Q: Will skills slow down my agents?

**A**: No. Skills are loaded at composition time (not runtime), so they don't affect agent speed during conversation.

---

### Q: How much do skills increase token usage?

**A**:
- 1 skill: +2,000 to +5,000 tokens
- 2 skills: +5,000 to +8,000 tokens
- 3 skills: +8,000 to +12,000 tokens

For perspective: Still leaves 188,000+ tokens for conversation (Claude Sonnet 4.5).

---

### Q: Can I create custom skills?

**A**: Yes! See `skills/custom/template/` for a starter template and [SKILLS_GUIDE.md](SKILLS_GUIDE.md#custom-skills) for detailed instructions.

---

### Q: Do skills work with all LLM providers?

**A**: Yes. Skills are just markdown instructions, so they work with any LLM (Claude, GPT-4, etc.).

---

### Q: Can I mix Anthropic skills and custom skills?

**A**: Yes! You can use any combination of Anthropic skills and your own custom skills.

---

### Q: How do I know which skills to add?

**A**: See the decision tree in [SKILLS_GUIDE.md#skill-selection-guide](SKILLS_GUIDE.md#skill-selection-guide). General rule:
- Frontend: artifacts-builder, theme-factory
- Backend: mcp-builder
- QA: webapp-testing
- Manager: internal-comms, xlsx, pptx

---

### Q: What if a skill I need doesn't exist?

**A**: Create a custom skill! Copy the template from `skills/custom/template/`, add your instructions, and reference it in your config.

---

### Q: Can I update skills after adding them?

**A**: Yes. Pull latest from library, recompose agents. Skills are versioned for safe updates.

---

## Summary

### Key Points

1. **Optional**: Migration is not required
2. **Safe**: 100% backward compatible
3. **Gradual**: Start with one agent, expand as needed
4. **Reversible**: Easy rollback if needed
5. **Beneficial**: Adds specialized capabilities

### Recommended Approach

```
Week 1: Add skills to 1 agent → Test
Week 2: Evaluate results → Adjust
Week 3: Add skills to more agents → Monitor
Week 4: Optimize and document → Complete
```

### Success Criteria

✅ Agents functioning as expected
✅ Skills being utilized
✅ Token budgets manageable
✅ Team satisfied with results
✅ Documentation updated

---

## Support

### Getting Help

**For migration questions**:
- Review [SKILLS_GUIDE.md](SKILLS_GUIDE.md)
- Check [FAQ](#faq) section
- Consult [TESTING_REPORT.md](TESTING_REPORT.md)

**For technical issues**:
- Review [Common Migration Issues](#common-migration-issues)
- Check example configurations in `examples/`
- See troubleshooting in SKILLS_GUIDE.md

**For custom skills**:
- Use template in `skills/custom/template/`
- Follow [SKILLS_GUIDE.md#custom-skills](SKILLS_GUIDE.md#custom-skills)
- Review [skills/INTEGRATION.md](skills/INTEGRATION.md)

---

## Resources

- [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Comprehensive skills guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Skills integration architecture
- [skills/CATALOG.md](skills/CATALOG.md) - All available skills
- [TESTING_REPORT.md](TESTING_REPORT.md) - Test results
- [examples/](examples/) - Example configurations

---

**Migration Guide Version**: 1.0.0
**Last Updated**: 2025-11-20
**Status**: Production Ready

**Good luck with your migration! Remember: start small, test thoroughly, and iterate based on results.**
