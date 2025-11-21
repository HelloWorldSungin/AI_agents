# Skills Integration Guide

A comprehensive guide to using Anthropic Skills with the AI Agents Library to create specialized, capable agents for your multi-agent development teams.

**Version:** 1.0.0
**Last Updated:** 2025-11-20

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Available Skills Catalog](#available-skills-catalog)
4. [Skill Selection Guide](#skill-selection-guide)
5. [Skills vs Tools vs Platform Augmentations](#skills-vs-tools-vs-platform-augmentations)
6. [Configuration Examples](#configuration-examples)
7. [Token Budget Management](#token-budget-management)
8. [Custom Skills](#custom-skills)
9. [Advanced Topics](#advanced-topics)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)

---

## Introduction

### What are Anthropic Skills?

**Anthropic Skills** are modular instruction packages that extend AI agent capabilities with specialized knowledge, workflows, and tool integrations. They act as "onboarding guides" that transform general-purpose agents into domain experts.

Think of skills as training manuals that teach your agents how to perform specific tasks more effectively. Just like a new employee learns company-specific workflows through training, skills teach your AI agents specialized procedures and domain expertise.

### Integration with AI Agents Library

The AI Agents Library provides the foundation for multi-agent software development teams. Skills enhance this foundation by:

- **Adding specialized workflows**: Step-by-step procedures for complex tasks
- **Providing domain expertise**: Industry-specific knowledge and best practices
- **Enabling tool integrations**: Guidance for using external tools and APIs
- **Bundling resources**: Scripts, templates, and documentation

### Benefits for Multi-Agent Systems

**For Individual Agents:**
- Focused expertise in specific domains
- Improved task success rates
- Consistent application of best practices
- Reduced need for manual guidance

**For Agent Teams:**
- Clear role specialization
- Better task distribution
- Reduced overlap and conflicts
- More efficient collaboration

**For Projects:**
- Faster development cycles
- Higher code quality
- Better documentation
- Easier onboarding of new agents

---

## Getting Started

### Quick Start (5 Minutes)

**Step 1: Verify Skills Directory**
```bash
cd /path/to/AI_agents
ls -la skills/
# Should see: core/, communication/, design/, documents/, custom/
```

**Step 2: Choose a Skill**

For a frontend developer, start with `artifacts-builder`:
```yaml
# In your .ai-agents/config.yml
agents:
  frontend_developer:
    base: "base/software-developer.md"
    platforms:
      - "platforms/web/frontend-developer.md"
    skills:
      - "core/artifacts-builder"  # Add this line
```

**Step 3: Compose Agent**
```bash
cd .ai-agents/library
python scripts/compose-agent.py \
  --config ../../config.yml \
  --agent frontend_developer
```

**Step 4: Review Output**
```bash
✓ Saved: .ai-agents/composed/frontend_developer.md
  Tokens: 9,500 / 12,000 recommended
  Context usage: 4.75%
```

**Step 5: Deploy**

Use the composed prompt (`frontend_developer.md`) to initialize your agent with your LLM provider.

### Adding Your First Skill to an Agent

Let's walk through a complete example adding the `webapp-testing` skill to a QA tester:

**Before (No Skills):**
```yaml
# .ai-agents/config.yml
agents:
  qa_tester:
    base: "base/qa-tester.md"
    project_context:
      - ".ai-agents/context/test-plan.md"
    tools:
      - "tools/testing-tools.md"
```

**After (With Skill):**
```yaml
# .ai-agents/config.yml
agents:
  qa_tester:
    base: "base/qa-tester.md"
    skills:
      - "core/webapp-testing"  # ← New skill added
    project_context:
      - ".ai-agents/context/test-plan.md"
    tools:
      - "tools/testing-tools.md"
```

**Compose and Verify:**
```bash
python scripts/compose-agent.py --config config.yml --agent qa_tester

# Output:
Composing qa_tester...
✓ Saved: .ai-agents/composed/qa_tester.md
  Tokens: 8,200 / 12,000 recommended
  Context usage: 4.10%
```

**Test the Enhanced Agent:**

1. Initialize agent with the composed prompt
2. Give it a testing task: "Test the login form at localhost:3000"
3. Observe how it uses the webapp-testing skill to:
   - Start a browser with Playwright
   - Navigate to the page
   - Interact with form elements
   - Verify functionality
   - Capture screenshots if needed

### Testing Skill Integration

After adding a skill, verify it's working correctly:

**1. Check Composed File:**
```bash
grep -A 5 "## Skill: core/webapp-testing" .ai-agents/composed/qa_tester.md
```

Should show the skill content is included.

**2. Test with Sample Task:**

Give your agent a task that requires the skill:
- **For `artifacts-builder`**: "Create a React button component"
- **For `webapp-testing`**: "Test the homepage navigation"
- **For `mcp-builder`**: "Design an MCP server for the GitHub API"
- **For `theme-factory`**: "Apply the Ocean Depths theme to this component"

**3. Monitor Usage:**

Watch for the agent to reference the skill's guidance:
- Does it follow the skill's workflow?
- Does it use the skill's terminology?
- Does it produce better results than without the skill?

**4. Check Token Impact:**

```bash
python scripts/compose-agent.py --config config.yml --agent your_agent

# Before adding skill:
# Tokens: 6,000 / 12,000

# After adding skill:
# Tokens: 9,500 / 12,000  (+3,500 for the skill)
```

---

## Available Skills Catalog

### Core Development Skills

#### artifacts-builder

**Purpose**: Build interactive React components and web artifacts

**Use Cases**:
- Creating reusable UI components
- Building interactive demos
- Prototyping features
- Generating web artifacts

**Technologies**: React, Tailwind CSS, shadcn/ui

**Best For**: Frontend developers, UI designers

**Token Cost**: ~3,500 tokens

**Configuration**:
```yaml
frontend_developer:
  skills:
    - "core/artifacts-builder"
```

---

#### webapp-testing

**Purpose**: End-to-end testing of web applications with Playwright

**Use Cases**:
- Automated UI testing
- Browser automation
- Visual regression testing
- Integration testing

**Technologies**: Playwright, Python

**Best For**: QA testers, frontend developers

**Token Cost**: ~4,000 tokens

**Configuration**:
```yaml
qa_tester:
  skills:
    - "core/webapp-testing"
```

---

#### mcp-builder

**Purpose**: Design and build Model Context Protocol (MCP) servers

**Use Cases**:
- API integrations
- External service connectors
- Custom tool development
- Service abstraction layers

**Technologies**: TypeScript MCP SDK, Python FastMCP

**Best For**: Backend developers, architects

**Token Cost**: ~4,500 tokens

**Configuration**:
```yaml
backend_developer:
  skills:
    - "core/mcp-builder"
```

---

#### skill-creator

**Purpose**: Create custom skills with best practices

**Use Cases**:
- Developing project-specific skills
- Understanding skill architecture
- Improving existing skills
- Training team on skill development

**Best For**: Architects, senior developers

**Token Cost**: ~5,000 tokens

**Configuration**:
```yaml
architect:
  skills:
    - "core/skill-creator"
```

---

### Communication Skills

#### internal-comms

**Purpose**: Create professional internal communications

**Use Cases**:
- Team status updates (3P format)
- Project newsletters
- FAQ responses
- Incident reports
- Leadership updates

**Best For**: Managers, team leads

**Token Cost**: ~3,000 tokens

**Configuration**:
```yaml
team_manager:
  skills:
    - "communication/internal-comms"
```

---

### Design & Creative Skills

#### theme-factory

**Purpose**: Apply professional themes to UI components and artifacts

**Use Cases**:
- Consistent design application
- Brand styling
- Theme generation
- Visual identity

**Includes**: 10 pre-set themes + custom theme generation

**Best For**: Frontend developers, designers

**Token Cost**: ~2,500 tokens

**Configuration**:
```yaml
frontend_developer:
  skills:
    - "design/theme-factory"
```

---

#### algorithmic-art

**Purpose**: Create generative art and visualizations with p5.js

**Use Cases**:
- Data visualizations
- Interactive graphics
- Artistic content
- Visual effects

**Technologies**: p5.js, seeded randomness

**Best For**: Frontend developers, creative developers

**Token Cost**: ~3,000 tokens

**Configuration**:
```yaml
frontend_developer:
  skills:
    - "design/algorithmic-art"
```

---

#### canvas-design

**Purpose**: Generate visual assets in PNG and PDF formats

**Use Cases**:
- Graphics creation
- Asset generation
- Visual content

**Best For**: Frontend developers, designers

**Token Cost**: ~2,000 tokens

**Configuration**:
```yaml
frontend_developer:
  skills:
    - "design/canvas-design"
```

---

### Document Skills

#### docx

**Purpose**: Create and edit Microsoft Word documents

**Use Cases**:
- Technical documentation
- Reports
- Contracts
- Change tracking

**Best For**: Managers, QA testers, architects

**Token Cost**: ~3,500 tokens

**Configuration**:
```yaml
team_manager:
  skills:
    - "documents/docx"
```

---

#### pdf

**Purpose**: Manipulate PDF documents

**Use Cases**:
- Content extraction
- PDF creation
- Document merging
- Metadata handling

**Best For**: Managers, QA testers

**Token Cost**: ~3,000 tokens

**Configuration**:
```yaml
team_manager:
  skills:
    - "documents/pdf"
```

---

#### xlsx

**Purpose**: Create and edit Excel spreadsheets

**Use Cases**:
- Data reports
- Metrics dashboards
- Test data management
- Data exports

**Best For**: Managers, QA testers, backend developers

**Token Cost**: ~4,000 tokens

**Configuration**:
```yaml
team_manager:
  skills:
    - "documents/xlsx"
```

---

#### pptx

**Purpose**: Create and edit PowerPoint presentations

**Use Cases**:
- Project presentations
- Status reports
- Technical presentations
- Stakeholder updates

**Best For**: Managers, architects

**Token Cost**: ~3,500 tokens

**Configuration**:
```yaml
team_manager:
  skills:
    - "documents/pptx"
```

---

For complete details on all skills, see [CATALOG.md](skills/CATALOG.md).

---

## Skill Selection Guide

### Decision Tree: Which Skills for Which Agents?

```
START: What is the agent's primary role?
│
├─ MANAGER / TEAM LEAD
│  ├─ Communication required? → internal-comms (PRIMARY)
│  ├─ Metrics/Reporting? → xlsx (PRIMARY)
│  ├─ Documentation? → docx (SECONDARY)
│  └─ Presentations? → pptx (SECONDARY)
│
├─ FRONTEND DEVELOPER
│  ├─ Building components? → artifacts-builder (PRIMARY)
│  ├─ Styling/Theming? → theme-factory (PRIMARY)
│  ├─ Testing UI? → webapp-testing (SECONDARY)
│  └─ Visualizations? → algorithmic-art (OPTIONAL)
│
├─ BACKEND DEVELOPER
│  ├─ API Integrations? → mcp-builder (PRIMARY)
│  ├─ API Testing? → webapp-testing (SECONDARY)
│  └─ Data Exports? → xlsx (OPTIONAL)
│
├─ QA TESTER
│  ├─ UI Testing? → webapp-testing (PRIMARY)
│  ├─ Test Reports? → docx (SECONDARY)
│  └─ Test Data? → xlsx (SECONDARY)
│
├─ ARCHITECT
│  ├─ Creating skills? → skill-creator (PRIMARY)
│  ├─ System design? → mcp-builder (SECONDARY)
│  └─ Documentation? → docx (SECONDARY)
│
└─ MOBILE DEVELOPER
   ├─ UI Styling? → theme-factory (PRIMARY)
   ├─ Web views? → webapp-testing (OPTIONAL)
   └─ Asset creation? → canvas-design (OPTIONAL)
```

### Use Case → Skill Mapping

| Use Case | Primary Skill | Supporting Skills |
|----------|---------------|-------------------|
| **Building React UI** | artifacts-builder | theme-factory, webapp-testing |
| **API Development** | mcp-builder | - |
| **End-to-End Testing** | webapp-testing | - |
| **Team Management** | internal-comms | xlsx, docx, pptx |
| **Technical Documentation** | docx | pptx (for presentations) |
| **Data Analysis** | xlsx | pdf (for reports) |
| **Custom Workflows** | skill-creator | - |
| **UI Theming** | theme-factory | artifacts-builder |
| **Data Visualization** | algorithmic-art | canvas-design |
| **Report Generation** | docx, xlsx | pdf (for distribution) |

### Common Skill Combinations

**Full-Stack Web Developer:**
```yaml
fullstack_developer:
  skills:
    - "core/artifacts-builder"   # Frontend components
    - "core/mcp-builder"         # Backend integrations
    - "design/theme-factory"     # UI styling
```
**Token Total**: ~10,500 tokens

---

**UI/UX Specialist:**
```yaml
ui_specialist:
  skills:
    - "core/artifacts-builder"   # Component building
    - "design/theme-factory"     # Theming
    - "design/canvas-design"     # Asset creation
```
**Token Total**: ~8,000 tokens

---

**Test Engineer:**
```yaml
test_engineer:
  skills:
    - "core/webapp-testing"      # Automated testing
    - "documents/docx"           # Test reports
    - "documents/xlsx"           # Test data
```
**Token Total**: ~10,500 tokens

---

**Technical Lead:**
```yaml
tech_lead:
  skills:
    - "core/skill-creator"       # Team capabilities
    - "core/mcp-builder"         # Architecture
    - "communication/internal-comms"  # Team updates
```
**Token Total**: ~12,500 tokens

---

**Project Manager:**
```yaml
project_manager:
  skills:
    - "communication/internal-comms"  # Updates
    - "documents/xlsx"           # Metrics
    - "documents/pptx"           # Presentations
    - "documents/docx"           # Documentation
```
**Token Total**: ~14,000 tokens

---

## Skills vs Tools vs Platform Augmentations

### Clear Comparison

| Aspect | Skills | Tools | Platform Augmentations |
|--------|--------|-------|------------------------|
| **What They Are** | Instruction packages | Function definitions | Knowledge layers |
| **Purpose** | Teach workflows | Enable actions | Add expertise |
| **Format** | Markdown + resources | JSON schemas | Markdown prompts |
| **When Loaded** | At composition | Available always | At composition |
| **Token Impact** | 2-5k per skill | Minimal | 2-3k per platform |
| **Scope** | Task-specific | Action-specific | Platform-wide |
| **Examples** | artifacts-builder, mcp-builder | file_read, git_commit | frontend-developer.md |
| **Customizable** | Yes, easily | Yes, carefully | Yes, with caution |

### When to Use Each

#### Use Skills When:
- ✅ You need **domain expertise** (e.g., React best practices)
- ✅ You want **workflow guidance** (e.g., MCP server development process)
- ✅ You need **tool integration** instructions (e.g., Playwright usage)
- ✅ You want **reusable procedures** (e.g., theme application)

**Example**: Adding `artifacts-builder` skill teaches the agent how to build React components following best practices.

#### Use Tools When:
- ✅ You need **specific actions** (e.g., read a file, make HTTP request)
- ✅ You want **deterministic operations** (e.g., git commands)
- ✅ You need **external integrations** (e.g., database queries)
- ✅ You want **programmatic control** (e.g., API calls)

**Example**: Adding `file_read` tool allows the agent to read file contents.

#### Use Platform Augmentations When:
- ✅ You need **platform-wide expertise** (e.g., React knowledge)
- ✅ You want **framework proficiency** (e.g., Express.js patterns)
- ✅ You need **ecosystem knowledge** (e.g., npm, webpack)
- ✅ You want **platform best practices** (e.g., mobile UI guidelines)

**Example**: Adding `frontend-developer.md` augmentation provides comprehensive React, web APIs, and frontend ecosystem knowledge.

### How They Work Together

**Example: Frontend Developer Building a Login Form**

```yaml
frontend_developer:
  base: "base/software-developer.md"           # Universal engineering
  platforms:
    - "platforms/web/frontend-developer.md"    # React expertise
  skills:
    - "core/artifacts-builder"                 # Component building workflow
    - "design/theme-factory"                   # Styling guidance
  tools:
    - "tools/git-tools.md"                     # Git operations
    - "tools/testing-tools.md"                 # Test execution
  project_context:
    - ".ai-agents/context/api-contracts.md"    # Specific API info
```

**How each contributes:**

1. **Base**: Provides software engineering fundamentals
2. **Platform**: Knows React, JSX, hooks, component patterns
3. **Skills**: Guides through creating interactive component with proper structure
4. **Tools**: Enables git commits, running tests, file operations
5. **Context**: Provides project-specific API endpoints and authentication details

**Result**: Agent can build, style, test, and commit a login form that follows project standards.

---

## Configuration Examples

### Minimal Configuration (No Skills)

**Purpose**: Validate base agent functionality before adding complexity

```yaml
# Minimal software developer
minimal_developer:
  base: "base/software-developer.md"
  project_context:
    - ".ai-agents/context/architecture.md"
  tools:
    - "tools/git-tools.md"

# Token Budget: ~4,000 tokens
# Use Case: General-purpose development, learning system
```

---

### Standard Configuration (2-3 Skills)

**Purpose**: Production-ready agents with focused capabilities

#### Standard Frontend Developer
```yaml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/api-contracts.md"
  tools:
    - "tools/git-tools.md"
    - "tools/testing-tools.md"

# Token Budget: ~11,500 tokens
# Use Case: React UI development with theming
```

#### Standard Backend Developer
```yaml
backend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  skills:
    - "core/mcp-builder"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/database-schema.md"
  tools:
    - "tools/git-tools.md"
    - "tools/build-tools.md"

# Token Budget: ~10,000 tokens
# Use Case: API development and integrations
```

#### Standard QA Tester
```yaml
qa_tester:
  base: "base/qa-tester.md"
  skills:
    - "core/webapp-testing"
    - "documents/docx"
  project_context:
    - ".ai-agents/context/test-plan.md"
  tools:
    - "tools/testing-tools.md"

# Token Budget: ~8,500 tokens
# Use Case: Automated testing and reporting
```

---

### Advanced Configuration (4+ Skills)

**Purpose**: Highly specialized agents for complex roles

#### Advanced Team Manager
```yaml
team_manager:
  base: "base/manager.md"
  skills:
    - "communication/internal-comms"
    - "documents/xlsx"
    - "documents/docx"
    - "documents/pptx"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/workflows/feature-development.md"
  tools:
    - "tools/communication-tools.md"
  coordination:
    manages:
      - "frontend_developer"
      - "backend_developer"
      - "qa_tester"

# Token Budget: ~14,000 tokens
# Use Case: Full project management with documentation
# WARNING: Approaching token budget limit
```

#### Advanced Technical Architect
```yaml
technical_architect:
  base: "base/architect.md"
  skills:
    - "core/skill-creator"
    - "core/mcp-builder"
    - "documents/docx"
    - "documents/pptx"
  project_context:
    - ".ai-agents/context/architecture.md"
    - ".ai-agents/context/technical-decisions.md"
  tools:
    - "tools/analysis-tools.md"

# Token Budget: ~15,000 tokens
# Use Case: System design, skill development, documentation
# WARNING: High token usage - monitor carefully
```

---

### Specialized Configurations

#### UI/UX Specialist
```yaml
ui_specialist:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"
    - "design/algorithmic-art"
    - "design/canvas-design"
  project_context:
    - ".ai-agents/context/design-system.md"

# Token Budget: ~13,500 tokens
# Use Case: Advanced UI development and design
```

#### Integration Specialist
```yaml
integration_specialist:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  skills:
    - "core/mcp-builder"
    - "core/skill-creator"
  project_context:
    - ".ai-agents/context/api-integrations.md"
  tools:
    - "tools/build-tools.md"

# Token Budget: ~11,500 tokens
# Use Case: Building service integrations and connectors
```

#### Documentation Specialist
```yaml
documentation_specialist:
  base: "base/software-developer.md"
  skills:
    - "documents/docx"
    - "documents/pptx"
    - "documents/pdf"
    - "communication/internal-comms"
  project_context:
    - ".ai-agents/context/documentation-standards.md"

# Token Budget: ~13,000 tokens
# Use Case: Technical writing and presentation creation
```

---

## Token Budget Management

### How Skills Impact Token Usage

**Base Token Allocation:**
```
Claude Sonnet 4.5 Context: 200,000 tokens

Agent Prompt Budget: 6,000-12,000 tokens (3-6%)
├── Base Agent: 3,000-4,000 tokens
├── Platform: 2,000-3,000 tokens
├── Skills: 0-6,000 tokens ← Variable
└── Project Context: 1,000-2,000 tokens

Conversation Space: 188,000-194,000 tokens (94-97%)
```

### Calculating Your Agent's Budget

**Formula:**
```
Total Tokens = Base + Platform + Skills + Context

Where:
- Base: ~3,000-4,000
- Platform: ~2,000-3,000 (0 if no platform)
- Skills: (number_of_skills × avg_skill_size)
- Context: (number_of_context_files × avg_context_size)
```

**Example Calculation:**

```yaml
frontend_developer:
  base: "base/software-developer.md"           # 3,000 tokens
  platforms:
    - "platforms/web/frontend-developer.md"    # 2,500 tokens
  skills:
    - "core/artifacts-builder"                 # 3,500 tokens
    - "design/theme-factory"                   # 2,500 tokens
  project_context:
    - ".ai-agents/context/architecture.md"     # 500 tokens
    - ".ai-agents/context/api-contracts.md"    # 400 tokens

Total: 3,000 + 2,500 + 3,500 + 2,500 + 500 + 400 = 12,400 tokens
Status: ⚠️ Slightly over recommended budget (12,000)
```

### Optimization Strategies

#### Strategy 1: Skill Audit

Review actual skill usage:

```bash
# Track which skills are actually used
# In your project documentation:
Skill Usage Analysis (Last 30 Days):
- artifacts-builder: Used in 45/50 sessions → KEEP
- theme-factory: Used in 38/50 sessions → KEEP
- canvas-design: Used in 2/50 sessions → REMOVE
- algorithmic-art: Never used → REMOVE
```

**Action**: Remove unused skills to free up tokens.

#### Strategy 2: Agent Specialization

Instead of one agent with many skills, create specialized agents:

**Before:**
```yaml
# Super developer with all skills (18,000 tokens - too much!)
super_developer:
  skills:
    - "core/artifacts-builder"
    - "core/mcp-builder"
    - "core/webapp-testing"
    - "design/theme-factory"
    - "documents/docx"
```

**After:**
```yaml
# Specialized UI developer (11,500 tokens)
ui_developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"

# Specialized API developer (10,000 tokens)
api_developer:
  skills:
    - "core/mcp-builder"

# Specialized tester (8,500 tokens)
tester:
  skills:
    - "core/webapp-testing"
    - "documents/docx"
```

#### Strategy 3: Context Consolidation

Combine multiple small context files:

**Before:**
```yaml
project_context:
  - ".ai-agents/context/architecture.md"      # 500 tokens
  - ".ai-agents/context/coding-standards.md"  # 300 tokens
  - ".ai-agents/context/git-workflow.md"      # 200 tokens
  - ".ai-agents/context/ci-cd.md"             # 250 tokens
  - ".ai-agents/context/deployment.md"        # 300 tokens
# Total: 1,550 tokens across 5 files
```

**After:**
```yaml
project_context:
  - ".ai-agents/context/core-standards.md"    # 800 tokens (consolidated)
  - ".ai-agents/context/api-contracts.md"     # 400 tokens (kept separate)
# Total: 1,200 tokens across 2 files
# Savings: 350 tokens
```

#### Strategy 4: Progressive Skill Addition

Start minimal, add skills as needed:

**Phase 1: Validate Base (Week 1)**
```yaml
developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  # No skills yet
# Token Budget: 5,500 tokens
```

**Phase 2: Add Primary Skill (Week 2)**
```yaml
developer:
  skills:
    - "core/artifacts-builder"  # Most-needed skill
# Token Budget: 9,000 tokens
```

**Phase 3: Add Secondary Skills (Week 3+)**
```yaml
developer:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"    # Proven valuable
# Token Budget: 11,500 tokens
```

### Warning Systems

The composition script provides automatic warnings:

#### Green: Healthy Budget
```bash
✓ Tokens: 8,500 / 12,000 recommended
  Context usage: 4.25%
# No action needed
```

#### Yellow: Approaching Limit
```bash
✓ Tokens: 10,200 / 12,000 recommended
  Context usage: 5.10%
  ⚠️  Approaching token budget limit
  Remaining budget: 1,800 tokens
# Review skills, consider removing non-essential
```

#### Orange: Near Limit
```bash
✓ Tokens: 11,600 / 12,000 recommended
  Context usage: 5.80%
  ⚠️  Approaching token budget limit
  Remaining budget: 400 tokens
# Remove 1-2 skills or reduce context
```

#### Red: Over Budget
```bash
✓ Tokens: 13,200 / 12,000 recommended
  Context usage: 6.60%
  ⚠️  WARNING: Agent prompt exceeds recommended size!
  Recommendation: 1,200 tokens over budget

  Suggestions to reduce token usage:
  - Consider removing 3 skill(s)
  - Review 4 project context files
# Immediate action required
```

### Budget Recommendations by Team Size

| Team Size | Skills per Agent | Total Team Budget |
|-----------|------------------|-------------------|
| **Solo (1 agent)** | 3-5 skills | 12,000-18,000 tokens |
| **Small (2-3 agents)** | 2-3 skills | 20,000-35,000 tokens |
| **Medium (4-6 agents)** | 2-3 skills | 35,000-60,000 tokens |
| **Large (7+ agents)** | 1-2 skills | 50,000-80,000 tokens |

**Note**: Total team budget is cumulative across all agents. This still leaves 120,000-150,000 tokens for conversations.

---

## Custom Skills

### Creating Project-Specific Skills

Custom skills let you capture your organization's unique workflows and requirements.

#### Step-by-Step Guide

**Step 1: Identify the Need**

Good candidates for custom skills:
- ✅ Repeated workflows specific to your project
- ✅ Integration with proprietary systems
- ✅ Company-specific best practices
- ✅ Complex procedures that need consistency

Poor candidates:
- ❌ One-time tasks
- ❌ Trivial operations
- ❌ Already covered by existing skills
- ❌ Highly variable procedures

**Step 2: Copy the Template**
```bash
cd /path/to/AI_agents
cp -r skills/custom/template skills/custom/your-workflow-name
cd skills/custom/your-workflow-name
```

**Step 3: Edit SKILL.md**

Template structure:
```markdown
---
name: your-workflow-name
description: Brief description of what this skill does and when to use it
license: MIT
---

# Your Workflow Name

## Overview

Brief overview of the workflow...

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Prerequisites

- Required knowledge
- Required tools
- Required access

## Workflow Steps

### Step 1: Initial Setup

Detailed instructions...

### Step 2: Main Process

Detailed instructions...

### Step 3: Verification

How to verify success...

## Examples

### Example 1: Common Case

Concrete example...

### Example 2: Edge Case

Concrete example...

## Troubleshooting

### Issue: Common Problem

**Symptoms**: ...
**Solution**: ...

## Best Practices

1. Best practice 1
2. Best practice 2
3. Best practice 3

## Resources

- Link to internal docs
- Link to API documentation
- Link to examples
```

**Step 4: Add Supporting Resources** (Optional)

```bash
mkdir -p scripts references assets

# Add automation scripts
echo '#!/usr/bin/env python3' > scripts/helper.py

# Add reference documentation
echo '# API Reference' > references/api-guide.md

# Add templates or assets
echo '{}' > assets/template.json
```

**Step 5: Test the Skill**

```yaml
# test-config.yml
agents:
  test_agent:
    base: "base/software-developer.md"
    skills:
      - "custom/your-workflow-name"
```

```bash
python scripts/compose-agent.py --config test-config.yml --agent test_agent
```

**Step 6: Deploy to Team**

```yaml
# production config.yml
agents:
  backend_developer:
    skills:
      - "core/mcp-builder"
      - "custom/your-workflow-name"  # Your custom skill
```

#### Example Custom Skill

**Scenario**: Your company has a specific deployment workflow

**File**: `skills/custom/company-deployment/SKILL.md`

```markdown
---
name: company-deployment
description: Acme Corp deployment workflow for microservices
license: Internal Use Only
---

# Acme Corp Deployment Workflow

## Overview

This skill provides step-by-step guidance for deploying microservices
to Acme Corp's Kubernetes infrastructure following security and
compliance requirements.

## When to Use This Skill

- Deploying to staging environment
- Deploying to production environment
- Rolling back deployments
- Blue-green deployment scenarios

## Prerequisites

- Access to Acme Corp VPN
- kubectl configured with company cluster
- Deployment checklist approval
- Security scan completion

## Workflow Steps

### Step 1: Pre-Deployment Checks

1. Verify security scan passed (./scripts/verify-scan.sh)
2. Check deployment checklist signed off
3. Verify no active incidents (check status.acme.corp)
4. Ensure change window is open

### Step 2: Staging Deployment

1. Switch to staging context:
   ```bash
   kubectl config use-context staging-us-east-1
   ```

2. Apply deployment manifest:
   ```bash
   kubectl apply -f k8s/deployment-staging.yaml
   ```

3. Monitor rollout:
   ```bash
   kubectl rollout status deployment/<service-name>
   ```

4. Run smoke tests:
   ```bash
   ./scripts/smoke-test.sh staging
   ```

### Step 3: Production Deployment

[... detailed steps ...]

## Resources

- [Deployment Checklist](https://wiki.acme.corp/deployments)
- [Runbook](https://runbook.acme.corp)
- [Incident Response](https://incidents.acme.corp)
```

### Link to Detailed Guide

For comprehensive guidance on creating effective skills, including:
- Progressive disclosure patterns
- Resource bundling strategies
- Testing methodologies
- Version management

See [skills/INTEGRATION.md](skills/INTEGRATION.md#creating-custom-skills).

### Example Custom Skills Repository

Consider creating a separate repository for your organization's custom skills:

```
acme-corp-skills/
├── README.md
├── deployment/
│   └── SKILL.md
├── code-review/
│   └── SKILL.md
├── security-scan/
│   └── SKILL.md
└── documentation/
    └── SKILL.md
```

Then reference as a git submodule:
```bash
cd AI_agents/skills
git submodule add git@github.com:acme-corp/acme-corp-skills.git acme
```

---

## Advanced Topics

### Skills That Reference Other Skills

Some skills build upon others. The `skill-creator` skill, for instance, teaches how to create skills that might reference existing skills.

**Example Configuration:**
```yaml
architect:
  skills:
    - "core/skill-creator"    # Teaches skill creation
    - "core/mcp-builder"      # Example of well-structured skill
```

The architect can then create new skills following patterns from existing ones.

### Conditional Skill Loading

Future enhancement: Load skills based on task context.

**Concept** (not yet implemented):
```yaml
frontend_developer:
  skills:
    always:
      - "core/artifacts-builder"
    conditional:
      - skill: "core/webapp-testing"
        when: "task.type == 'testing'"
      - skill: "design/algorithmic-art"
        when: "task.requires == 'visualization'"
```

**Current Workaround**: Create specialized agent variants:

```yaml
frontend_developer_standard:
  skills:
    - "core/artifacts-builder"
    - "design/theme-factory"

frontend_developer_testing:
  skills:
    - "core/artifacts-builder"
    - "core/webapp-testing"
    - "design/theme-factory"
```

### Project-Specific Skill Overrides

Projects can override library skills by placing custom versions in `.ai-agents/skills/`.

**Use Case**: Your project uses a modified workflow for MCP server development.

**Implementation**:
```bash
# In your project
mkdir -p .ai-agents/skills/core
cp /path/to/AI_agents/skills/core/mcp-builder.md .ai-agents/skills/core/
# Edit .ai-agents/skills/core/mcp-builder.md with your customizations
```

**Resolution**:
```yaml
backend_developer:
  skills:
    - "core/mcp-builder"  # Will load from project override, not library
```

The composition script checks project skills directory first, then library.

### Version Management

#### Library Version Pinning

Lock to specific versions to ensure consistency:

```yaml
agent_library:
  repo: "git@github.com:org/AI_agents.git"
  version: "1.0.0"
  update_strategy: "manual"
```

#### Skill Version Tracking

Document which versions of skills are in use:

```markdown
# skills-manifest.md

Current Skill Versions:
- artifacts-builder: v1.2.0 (from Anthropic Skills 2024-11-15)
- theme-factory: v1.0.0 (from Anthropic Skills 2024-11-15)
- mcp-builder: v1.3.0 (from Anthropic Skills 2024-11-15)
- company-deployment: v2.1.0 (custom skill)

Last Updated: 2025-11-20
```

#### Updating Skills

**Anthropic Skills Update:**
```bash
# If using git submodule
cd skills/anthropic
git pull origin main
cd ../..
git add skills/anthropic
git commit -m "Update Anthropic skills to latest"

# Recompose agents to pick up changes
python scripts/compose-agent.py --config config.yml --all
```

**Custom Skills Update:**
```bash
# Update custom skill
vi skills/custom/your-skill/SKILL.md
# Increment version in frontmatter

# Update version manifest
vi skills/custom/versions.md

# Recompose affected agents
python scripts/compose-agent.py --config config.yml --agent affected_agent
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Skill Not Found

**Symptoms:**
```bash
python scripts/compose-agent.py --config config.yml --agent developer

Warning: Skill not found: my-skill
  Searched in library: skills/my-skill.md
  Searched in project: .ai-agents/skills/my-skill.md
```

**Solutions:**

1. **Check skill name format**:
   ```yaml
   # Wrong
   skills:
     - "my-skill"  # Looks in skills/core/my-skill.md

   # Right (if skill is in custom/)
   skills:
     - "custom/my-skill"
   ```

2. **Verify skill file exists**:
   ```bash
   ls -la skills/custom/my-skill/SKILL.md
   # or
   ls -la skills/core/my-skill.md
   ```

3. **Check file permissions**:
   ```bash
   chmod +r skills/custom/my-skill/SKILL.md
   ```

---

#### Issue: Token Budget Exceeded

**Symptoms:**
```bash
⚠️  WARNING: Agent prompt exceeds recommended size!
Recommendation: 2,500 tokens over budget
```

**Solutions:**

1. **Remove least-used skills**:
   ```yaml
   # Before (14,500 tokens)
   skills:
     - "core/artifacts-builder"
     - "design/theme-factory"
     - "core/webapp-testing"
     - "design/canvas-design"

   # After (11,500 tokens)
   skills:
     - "core/artifacts-builder"
     - "design/theme-factory"
   # Removed webapp-testing (move to QA agent)
   # Removed canvas-design (rarely used)
   ```

2. **Consolidate context files**:
   ```bash
   # Merge multiple small files into one
   cat context/file1.md context/file2.md > context/combined.md
   ```

3. **Create specialized agents**:
   ```yaml
   # Split one heavy agent into two focused agents
   ui_developer:
     skills: ["core/artifacts-builder", "design/theme-factory"]

   test_developer:
     skills: ["core/webapp-testing"]
   ```

---

#### Issue: Skill Not Being Used

**Symptoms:**
- Agent has skill loaded but doesn't reference it
- Agent doesn't follow skill's workflow
- Results not improved despite skill

**Diagnosis:**

1. **Verify skill is loaded**:
   ```bash
   grep "Skill: your-skill" .ai-agents/composed/agent.md
   ```

2. **Check task matches skill's use case**:
   - `artifacts-builder`: Only for React component tasks
   - `webapp-testing`: Only for browser testing tasks
   - `mcp-builder`: Only for MCP server development

3. **Review skill quality**:
   - Is the skill too vague?
   - Does it have concrete examples?
   - Is it well-structured?

**Solutions:**

1. **Improve skill instructions**:
   ```markdown
   # Bad (vague)
   Build the component properly.

   # Good (specific)
   ## Component Structure
   1. Create functional component with TypeScript
   2. Define props interface
   3. Implement component logic
   4. Add Tailwind CSS classes
   5. Export component
   ```

2. **Add more examples**:
   ```markdown
   ## Example: Button Component
   \`\`\`typescript
   interface ButtonProps {
     label: string;
     onClick: () => void;
   }

   export const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
     return (
       <button
         onClick={onClick}
         className="px-4 py-2 bg-blue-500 text-white rounded"
       >
         {label}
       </button>
     );
   };
   \`\`\`
   ```

3. **Explicitly reference the skill**:
   ```markdown
   When building React components, follow the artifacts-builder workflow...
   ```

---

#### Issue: Agent Performance Degraded

**Symptoms:**
- Agent slower after adding skills
- Lower quality responses
- Confusion or inconsistency

**Diagnosis:**

1. **Check token budget**:
   ```bash
   python scripts/compose-agent.py --config config.yml --agent affected_agent
   # Look for warnings
   ```

2. **Review skill conflicts**:
   - Do multiple skills provide overlapping guidance?
   - Are skills contradicting each other?

3. **Check context overflow**:
   - Is agent hitting context limits during conversation?

**Solutions:**

1. **Remove redundant skills**:
   ```yaml
   # Before (overlapping)
   skills:
     - "core/artifacts-builder"  # Includes testing guidance
     - "core/webapp-testing"     # Overlaps with artifacts-builder

   # After (focused)
   skills:
     - "core/artifacts-builder"  # Keep primary skill
   # Move webapp-testing to dedicated QA agent
   ```

2. **Consolidate related skills into custom skill**:
   ```bash
   # Create unified workflow
   cp -r skills/custom/template skills/custom/our-react-workflow
   # Combine artifacts-builder + theme-factory into single skill
   ```

3. **Monitor context usage**:
   - Add checkpoints more frequently
   - Compress older context aggressively

---

#### Issue: Debugging Skill Loading

**Symptoms:**
- Uncertain if skill is actually loaded
- Need to verify skill content

**Solutions:**

1. **Check composed output**:
   ```bash
   # Find skill sections
   grep -n "## Skill:" .ai-agents/composed/agent.md

   # View skill content
   sed -n '/## Skill: artifacts-builder/,/## /p' .ai-agents/composed/agent.md | head -50
   ```

2. **Verify resolution**:
   ```bash
   # Add debug output to compose-agent.py
   python scripts/compose-agent.py --config config.yml --agent developer 2>&1 | grep -i skill
   ```

3. **Manual composition test**:
   ```python
   # test_composition.py
   from pathlib import Path
   import sys
   sys.path.insert(0, 'scripts')
   from compose_agent import AgentComposer

   library_path = Path('/path/to/AI_agents')
   project_path = Path('/path/to/project')
   composer = AgentComposer(library_path, project_path)

   skill_path = composer.resolve_skill_path('artifacts-builder')
   print(f"Resolved to: {skill_path}")
   print(f"Exists: {skill_path.exists() if skill_path else False}")
   ```

---

## Best Practices

### Skill Selection Strategies

1. **Start with Role-Based Essentials**
   ```yaml
   # Identify agent's primary function
   frontend_developer:
     skills:
       - "core/artifacts-builder"  # Essential for role

   # Don't add skills just because they exist
   ```

2. **Add Skills Based on Actual Need**
   ```markdown
   Week 1: No skills - validate base agent
   Week 2: artifacts-builder - primary need identified
   Week 3: theme-factory - consistent styling needed
   Week 4: Review usage, keep or remove
   ```

3. **Monitor and Adjust**
   ```markdown
   Monthly Skill Review:
   - Which skills used most frequently?
   - Which skills improved outcomes?
   - Which skills never referenced?
   - Action: Remove unused, add requested
   ```

### Maintenance and Updates

1. **Regular Skill Audits**
   ```bash
   # Schedule quarterly
   # Review: skills/audit-$(date +%Y-%m).md

   ## Skills Audit: November 2025

   ### High Value (Keep)
   - artifacts-builder: 95% usage rate
   - mcp-builder: 88% usage rate

   ### Medium Value (Monitor)
   - theme-factory: 60% usage rate
   - webapp-testing: 55% usage rate

   ### Low Value (Remove)
   - canvas-design: 5% usage rate → REMOVE
   - algorithmic-art: 2% usage rate → REMOVE
   ```

2. **Version Tracking**
   ```markdown
   # SKILLS_VERSIONS.md

   ## Current Versions (2025-11-20)

   ### Anthropic Skills
   - Source: github.com/anthropics/skills @ abc123
   - Last Updated: 2025-11-15
   - Skills: artifacts-builder, mcp-builder, theme-factory, ...

   ### Custom Skills
   - company-deployment: v2.1.0
   - internal-workflows: v1.5.0
   - security-scan: v3.0.1

   ## Update Schedule
   - Anthropic Skills: Monthly (first Tuesday)
   - Custom Skills: As needed with version increments
   ```

3. **Update Procedure**
   ```bash
   # 1. Update library
   cd AI_agents
   git pull origin main

   # 2. Update Anthropic skills (if submodule)
   cd skills/anthropic
   git pull origin main
   cd ../..

   # 3. Test in staging
   python scripts/compose-agent.py --config staging-config.yml --all

   # 4. Verify token budgets
   # Check for warnings

   # 5. Test with sample tasks
   # Ensure no regressions

   # 6. Deploy to production
   python scripts/compose-agent.py --config config.yml --all

   # 7. Update version tracking
   vi SKILLS_VERSIONS.md
   ```

### Testing Approaches

1. **Unit Testing: Individual Skills**
   ```bash
   # Test skill composition
   python scripts/compose-agent.py \
     --config test-configs/skill-test.yml \
     --agent test_agent

   # Verify skill loaded
   grep "Skill: artifacts-builder" composed/test_agent.md

   # Check token count
   # Expected: ~3,500 tokens for this skill
   ```

2. **Integration Testing: Complete Agent**
   ```yaml
   # test-configs/full-test.yml
   test_agent:
     base: "base/software-developer.md"
     platforms:
       - "platforms/web/frontend-developer.md"
     skills:
       - "core/artifacts-builder"
       - "design/theme-factory"
     project_context:
       - "test-context/minimal.md"
   ```

   ```bash
   # Compose and verify
   python scripts/compose-agent.py --config test-configs/full-test.yml --agent test_agent

   # Check total tokens
   # Expected: ~11,000 tokens

   # Test with real LLM
   # Give agent a task using composed prompt
   ```

3. **Acceptance Testing: Real Tasks**
   ```markdown
   ## Skill Testing Checklist

   Agent: frontend_developer
   Skill: artifacts-builder

   ### Test Cases
   - [ ] Create button component
   - [ ] Create form with validation
   - [ ] Create data table with sorting
   - [ ] Create modal dialog

   ### Success Criteria
   - [ ] Components follow React best practices
   - [ ] Code is properly typed (TypeScript)
   - [ ] Styling uses Tailwind CSS
   - [ ] Components are reusable
   - [ ] Code quality improved vs without skill

   ### Results
   - 4/4 test cases passed
   - Average quality score: 9.2/10
   - Decision: KEEP skill
   ```

### Documentation Standards

1. **Skill Documentation Template**
   ```markdown
   # Skill: [Skill Name]

   ## Metadata
   - **Category**: core|communication|design|documents|custom
   - **Version**: X.Y.Z
   - **Token Cost**: ~X,XXX tokens
   - **Recommended For**: [Agent types]
   - **Prerequisites**: [Required knowledge/tools]

   ## Purpose
   One-paragraph description...

   ## Use Cases
   - Use case 1
   - Use case 2
   - Use case 3

   ## Workflow
   Step-by-step guide...

   ## Examples
   Concrete examples...

   ## Best Practices
   Tips and recommendations...

   ## Related Skills
   - skill-1: [relationship]
   - skill-2: [relationship]

   ## Resources
   - Internal documentation
   - External references
   ```

2. **Agent Configuration Documentation**
   ```yaml
   # agents/frontend-developer.md

   # Frontend Developer Agent

   ## Configuration

   \`\`\`yaml
   frontend_developer:
     base: "base/software-developer.md"
     platforms:
       - "platforms/web/frontend-developer.md"
     skills:
       - "core/artifacts-builder"
       - "design/theme-factory"
   \`\`\`

   ## Token Budget
   - Base: 3,000 tokens
   - Platform: 2,500 tokens
   - Skills: 6,000 tokens (2 skills)
   - Context: 1,000 tokens
   - **Total**: 12,500 tokens (⚠️ slightly over recommended)

   ## Skill Rationale
   - **artifacts-builder**: Primary skill for React component development
   - **theme-factory**: Ensures consistent UI styling across project

   ## Usage Notes
   - Best for UI implementation tasks
   - Excels at creating reusable components
   - Strong at styling with Tailwind CSS
   - Can perform basic testing

   ## Limitations
   - Not specialized for testing (use qa_tester for that)
   - Limited backend knowledge
   - Token budget near limit (avoid adding more skills)
   ```

3. **Project Skills Manifest**
   ```yaml
   # PROJECT_SKILLS.md

   # Project Skills Manifest

   ## Agents and Their Skills

   ### team_manager
   - communication/internal-comms (v1.0, 3k tokens)
   - documents/xlsx (v1.0, 4k tokens)
   - documents/docx (v1.0, 3.5k tokens)
   **Total**: 10.5k tokens

   ### frontend_developer
   - core/artifacts-builder (v1.2, 3.5k tokens)
   - design/theme-factory (v1.0, 2.5k tokens)
   **Total**: 6k tokens

   ### backend_developer
   - core/mcp-builder (v1.3, 4.5k tokens)
   **Total**: 4.5k tokens

   ### qa_tester
   - core/webapp-testing (v1.1, 4k tokens)
   - documents/docx (v1.0, 3.5k tokens)
   **Total**: 7.5k tokens

   ## Team Total
   **28.5k tokens** across 4 agents

   ## Last Updated
   2025-11-20
   ```

---

## FAQ

### General Questions

**Q: Do I need skills for my agents to work?**

A: No. Skills are optional enhancements. Agents work fine with just base + platform + project context. Add skills when you need specialized capabilities.

---

**Q: How many skills should I assign per agent?**

A: **Recommended**: 1-3 skills per agent
- 0 skills: Valid for simple, general-purpose agents
- 1-2 skills: Ideal for most agents
- 3-4 skills: Acceptable for specialized roles
- 5+ skills: ⚠️ Approaching token limits, carefully justify each

---

**Q: Can I use the same skill with multiple agents?**

A: Yes! Skills are reusable. For example, both frontend and backend developers might use `webapp-testing`:

```yaml
frontend_developer:
  skills:
    - "core/webapp-testing"

backend_developer:
  skills:
    - "core/webapp-testing"
```

---

**Q: What's the difference between skills and tools?**

A:
- **Skills** = Instructions/knowledge (markdown documents)
- **Tools** = Actions/functions (callable APIs)

Skills teach agents **how** to do things. Tools give agents **actions** they can take.

Example:
- **Tool**: `file_read(path)` - reads a file
- **Skill**: `artifacts-builder` - teaches how to build React components

---

**Q: Are Anthropic Skills required?**

A: No. The library works without Anthropic Skills. They're optional enhancements. You can:
- Use no skills
- Use only Anthropic Skills
- Use only custom skills
- Use a mix of both

---

### Configuration Questions

**Q: How do I reference a skill in a different category?**

A: Use the full path with category:

```yaml
skills:
  - "core/artifacts-builder"      # In core/ category
  - "design/theme-factory"        # In design/ category
  - "documents/xlsx"              # In documents/ category
  - "custom/my-workflow"          # In custom/ category
```

---

**Q: Can I override an Anthropic skill with my own version?**

A: Yes! Place your version in `.ai-agents/skills/` in your project:

```bash
# Your project
.ai-agents/
└── skills/
    └── core/
        └── mcp-builder.md  # Your customized version

# Library
AI_agents/
└── skills/
    └── core/
        └── mcp-builder.md  # Original version
```

The composition script checks project skills first, so yours will be used.

---

**Q: What happens if a skill isn't found?**

A: The composition script:
1. Issues a warning
2. Continues composing the agent
3. Agent is still usable, just without that skill

```bash
Warning: Skill not found: my-skill
  Searched in library: skills/my-skill.md
  Searched in project: .ai-agents/skills/my-skill.md
```

---

### Token Budget Questions

**Q: How do I know if I'm over budget?**

A: The composition script tells you:

```bash
python scripts/compose-agent.py --config config.yml --agent developer

✓ Tokens: 13,200 / 12,000 recommended
  ⚠️  WARNING: Agent prompt exceeds recommended size!
```

---

**Q: What's the actual token limit?**

A:
- **Context window**: 200,000 tokens (Claude Sonnet 4.5)
- **Recommended agent prompt**: < 12,000 tokens (6% of context)
- **Conversation space**: 188,000+ tokens (94% of context)

Going over 12,000 tokens is possible but leaves less room for conversation.

---

**Q: Can I use more skills if I reduce project context?**

A: Yes! It's a tradeoff:

```yaml
# Option A: More skills, less context
agent:
  skills: [skill1, skill2, skill3, skill4]  # 12k tokens
  project_context: ["minimal.md"]            # 500 tokens

# Option B: Fewer skills, more context
agent:
  skills: [skill1, skill2]                   # 6k tokens
  project_context:                            # 3k tokens
    - "architecture.md"
    - "api-contracts.md"
    - "coding-standards.md"
```

---

**Q: Do skills slow down the agent?**

A: Skills don't affect agent speed directly. However:
- More tokens = slightly longer initial processing
- Once loaded, skills are just part of the context
- Impact is minimal (milliseconds, not seconds)

---

### Custom Skills Questions

**Q: How do I create a custom skill?**

A:
1. Copy template: `cp -r skills/custom/template skills/custom/my-skill`
2. Edit `SKILL.md` with your instructions
3. Reference in config: `skills: ["custom/my-skill"]`
4. Compose agent

See [Custom Skills](#custom-skills) section for details.

---

**Q: Can custom skills reference other skills?**

A: Yes, but:
- The other skill must be loaded separately
- Reference by name in your skill's instructions
- Don't duplicate content from other skills

```yaml
architect:
  skills:
    - "core/skill-creator"        # Loaded
    - "core/mcp-builder"          # Loaded
    - "custom/our-integration"    # Can reference both above
```

---

**Q: Should I create a custom skill or add to project context?**

A:

**Create a custom skill when:**
- ✅ Workflow is reusable across tasks
- ✅ Procedure is complex and needs structure
- ✅ You want to share with multiple agents
- ✅ It's a specialized domain

**Add to project context when:**
- ✅ Information is project-specific
- ✅ It's reference data (APIs, schemas, conventions)
- ✅ Changes frequently
- ✅ Simple facts, not workflows

---

### Troubleshooting Questions

**Q: My agent has a skill but doesn't use it. Why?**

A:
1. **Verify it's loaded**: Check composed file for skill content
2. **Match use case**: Ensure task matches skill's purpose
3. **Improve skill**: Make instructions more concrete and specific
4. **Check examples**: Add more examples to the skill

---

**Q: Skills made my agent worse. What happened?**

A: Possible causes:
1. **Token budget exceeded**: Check if agent is over recommended limit
2. **Conflicting guidance**: Multiple skills providing contradictory advice
3. **Skill quality**: Poorly written skill confusing the agent
4. **Not needed**: Skill doesn't match agent's actual tasks

Solution: Remove skills one by one to identify the problematic one.

---

**Q: How do I debug skill loading?**

A:
```bash
# 1. Check composed file
grep "## Skill:" .ai-agents/composed/agent.md

# 2. View skill content in composed file
sed -n '/## Skill: my-skill/,/## /p' .ai-agents/composed/agent.md

# 3. Check resolution
python -c "
from pathlib import Path
from scripts.compose_agent import AgentComposer
composer = AgentComposer(Path('AI_agents'), Path('project'))
print(composer.resolve_skill_path('my-skill'))
"
```

---

**Q: Can I load skills conditionally based on task?**

A: Not currently. Skills are loaded at composition time, not runtime.

**Workaround**: Create agent variants:

```yaml
developer_standard:
  skills: ["core/artifacts-builder"]

developer_testing:
  skills: ["core/artifacts-builder", "core/webapp-testing"]
```

---

### Integration Questions

**Q: Do skills work with all LLM providers?**

A: Yes. Skills are just markdown instructions in the prompt. They work with:
- Anthropic Claude (all versions)
- OpenAI GPT (3.5, 4, 4-turbo)
- Other LLMs with sufficient context windows

Note: Token budgets may vary by model.

---

**Q: Can I use skills without the AI Agents Library?**

A: Yes! Skills are standalone. You can:
1. Copy skill files to your project
2. Include in your custom prompts
3. Use with any LLM

The AI Agents Library just provides convenient composition tooling.

---

**Q: How do skills interact with RAG/vector databases?**

A: They're complementary:
- **Skills**: Workflows and procedures (always in context)
- **RAG**: Reference information (retrieved when needed)

Example:
- Skill: "How to deploy" (workflow always available)
- RAG: "Past deployment incidents" (retrieved if relevant)

---

**Q: Where can I find more skills?**

A:
1. **Anthropic Skills Repository**: [github.com/anthropics/skills](https://github.com/anthropics/skills)
2. **Library Catalog**: [skills/CATALOG.md](skills/CATALOG.md)
3. **Create Your Own**: Use the template in `skills/custom/template/`
4. **Community**: Share and discover in project discussions

---

**Q: How often are Anthropic Skills updated?**

A: Anthropic updates their skills repository periodically.

**Staying Updated**:
```bash
# If using git submodule
cd skills/anthropic
git pull origin main

# Check for changes
git log --oneline --since="1 month ago"

# Update your agents
cd ../..
python scripts/compose-agent.py --config config.yml --all
```

---

**Q: Can I contribute skills back to the community?**

A: Yes!
1. **To Anthropic**: Follow their contribution guidelines
2. **To AI Agents Library**: Submit PR with your custom skill in `skills/community/`
3. **To Your Organization**: Maintain internal skills repository

---

## Resources

### Documentation

- [README.md](README.md) - Library overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture with Skills Integration section
- [skills/README.md](skills/README.md) - Skills overview
- [skills/CATALOG.md](skills/CATALOG.md) - Complete skills directory
- [skills/INTEGRATION.md](skills/INTEGRATION.md) - Technical integration guide
- [Context_Engineering.md](Context_Engineering.md) - Foundational principles

### External Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official skills collection
- [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills) - Official documentation
- [Claude Documentation](https://docs.anthropic.com/) - Claude API and capabilities

### Examples

- [examples/web-app-team/](examples/web-app-team/) - Full-stack team with skills
- [examples/mobile-app-team/](examples/mobile-app-team/) - Mobile development team
- [skills/custom/template/](skills/custom/template/) - Custom skill template

---

## Support

### Getting Help

**For Skill Usage Questions:**
- Review this guide's [Troubleshooting](#troubleshooting) section
- Check [skills/CATALOG.md](skills/CATALOG.md) for specific skill details
- Consult individual skill SKILL.md files

**For Custom Skill Development:**
- Review [Custom Skills](#custom-skills) section
- Study existing skills in `skills/core/` for patterns
- Use `skill-creator` skill for guided development

**For Technical Issues:**
- Check [Troubleshooting](#troubleshooting) section first
- Review GitHub Issues for similar problems
- Enable debug output in compose-agent.py

**For General Library Questions:**
- See main [README.md](README.md)
- Check [ARCHITECTURE.md](ARCHITECTURE.md)
- Consult [examples/](examples/) for working configurations

### Community

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share experiences
- **Examples**: Contribute your agent configurations

---

## Changelog

### Version 1.0.0 (2025-11-20)

**Initial Release:**
- Comprehensive skills integration guide
- 14 Anthropic skills documented
- Custom skills framework
- Token budget management guidance
- Complete examples and troubleshooting
- FAQ with 25+ common questions

---

**Ready to enhance your agents with skills?** Start with the [Quick Start](#getting-started) section and compose your first skilled agent in 5 minutes!
