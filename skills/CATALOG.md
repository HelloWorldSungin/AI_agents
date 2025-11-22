# Skills Catalog

Complete directory of available skills organized by category, with descriptions and recommended agent assignments.

**Version:** 1.0.0
**Last Updated:** 2025-11-20

---

## Table of Contents

1. [Core Development Skills](#core-development-skills)
2. [Communication Skills](#communication-skills)
3. [Design & Creative Skills](#design--creative-skills)
4. [Document Skills](#document-skills)
5. [Custom Skills](#custom-skills)
6. [Agent Skill Matrix](#agent-skill-matrix)

---

## Core Development Skills

Technical skills for software development, testing, and infrastructure.

### artifacts-builder

**Path**: `skills/core/artifacts-builder` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~3,500 tokens

**Description**: Complex HTML artifact creation using React, Tailwind CSS, and shadcn/ui. Enables agents to build interactive web components and applications with modern frontend technologies.

**Capabilities**:
- React component development
- Tailwind CSS styling
- shadcn/ui component integration
- Interactive artifact creation
- Responsive design implementation

**When to Use**:
- Building interactive UI components
- Creating web artifacts for demonstrations
- Prototyping frontend features
- Generating reusable React components

**Recommended For**:
- Frontend Developer (PRIMARY)
- Software Developer (SECONDARY)

**Dependencies**: None

**Example Usage**:
```yaml
frontend_developer:
  skills:
    - "skills/core/artifacts-builder"
```

---

### webapp-testing

**Path**: `skills/core/webapp-testing` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~4,000 tokens

**Description**: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing screenshots, and viewing browser logs.

**Capabilities**:
- Playwright-based browser automation
- Static HTML testing
- Dynamic webapp testing with server management
- Element discovery and interaction
- Screenshot capture
- Console log analysis
- Network idle waiting for dynamic content

**When to Use**:
- End-to-end testing of web applications
- UI behavior verification
- Visual regression testing
- Browser automation tasks
- Frontend integration testing

**Recommended For**:
- QA Tester (PRIMARY)
- Frontend Developer (SECONDARY)
- Software Developer (TERTIARY)

**Dependencies**:
- Playwright
- Python test frameworks

**Example Usage**:
```yaml
qa_tester:
  skills:
    - "skills/core/webapp-testing"
```

**Supporting Scripts**:
- `scripts/with_server.py` - Server lifecycle management

---

### mcp-builder

**Path**: `skills/core/mcp-builder` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~4,500 tokens

**Description**: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Covers both Python (FastMCP) and TypeScript (MCP SDK) implementations.

**Capabilities**:
- MCP server architecture planning
- Tool schema design
- API integration patterns
- Error handling best practices
- TypeScript/Python implementation guidance
- Testing and validation workflows

**Phases**:
1. Research and planning
2. Implementation
3. Review and testing
4. Evaluation with realistic scenarios

**When to Use**:
- Building MCP servers for external API integration
- Creating custom tools for LLM interactions
- Implementing service connectors
- Extending agent capabilities with new protocols

**Recommended For**:
- Backend Developer (PRIMARY)
- Software Developer (SECONDARY)
- Architect (TERTIARY)

**Dependencies**:
- TypeScript MCP SDK or Python FastMCP
- Target API documentation

**Example Usage**:
```yaml
backend_developer:
  skills:
    - "skills/core/mcp-builder"
```

---

### skill-creator

**Path**: `skills/core/skill-creator` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~5,000 tokens

**Description**: Comprehensive guide for creating effective skills. Provides a systematic approach to designing, implementing, and packaging custom skills for specialized tasks and workflows.

**Capabilities**:
- Skill design principles
- Progressive disclosure patterns
- Resource bundling strategies
- SKILL.md formatting guidelines
- Testing and iteration workflows
- Packaging and distribution

**Workflow**:
1. Understanding with concrete examples
2. Planning reusable contents
3. Initializing skill structure
4. Editing and refinement
5. Packaging for distribution
6. Iteration based on usage

**When to Use**:
- Creating new custom skills
- Improving existing skills
- Understanding skill architecture
- Training team on skill development

**Recommended For**:
- Architect (PRIMARY)
- Software Developer (SECONDARY)
- Manager (for understanding skill capabilities)

**Dependencies**:
- Skill initialization scripts
- Packaging tools

**Example Usage**:
```yaml
architect:
  skills:
    - "skills/core/skill-creator"
```

**Supporting Scripts**:
- `scripts/init_skill.py` - Initialize skill structure
- `scripts/package_skill.py` - Package skills for distribution

---

## Communication Skills

Skills for creating internal communications and documentation.

### internal-comms

**Path**: `skills/communication/internal-comms` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~3,000 tokens

**Description**: Toolkit for composing various internal company communications using standardized formats. Supports multiple communication types with appropriate tone and structure.

**Capabilities**:
- 3P updates (progress/plans/problems)
- Company newsletters
- FAQ responses
- Status reports
- Leadership updates
- Project updates
- Incident reports

**Workflow**:
1. Identify communication type
2. Load relevant guideline file
3. Apply formatting and tone requirements

**When to Use**:
- Writing team status updates
- Creating project newsletters
- Responding to common questions
- Documenting incidents
- Leadership communications

**Recommended For**:
- Manager (PRIMARY)
- Architect (for technical communications)

**Dependencies**: None

**Example Usage**:
```yaml
team_manager:
  skills:
    - "skills/communication/internal-comms"
```

**Supporting Files**:
- `examples/3p-updates.md` - 3P format guide
- `examples/company-newsletter.md` - Newsletter template
- `examples/faq-answers.md` - FAQ response guide
- `examples/general-comms.md` - General communication patterns

---

## Design & Creative Skills

Skills for visual design, styling, and creative content generation.

### theme-factory

**Path**: `skills/design/theme-factory` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~2,500 tokens

**Description**: Toolkit for styling artifacts with professional themes. Provides 10 pre-set themes with curated colors and fonts, plus custom theme generation capabilities.

**Capabilities**:
- 10 pre-set professional themes
- Custom theme generation
- Consistent color palette application
- Typography pairing
- Visual identity guidelines

**Pre-set Themes**:
- Ocean Depths
- Midnight Galaxy
- (8 additional professional themes)

**Workflow**:
1. Display theme showcase
2. Obtain user selection
3. Apply theme specifications

**When to Use**:
- Styling presentations
- Applying consistent design to artifacts
- Creating branded deliverables
- Generating professional-looking documents
- Web page theming

**Recommended For**:
- Frontend Developer (PRIMARY)
- Software Developer (for UI work)

**Dependencies**: None

**Example Usage**:
```yaml
frontend_developer:
  skills:
    - "skills/design/theme-factory"
```

---

### algorithmic-art

**Path**: `skills/design/algorithmic-art` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~3,000 tokens

**Description**: Generative art creation using p5.js with seeded randomness and particle systems. For creative visualization and artistic applications.

**Capabilities**:
- p5.js-based art generation
- Seeded randomness for reproducibility
- Particle system simulations
- Generative algorithms

**When to Use**:
- Creating data visualizations
- Generating artistic content
- Building interactive graphics
- Prototyping visual effects

**Recommended For**:
- Frontend Developer (for visualization needs)
- Software Developer (for creative projects)

**Dependencies**:
- p5.js library

**Example Usage**:
```yaml
frontend_developer:
  skills:
    - "skills/design/algorithmic-art"
```

---

### canvas-design

**Path**: `skills/design/canvas-design` (via Anthropic skills)
**License**: Apache 2.0
**Token Estimate**: ~2,000 tokens

**Description**: Visual art generation in PNG and PDF formats. For creating graphics and visual assets.

**When to Use**:
- Creating graphics assets
- Generating visual content
- Producing deliverable images

**Recommended For**:
- Frontend Developer (SECONDARY)

---

## Document Skills

Skills for manipulating and creating various document formats.

### docx

**Path**: `skills/documents/docx` (via Anthropic skills)
**License**: Source-available (see LICENSE.txt)
**Token Estimate**: ~3,500 tokens

**Description**: Word document creation and editing with change tracking capabilities. Enables agents to work with Microsoft Word documents programmatically.

**Capabilities**:
- Document creation
- Document editing
- Change tracking
- Formatting application
- Template usage

**When to Use**:
- Creating Word documents
- Editing existing .docx files
- Generating reports
- Documentation authoring
- Contract preparation

**Recommended For**:
- Manager (for documentation)
- QA Tester (for test reports)
- Architect (for technical docs)

**Dependencies**:
- python-docx library

**Example Usage**:
```yaml
team_manager:
  skills:
    - "skills/documents/docx"
```

---

### pdf

**Path**: `skills/documents/pdf` (via Anthropic skills)
**License**: Source-available (see LICENSE.txt)
**Token Estimate**: ~3,000 tokens

**Description**: PDF manipulation including extraction, creation, and merging. For working with PDF documents.

**Capabilities**:
- Text extraction
- PDF creation
- PDF merging
- Page manipulation
- Metadata handling

**When to Use**:
- Extracting content from PDFs
- Creating PDF documents
- Merging multiple PDFs
- Converting to PDF format

**Recommended For**:
- Manager (for deliverables)
- QA Tester (for test reports)

**Dependencies**:
- PyPDF2 or similar PDF libraries

**Example Usage**:
```yaml
team_manager:
  skills:
    - "skills/documents/pdf"
```

---

### xlsx

**Path**: `skills/documents/xlsx` (via Anthropic skills)
**License**: Source-available (see LICENSE.txt)
**Token Estimate**: ~4,000 tokens

**Description**: Excel spreadsheet creation and editing. For working with structured data in spreadsheet format.

**Capabilities**:
- Spreadsheet creation
- Data manipulation
- Formula application
- Chart creation
- Formatting

**When to Use**:
- Creating data reports
- Analyzing structured data
- Building data templates
- Generating metrics dashboards

**Recommended For**:
- Manager (for metrics and reporting)
- QA Tester (for test data)
- Backend Developer (for data exports)

**Dependencies**:
- openpyxl or xlsxwriter libraries

**Example Usage**:
```yaml
team_manager:
  skills:
    - "skills/documents/xlsx"
```

---

### pptx

**Path**: `skills/documents/pptx` (via Anthropic skills)
**License**: Source-available (see LICENSE.txt)
**Token Estimate**: ~3,500 tokens

**Description**: PowerPoint presentation creation and editing. For creating professional presentations.

**Capabilities**:
- Presentation creation
- Slide manipulation
- Template application
- Chart and diagram insertion
- Formatting

**When to Use**:
- Creating presentations
- Generating slide decks
- Building status reports
- Creating project overviews

**Recommended For**:
- Manager (PRIMARY)
- Architect (for technical presentations)

**Dependencies**:
- python-pptx library

**Example Usage**:
```yaml
team_manager:
  skills:
    - "skills/documents/pptx"
```

---

## Custom Skills

Project-specific skills created for your organization.

### appflowy-integration

**Path**: `skills/custom/appflowy-integration`
**License**: Apache 2.0
**Token Estimate**: ~3,800 tokens

**Description**: Integration with AppFlowy project management tool for task tracking, database management, and workspace organization. Enables agents to create tasks, update project status, and sync work with AppFlowy's REST API.

**Capabilities**:
- Create and update tasks in AppFlowy databases
- Manage workspaces and folders
- Track project progress automatically
- Generate project dashboards
- Sync agent work with AppFlowy
- Support for self-hosted deployments (Synology NAS, Docker)

**When to Use**:
- Tracking agent tasks in project management system
- Managing project workspaces and databases
- Organizing work items in Kanban boards
- Automating project status updates
- Generating project reports and dashboards

**Recommended For**:
- All agents (for task tracking)
- Project Manager (PRIMARY)
- Software Developer (SECONDARY)

**Dependencies**:
- Python 3.7+
- `requests` library
- AppFlowy instance (self-hosted or cloud)
- JWT authentication token

**Example Usage**:
```yaml
software_developer:
  skills:
    - "skills/custom/appflowy-integration"
  project_context:
    - ".ai-agents/context/appflowy-config.md"
```

**Scripts Included**:
- `appflowy_client.py`: Python API client
- `task_tracker.py`: CLI task tracker

**Deployment Options**:
- Docker deployment
- Synology NAS (DS 923+)
- AI home server
- See `references/setup_guide.md` for details

---

### template

**Path**: `skills/custom/template`
**License**: Your project license
**Token Estimate**: Varies

**Description**: Template for creating new custom skills. Provides structure and examples for developing project-specific skills.

**When to Use**:
- Starting a new custom skill
- Learning skill structure
- Understanding skill components

**See Also**: [INTEGRATION.md](INTEGRATION.md#creating-custom-skills) for detailed guide on creating custom skills.

---

## Agent Skill Matrix

Recommended skill assignments by agent type, with priority levels.

### Legend

- **PRIMARY**: Skill is central to agent's core function
- **SECONDARY**: Skill enhances agent capabilities
- **TERTIARY**: Skill useful in specific scenarios
- **OPTIONAL**: Skill can be added based on project needs

### Software Developer

**Core Skills**:
- None specific (general-purpose agent)

**Optional Skills** (based on assignment):
- `artifacts-builder` (SECONDARY) - when doing frontend work
- `webapp-testing` (TERTIARY) - when testing responsibilities overlap
- `mcp-builder` (SECONDARY) - when building integrations

**Token Budget**: 3,000-8,000 (base + 1-2 optional skills)

```yaml
software_developer:
  base: "base/software-developer.md"
  skills:  # Add based on specific assignment
    - "skills/core/artifacts-builder"  # If frontend-focused
```

---

### Manager

**Core Skills**:
- `internal-comms` (PRIMARY) - team communications
- `docx` (SECONDARY) - documentation
- `xlsx` (SECONDARY) - metrics and reporting
- `pptx` (SECONDARY) - presentations

**Optional Skills**:
- `pdf` (TERTIARY) - deliverable creation
- `skill-creator` (OPTIONAL) - understanding skill capabilities

**Token Budget**: 8,000-12,000 (base + 2-4 core skills)

```yaml
team_manager:
  base: "base/manager.md"
  skills:
    - "skills/communication/internal-comms"
    - "skills/documents/xlsx"
    - "skills/documents/docx"
```

---

### QA Tester

**Core Skills**:
- `webapp-testing` (PRIMARY) - end-to-end testing

**Optional Skills**:
- `docx` (SECONDARY) - test reports
- `xlsx` (SECONDARY) - test data
- `pdf` (TERTIARY) - test deliverables

**Token Budget**: 6,000-10,000 (base + 1-3 skills)

```yaml
qa_tester:
  base: "base/qa-tester.md"
  skills:
    - "skills/core/webapp-testing"
    - "skills/documents/docx"
```

---

### Architect

**Core Skills**:
- `skill-creator` (PRIMARY) - designing team capabilities
- `mcp-builder` (SECONDARY) - integration architecture

**Optional Skills**:
- `docx` (SECONDARY) - technical documentation
- `pptx` (SECONDARY) - architecture presentations
- `internal-comms` (TERTIARY) - technical communications

**Token Budget**: 7,000-12,000 (base + 2-4 skills)

```yaml
architect:
  base: "base/architect.md"
  skills:
    - "skills/core/skill-creator"
    - "skills/core/mcp-builder"
    - "skills/documents/docx"
```

---

### Frontend Developer (Web)

**Core Skills**:
- `artifacts-builder` (PRIMARY) - React component development
- `theme-factory` (PRIMARY) - UI styling
- `webapp-testing` (SECONDARY) - component testing

**Optional Skills**:
- `algorithmic-art` (OPTIONAL) - visualizations
- `canvas-design` (OPTIONAL) - graphics

**Token Budget**: 9,000-15,000 (base + platform + 2-3 core skills)

```yaml
frontend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "skills/core/artifacts-builder"
    - "skills/design/theme-factory"
    - "skills/core/webapp-testing"
```

---

### Backend Developer (Web)

**Core Skills**:
- `mcp-builder` (PRIMARY) - API and service integrations

**Optional Skills**:
- `webapp-testing` (SECONDARY) - API testing
- `xlsx` (TERTIARY) - data exports

**Token Budget**: 7,000-11,000 (base + platform + 1-2 core skills)

```yaml
backend_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/backend-developer.md"
  skills:
    - "skills/core/mcp-builder"
```

---

### Mobile Developer

**Core Skills**:
- `theme-factory` (PRIMARY) - UI styling
- `webapp-testing` (SECONDARY) - if React Native web views

**Optional Skills**:
- `artifacts-builder` (OPTIONAL) - if building web components
- `canvas-design` (OPTIONAL) - asset creation

**Token Budget**: 8,000-13,000 (base + platform + 1-2 core skills)

```yaml
mobile_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/mobile/mobile-developer.md"
  skills:
    - "skills/design/theme-factory"
```

---

## Skill Combinations

Recommended skill combinations for common scenarios.

### Full-Stack Web Development Team

```yaml
agents:
  team_manager:
    skills:
      - "skills/communication/internal-comms"
      - "skills/documents/xlsx"

  frontend_developer:
    skills:
      - "skills/core/artifacts-builder"
      - "skills/design/theme-factory"

  backend_developer:
    skills:
      - "skills/core/mcp-builder"

  qa_tester:
    skills:
      - "skills/core/webapp-testing"
```

**Total Team Token Budget**: ~25,000-35,000 tokens

---

### Enterprise Documentation Team

```yaml
agents:
  team_manager:
    skills:
      - "skills/communication/internal-comms"
      - "skills/documents/docx"
      - "skills/documents/pptx"
      - "skills/documents/pdf"

  architect:
    skills:
      - "skills/documents/docx"
      - "skills/core/skill-creator"
```

**Total Team Token Budget**: ~20,000-28,000 tokens

---

### Integration & API Development Team

```yaml
agents:
  team_manager:
    skills:
      - "skills/communication/internal-comms"

  architect:
    skills:
      - "skills/core/mcp-builder"
      - "skills/core/skill-creator"

  backend_developer:
    skills:
      - "skills/core/mcp-builder"

  qa_tester:
    skills:
      - "skills/core/webapp-testing"
```

**Total Team Token Budget**: ~28,000-38,000 tokens

---

## Usage Guidelines

### Choosing Skills for Agents

1. **Start with core skills** for the agent's primary function
2. **Add optional skills** based on project requirements
3. **Monitor token budget** - aim for 6,000-12,000 per agent
4. **Test incrementally** - add one skill at a time
5. **Remove unused skills** - if skill isn't used in 5+ sessions

### Token Budget Management

| Team Size | Skills per Agent | Total Budget Estimate |
|-----------|------------------|----------------------|
| 1-2 agents | 2-4 skills | 15,000-25,000 tokens |
| 3-4 agents | 2-3 skills | 25,000-40,000 tokens |
| 5+ agents | 1-2 skills | 30,000-50,000 tokens |

### Skill Loading Strategy

**Phase 1** (Current):
- Eager loading - all skills loaded at composition
- Simple, predictable behavior
- Best for small skill sets (1-3 per agent)

**Phase 2** (Future):
- Lazy loading - skills loaded on-demand
- Better token efficiency
- Best for large skill sets (4+ per agent)

---

## Adding New Skills

### From Anthropic Repository

1. Identify desired skill in [Anthropic Skills Repo](https://github.com/anthropics/skills)
2. Add git submodule reference (recommended)
3. Update this catalog with skill details
4. Test with target agents
5. Document usage patterns

### Custom Skills

1. Use template in `skills/custom/template`
2. Follow [INTEGRATION.md](INTEGRATION.md#creating-custom-skills) guide
3. Test with target agents
4. Add to this catalog
5. Share with team

---

## Maintenance

### Updating This Catalog

When adding new skills:
1. Add entry in appropriate category section
2. Update Agent Skill Matrix
3. Add to Skill Combinations if relevant
4. Update token estimates
5. Test all example configurations

### Versioning

This catalog follows semantic versioning:
- **Major**: Breaking changes to skill structure
- **Minor**: New skills added
- **Patch**: Documentation improvements, corrections

---

## References

- [README.md](README.md) - Skills overview
- [INTEGRATION.md](INTEGRATION.md) - Technical integration guide
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills)

---

## Support

For questions about:
- **Skill usage**: See individual skill documentation
- **Skill assignment**: Review Agent Skill Matrix above
- **Custom skills**: Consult [INTEGRATION.md](INTEGRATION.md)
- **Token budgets**: See Usage Guidelines section

---

**Last Updated**: 2025-11-20
**Catalog Version**: 1.0.0
**Total Skills**: 14 (from Anthropic) + custom template
