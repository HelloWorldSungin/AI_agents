# Project-Specific Skills Integration Guide

## Overview

This guide explains how to integrate the AI Agents Library skills system into your project, create project-specific custom skills, and manage the relationship between library skills and project customizations.

## Integration Approaches

### Approach 1: Git Submodule (Recommended)

Use the AI Agents Library as a Git submodule to stay synchronized with updates while maintaining project-specific customizations.

**Setup:**

```bash
# In your project root
mkdir -p .ai-agents
cd .ai-agents

# Add AI Agents Library as submodule
git submodule add https://github.com/your-org/AI_agents.git library

# Initialize and update
git submodule init
git submodule update

# Your structure:
# .ai-agents/
# ├── library/           # Git submodule (AI Agents Library)
# │   ├── base/
# │   ├── platforms/
# │   ├── skills/
# │   └── scripts/
# ├── config.yml         # Your project configuration
# ├── skills/            # Your project-specific skills
# └── context/           # Your project context files
```

**Benefits:**
- Stay updated with library improvements
- Clear separation between library and project content
- Easy to contribute fixes back to library
- Version control for library version used

**Updating Library:**

```bash
# Update to latest library version
cd .ai-agents/library
git pull origin main
cd ../..
git add .ai-agents/library
git commit -m "Update AI Agents Library to latest version"

# Update to specific version
cd .ai-agents/library
git checkout v1.2.0
cd ../..
git add .ai-agents/library
git commit -m "Update AI Agents Library to v1.2.0"
```

### Approach 2: Direct Copy

Copy the AI Agents Library directly into your project for full control and no external dependencies.

**Setup:**

```bash
# Copy library to your project
cp -r /path/to/AI_agents .ai-agents/

# Remove .git directory to make it part of your repo
rm -rf .ai-agents/.git

# Your structure:
# .ai-agents/
# ├── base/
# ├── platforms/
# ├── skills/
# ├── scripts/
# ├── config.yml
# └── README.md
```

**Benefits:**
- Complete control over all files
- No submodule complexity
- Can modify library files directly

**Drawbacks:**
- Manual process to sync updates from library
- Harder to contribute fixes back
- No clear separation between library and customizations

### Approach 3: Hybrid (Library + Extensions)

Keep library separate but reference it, adding project customizations alongside.

**Setup:**

```bash
# Structure:
# /path/to/AI_agents/      # Library repo (separate)
#
# your-project/
# ├── .ai-agents/
# │   ├── config.yml       # References library path
# │   ├── skills/          # Project skills only
# │   ├── context/         # Project context
# │   └── composed/        # Composed agents
# └── src/

# config.yml references library
library_path: "/path/to/AI_agents"  # or relative path
```

**Benefits:**
- Single library installation for multiple projects
- Minimal duplication
- Projects stay lightweight

**Drawbacks:**
- Library path dependency
- Team needs shared library location
- Versioning requires coordination

## Project Structure

### Recommended Directory Layout

```
your-project/
├── .ai-agents/
│   ├── config.yml                  # Agent configurations
│   ├── skills/                     # Project-specific skills
│   │   ├── custom/                 # Custom project skills
│   │   │   ├── deploy-to-prod/
│   │   │   │   └── SKILL.md
│   │   │   ├── run-integration-tests/
│   │   │   │   └── SKILL.md
│   │   │   └── create-jira-ticket/
│   │   │       └── SKILL.md
│   │   └── overrides/              # Override library skills
│   │       └── webapp-testing/
│   │           └── SKILL.md        # Customized for this project
│   ├── context/                    # Project context
│   │   ├── architecture.md
│   │   ├── coding-standards.md
│   │   └── deployment-env.md
│   ├── composed/                   # Composed agents (output)
│   │   ├── backend-developer.md
│   │   ├── frontend-developer.md
│   │   └── devops-engineer.md
│   └── library/                    # Git submodule (if using)
│       ├── base/
│       ├── platforms/
│       ├── skills/
│       └── scripts/
├── src/                            # Your application code
├── tests/
└── README.md
```

## Configuration File

### Example config.yml

```yaml
# .ai-agents/config.yml

# Library path (if not using submodule in .ai-agents/library)
library_path: ".ai-agents/library"  # or absolute path

# Agent definitions
agents:
  # Backend Developer with project-specific skills
  backend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/backend-developer.md"
    skills:
      # Library skills
      - "skills/core/python-testing"
      - "skills/core/debugging"
      # Project skills (override library path)
      - "skills/custom/deploy-to-prod"
      - "skills/custom/run-integration-tests"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/coding-standards.md"
    output: ".ai-agents/composed/backend-developer.md"

  # DevOps Engineer focused on infrastructure
  devops_engineer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/infrastructure/devops-engineer.md"
    skills:
      - "skills/core/debugging"
      # Project-specific deployment
      - "skills/custom/deploy-to-prod"
      # Override library skill with project version
      - "skills/overrides/webapp-testing"
    project_context:
      - ".ai-agents/context/deployment-env.md"
      - ".ai-agents/context/infrastructure.md"
    output: ".ai-agents/composed/devops-engineer.md"

  # Frontend Developer
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "skills/core/debugging"
      - "skills/design/webapp-testing"
      - "skills/custom/create-jira-ticket"
    project_context:
      - ".ai-agents/context/architecture.md"
      - ".ai-agents/context/ui-standards.md"
    output: ".ai-agents/composed/frontend-developer.md"

# Skill resolution order (where to look for skills)
skill_paths:
  - ".ai-agents/skills"              # Project skills first (highest priority)
  - ".ai-agents/library/skills"      # Then library skills

# Context files available to all agents
global_context:
  - ".ai-agents/context/team-values.md"
  - ".ai-agents/context/communication-norms.md"
```

## Skill Resolution and Override Priority

### Resolution Order

When compose-agent.py looks for a skill, it searches in this order:

1. **Project skills** (`.ai-agents/skills/`)
2. **Library skills** (`.ai-agents/library/skills/`)

**Example:**

```yaml
# config.yml
agents:
  my_agent:
    skills:
      - "skills/core/python-testing"
```

**Resolution:**
1. First checks: `.ai-agents/skills/core/python-testing/SKILL.md`
2. If not found: `.ai-agents/library/skills/core/python-testing/SKILL.md`
3. If not found: Error

### Overriding Library Skills

To customize a library skill for your project:

**Step 1: Copy library skill to project**

```bash
# Copy skill to project overrides
mkdir -p .ai-agents/skills/overrides/webapp-testing
cp .ai-agents/library/skills/design/webapp-testing/SKILL.md \
   .ai-agents/skills/overrides/webapp-testing/SKILL.md
```

**Step 2: Modify for your project**

```markdown
<!-- .ai-agents/skills/overrides/webapp-testing/SKILL.md -->
---
name: webapp-testing
description: Web application testing customized for MyProject. Use Cypress for E2E tests, Jest for unit tests, and include performance tests for critical paths.
version: 1.0.0-myproject
author: MyProject Team
category: design
token_estimate: ~3000
---

# Web Application Testing (MyProject Version)

## Purpose

This is MyProject's customized version of webapp-testing that includes:
- Specific test frameworks we use (Cypress, Jest)
- Performance testing requirements
- MyProject-specific test data setup
- Integration with our CI/CD pipeline

[Rest of customized content...]
```

**Step 3: Reference in config**

```yaml
agents:
  my_agent:
    skills:
      - "skills/overrides/webapp-testing"  # Uses project version
```

**Result:** Agent loads your customized version instead of library version.

## Organizing Project Skills

### By Team

Organize skills by team ownership:

```
.ai-agents/skills/
├── backend-team/
│   ├── api-conventions/
│   ├── database-patterns/
│   └── deployment-backend/
├── frontend-team/
│   ├── component-library/
│   ├── state-management/
│   └── deployment-frontend/
├── devops-team/
│   ├── infrastructure-as-code/
│   ├── monitoring-setup/
│   └── incident-response/
└── qa-team/
    ├── test-automation/
    ├── performance-testing/
    └── security-testing/
```

### By Domain

Organize skills by domain or feature area:

```
.ai-agents/skills/
├── authentication/
│   ├── oauth-setup/
│   ├── session-management/
│   └── password-policies/
├── payment/
│   ├── stripe-integration/
│   ├── payment-testing/
│   └── pci-compliance/
├── notifications/
│   ├── email-templates/
│   ├── push-notifications/
│   └── notification-preferences/
└── analytics/
    ├── event-tracking/
    ├── metrics-dashboard/
    └── data-privacy/
```

### By Workflow

Organize skills by workflow or process:

```
.ai-agents/skills/
├── development/
│   ├── local-setup/
│   ├── debugging-guide/
│   └── code-review/
├── deployment/
│   ├── staging-deploy/
│   ├── production-deploy/
│   └── rollback/
├── testing/
│   ├── unit-testing/
│   ├── integration-testing/
│   └── e2e-testing/
└── operations/
    ├── monitoring/
    ├── incident-response/
    └── capacity-planning/
```

**Recommendation:** Choose organization that matches your team structure and workflow. Consistency matters more than specific approach.

## Versioning and Maintenance

### Skill Versioning

Use semantic versioning for project skills:

```yaml
---
name: deploy-to-prod
version: 2.1.0
---
```

- **Major (2.0.0 → 3.0.0):** Breaking changes, workflow restructuring
- **Minor (2.0.0 → 2.1.0):** New features, improvements, non-breaking changes
- **Patch (2.0.0 → 2.0.1):** Bug fixes, typos, clarifications

### Version Control Best Practices

**1. Commit skills separately:**

```bash
# Good: Clear what changed
git add .ai-agents/skills/custom/deploy-to-prod/
git commit -m "feat: Add rollback procedure to deployment skill (v2.1.0)"

# Avoid: Multiple unrelated changes
git add .ai-agents/skills/
git commit -m "Update skills"
```

**2. Tag skill releases:**

```bash
# Tag major skill updates
git tag skill/deploy-to-prod-v2.1.0
git push origin skill/deploy-to-prod-v2.1.0
```

**3. Document changes:**

```markdown
## Version History

### Version 2.1.0 (2025-01-20)
- Added automated rollback procedure
- Updated monitoring dashboard links
- Added example for blue-green deployments

### Version 2.0.0 (2025-01-10)
- **Breaking:** Restructured deployment steps
- Added Kubernetes-specific instructions
- Removed legacy Docker Swarm content
```

### Maintaining Skills

**Regular Review Schedule:**

- **Monthly:** Review skill usage, update examples
- **Quarterly:** Major updates, incorporate feedback
- **After Incidents:** Update with lessons learned
- **When Tools Change:** Update for new tool versions

**Maintenance Checklist:**

- [ ] Examples still work with current tool versions
- [ ] Links to external docs are not broken
- [ ] Commands are still correct
- [ ] Token estimate is accurate
- [ ] Reflects current team practices
- [ ] Incorporates recent lessons learned

### Deprecation Process

When replacing or removing a skill:

**Step 1: Mark as deprecated (1-2 months)**

```markdown
---
name: old-deployment-process
description: [DEPRECATED - Use deploy-to-prod instead] Old deployment process...
version: 1.5.0
---

# ⚠️ DEPRECATED

This skill is deprecated. Use `deploy-to-prod` instead.

**Migration Guide:** [Link to migration guide]

**Removal Date:** 2025-03-01
```

**Step 2: Remove from configs**

```yaml
agents:
  my_agent:
    skills:
      # - "skills/custom/old-deployment-process"  # Deprecated
      - "skills/custom/deploy-to-prod"             # Use this
```

**Step 3: Remove skill (after deprecation period)**

```bash
git rm -r .ai-agents/skills/custom/old-deployment-process
git commit -m "Remove deprecated old-deployment-process skill"
```

## Migration Path: Project Skill → Library Skill

When a project skill becomes useful for other projects:

**Step 1: Generalize the skill**

```bash
# Copy project skill to work area
cp -r .ai-agents/skills/custom/my-skill /tmp/my-skill-generalized

# Remove project-specific details:
# - Replace company/project names with placeholders
# - Remove internal tool references or generalize them
# - Abstract infrastructure-specific details
# - Update examples to be generic
```

**Step 2: Propose to library**

```bash
# In library repo
cd /path/to/AI_agents
git checkout -b feature/add-my-skill

# Copy generalized skill
cp -r /tmp/my-skill-generalized skills/custom/examples/my-skill

# Create PR
gh pr create --title "Add my-skill to library" \
  --body "Proposes adding my-skill for common use across projects..."
```

**Step 3: Update project to use library version**

```yaml
# After merged into library
agents:
  my_agent:
    skills:
      # - "skills/custom/my-skill"        # Old project version
      - "skills/custom/examples/my-skill"  # Now from library
```

**Step 4: Maintain project-specific override if needed**

```yaml
# If project needs customizations
agents:
  my_agent:
    skills:
      - "skills/overrides/my-skill"  # Project-specific version based on library
```

## Example Project Setups

### Example 1: E-commerce Application

```
ecommerce-app/
├── .ai-agents/
│   ├── config.yml
│   ├── skills/
│   │   ├── deployment/
│   │   │   ├── deploy-storefront/
│   │   │   ├── deploy-api/
│   │   │   └── deploy-admin/
│   │   ├── payment/
│   │   │   ├── stripe-integration/
│   │   │   └── payment-testing/
│   │   └── inventory/
│   │       ├── sync-inventory/
│   │       └── low-stock-alerts/
│   ├── context/
│   │   ├── architecture.md          # Microservices architecture
│   │   ├── payment-compliance.md    # PCI DSS requirements
│   │   └── inventory-logic.md       # Stock management rules
│   └── library/                     # Git submodule
└── services/
    ├── storefront/
    ├── api/
    └── admin/
```

### Example 2: SaaS Platform

```
saas-platform/
├── .ai-agents/
│   ├── config.yml
│   ├── skills/
│   │   ├── multi-tenant/
│   │   │   ├── tenant-provisioning/
│   │   │   └── tenant-isolation-testing/
│   │   ├── billing/
│   │   │   ├── subscription-management/
│   │   │   └── usage-tracking/
│   │   └── analytics/
│   │       ├── event-tracking/
│   │       └── metrics-dashboard/
│   ├── context/
│   │   ├── multi-tenancy.md         # Tenant isolation patterns
│   │   ├── billing-logic.md         # Subscription tiers
│   │   └── analytics-events.md      # Event schema
│   └── library/
└── platform/
    ├── api/
    ├── web/
    └── workers/
```

### Example 3: Mobile App Backend

```
mobile-backend/
├── .ai-agents/
│   ├── config.yml
│   ├── skills/
│   │   ├── api/
│   │   │   ├── mobile-api-conventions/
│   │   │   └── api-versioning/
│   │   ├── notifications/
│   │   │   ├── push-notifications/
│   │   │   └── notification-testing/
│   │   └── auth/
│   │       ├── mobile-auth-flow/
│   │       └── token-refresh/
│   ├── context/
│   │   ├── api-standards.md         # Mobile API conventions
│   │   ├── auth-architecture.md     # JWT token flow
│   │   └── notification-system.md   # Push notification setup
│   └── library/
└── api/
    ├── controllers/
    ├── models/
    └── services/
```

## Team Collaboration

### Skill Ownership

Assign ownership to ensure maintenance:

```yaml
# In SKILL.md frontmatter
---
name: deploy-to-prod
author: DevOps Team
owner: @alice
reviewer: @bob
---
```

### Contribution Process

**Creating New Project Skill:**

1. Identify need (repeated workflow, tribal knowledge)
2. Create skill using template
3. Test with agents
4. Submit for review (PR)
5. Iterate based on feedback
6. Merge and announce to team

**Updating Existing Skill:**

1. Make changes
2. Update version number
3. Document changes in Version History
4. Submit PR with clear change description
5. Get review from skill owner
6. Merge and notify users

### Documentation

Maintain a project skill catalog:

```markdown
<!-- .ai-agents/SKILLS_CATALOG.md -->

# Project Skills Catalog

## Deployment Skills

### deploy-to-prod
- **Description:** Production deployment workflow for all services
- **Owner:** @alice
- **Version:** 2.1.0
- **Last Updated:** 2025-01-20
- **Usage:** Used by backend_developer, devops_engineer agents

### rollback-production
- **Description:** Emergency rollback procedures
- **Owner:** @bob
- **Version:** 1.0.0
- **Last Updated:** 2025-01-15

## Testing Skills

### integration-test-suite
- **Description:** Run full integration test suite
- **Owner:** @charlie
- **Version:** 1.2.0
- **Last Updated:** 2025-01-18

[...]
```

## Troubleshooting

### Issue: Skill Not Found

**Symptoms:** compose-agent.py reports skill not found

**Solution:**
1. Verify skill path in config.yml
2. Check skill directory exists
3. Verify SKILL.md exists in skill directory
4. Check skill_paths in config.yml includes correct directories

### Issue: Wrong Skill Version Loading

**Symptoms:** Agent uses library version instead of project override

**Solution:**
1. Verify project skill path comes before library in skill_paths
2. Check skill name matches exactly (case-sensitive)
3. Verify SKILL.md exists in project skill directory

### Issue: Library Submodule Not Updating

**Symptoms:** Library updates not appearing in project

**Solution:**
```bash
# Update submodule
cd .ai-agents/library
git pull origin main
cd ../..
git add .ai-agents/library
git commit -m "Update library"

# If submodule seems broken
git submodule update --init --recursive
```

## Best Practices Summary

1. **Use Git Submodule** for library (stay updated)
2. **Project skills override library** (clear precedence)
3. **Organize skills consistently** (by team, domain, or workflow)
4. **Version and document changes** (track evolution)
5. **Regular maintenance** (keep current with tools/practices)
6. **Clear ownership** (assigned maintainers)
7. **Promote useful skills** (project → library migration)
8. **Test before committing** (validate with agents)

## Additional Resources

- [Custom Skills Guide](CUSTOM_SKILLS_GUIDE.md) - Creating custom skills
- [Quick Start](custom/QUICK_START.md) - 5-minute skill creation
- [Skills Template](custom/template/SKILL.md) - Skill template
- [compose-agent.py Documentation](../scripts/README.md) - Agent composition

---

**Questions?** Create an issue or consult your team's AI agents champion!
