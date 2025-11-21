# Skills Showcase

This example demonstrates different skill configurations and their impacts on agent capabilities, token budgets, and use cases.

## Purpose

The skills-showcase provides:

1. **Progressive Examples**: From minimal (no skills) to maximum (many skills)
2. **Token Budget Analysis**: Understanding the cost of each skill addition
3. **Use Case Guidance**: When to use which skill combinations
4. **Best Practices**: Recommendations for production configurations

## Agent Configurations

### 1. Minimal Developer (Baseline)

**Configuration**: Base prompt only, no skills
**Token Budget**: ~3,000 tokens
**Use Case**: General-purpose development without specialization

```yaml
minimal_developer:
  base: "base/software-developer.md"
  # No skills
```

**Capabilities**:
- General software development knowledge
- Code writing and debugging
- Basic problem-solving

**When to Use**:
- Quick prototyping
- Simple scripting tasks
- When token budget is extremely limited
- Learning the base capabilities before adding skills

**Limitations**:
- No specialized frameworks or tools
- No testing automation
- No document generation
- No design capabilities

---

### 2. Testing Specialist (Single Skill)

**Configuration**: QA base + webapp-testing skill
**Token Budget**: ~7,000 tokens (+4,000 from skill)
**Use Case**: Focused testing role with automation

```yaml
testing_specialist:
  base: "base/qa-tester.md"
  skills:
    - "core/webapp-testing"
```

**Capabilities**:
- Everything from base QA tester
- Playwright-based browser automation
- Screenshot capture and comparison
- Console log analysis
- Element discovery and interaction

**When to Use**:
- Dedicated testing role
- E2E test automation
- UI behavior verification
- Regression testing

**Skill Impact**:
- +4,000 tokens (+133% increase)
- Adds comprehensive testing framework knowledge
- Enables automation that wasn't possible before

---

### 3. Frontend Specialist (Standard Configuration)

**Configuration**: Developer base + frontend platform + 3 skills
**Token Budget**: ~13,000 tokens
**Use Case**: Production frontend development

```yaml
frontend_specialist:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "core/web-artifacts-builder"  # React + Tailwind
    - "design/theme-factory"        # Professional styling
    - "core/webapp-testing"         # Component testing
```

**Capabilities**:
- React component development with Tailwind CSS
- Professional theme application
- Component and E2E testing
- Modern frontend best practices

**When to Use**:
- Production frontend development
- Building React applications
- Creating styled, tested components
- Professional web development

**Token Breakdown**:
- Base: 3,000 tokens
- Platform: 3,000 tokens
- web-artifacts-builder: 3,500 tokens
- theme-factory: 2,500 tokens
- webapp-testing: 4,000 tokens
- **Total**: ~13,000 tokens

**Recommended**: This is a well-balanced production configuration.

---

### 4. Full-Stack Developer (Advanced)

**Configuration**: Developer base + 2 platforms + 3 cross-domain skills
**Token Budget**: ~16,000 tokens
**Use Case**: End-to-end feature development

```yaml
fullstack_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
    - "platforms/web/backend-developer.md"
  skills:
    - "core/web-artifacts-builder"  # Frontend
    - "core/mcp-builder"            # Backend
    - "core/webapp-testing"         # Full-stack testing
```

**Capabilities**:
- Complete full-stack development
- Frontend React components
- Backend MCP server creation
- API integration
- End-to-end testing

**When to Use**:
- Small teams where developers own full features
- Microservices development
- API-first development
- When you need backend and frontend expertise

**Trade-offs**:
- Higher token budget (16,000)
- Broader but potentially less deep expertise in each area
- Best for T-shaped developers

---

### 5. QA Engineer (Specialized Testing + Reporting)

**Configuration**: QA base + 4 document skills
**Token Budget**: ~14,000 tokens
**Use Case**: Comprehensive QA with professional reporting

```yaml
qa_engineer:
  base: "base/qa-tester.md"
  skills:
    - "core/webapp-testing"  # Automation
    - "documents/xlsx"       # Test tracking
    - "documents/pdf"        # Reports
    - "documents/docx"       # Documentation
```

**Capabilities**:
- Automated testing with Playwright
- Test data management in spreadsheets
- Professional PDF test reports
- Detailed test documentation

**When to Use**:
- Enterprise QA processes
- Regulatory compliance testing
- Client deliverables requiring formal reports
- Large-scale test management

**Skill Synergy**:
- webapp-testing generates results
- xlsx tracks results across test runs
- pdf creates executive summaries
- docx provides detailed test documentation

---

### 6. Engineering Manager (Leadership)

**Configuration**: Manager base + communication + documentation
**Token Budget**: ~14,000 tokens
**Use Case**: Team leadership and coordination

```yaml
engineering_manager:
  base: "base/manager.md"
  skills:
    - "communication/internal-comms"  # Status updates
    - "documents/pptx"                # Presentations
    - "documents/xlsx"                # Metrics
    - "core/skill-creator"            # Team capabilities
```

**Capabilities**:
- Standardized team communications (3P updates)
- Professional stakeholder presentations
- Metrics tracking and reporting
- Understanding and composing team capabilities

**When to Use**:
- Team management role
- Project coordination
- Stakeholder communication
- Performance tracking

**Manager-Specific Value**:
- internal-comms ensures consistent team communication
- pptx for stakeholder alignment
- xlsx for data-driven decision making
- skill-creator for understanding team technical capabilities

---

### 7. System Architect (Strategic)

**Configuration**: Architect base + 2 platforms + 4 skills
**Token Budget**: ~17,000 tokens
**Use Case**: System design and technical leadership

```yaml
system_architect:
  base: "base/architect.md"
  platforms:
    - "platforms/web/frontend-developer.md"
    - "platforms/web/backend-developer.md"
  skills:
    - "core/skill-creator"            # Creating patterns
    - "core/mcp-builder"              # Integration design
    - "documents/pptx"                # Architecture docs
    - "communication/internal-comms"  # Technical writing
```

**Capabilities**:
- Full-stack architectural understanding
- Custom skill and pattern creation
- Integration architecture design
- Professional architecture presentations
- Technical documentation and ADRs

**When to Use**:
- System architecture role
- Creating team development patterns
- Integration strategy
- Technical leadership

**Strategic Value**:
- skill-creator enables defining team's development patterns
- Understanding of both frontend and backend for holistic design
- Communication skills for architectural decision records

---

### 8. UI/UX Developer (Creative)

**Configuration**: Developer base + frontend platform + design skills
**Token Budget**: ~14,000 tokens
**Use Case**: UI/UX development with visual design

```yaml
ui_ux_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
  skills:
    - "core/web-artifacts-builder"
    - "design/theme-factory"
    - "design/algorithmic-art"
    - "design/canvas-design"
```

**Capabilities**:
- React component development
- Professional theme application
- Generative art and visualizations
- Visual asset creation

**When to Use**:
- UI/UX-focused development
- Data visualization projects
- Creative web applications
- Design system implementation

**Design Focus**:
- Multiple design skills create strong creative capabilities
- Still grounded in engineering with web-artifacts-builder
- Good balance for design-engineer hybrid role

---

### 9. Technical Writer (Documentation)

**Configuration**: Developer base + 4 document skills
**Token Budget**: ~13,000 tokens
**Use Case**: Technical documentation and training

```yaml
technical_writer:
  base: "base/software-developer.md"
  skills:
    - "documents/docx"
    - "documents/pdf"
    - "documents/pptx"
    - "communication/internal-comms"
```

**Capabilities**:
- Technical documentation writing
- Published documentation (PDF)
- Training materials (PPTX)
- Communication guidelines
- Technical understanding for accurate docs

**When to Use**:
- Dedicated documentation role
- API documentation
- User guides and tutorials
- Training material creation

**Documentation Excellence**:
- Full suite of document creation tools
- Technical base ensures accuracy
- Communication skills ensure clarity

---

### 10. Polyglot Developer (Maximum Skills - Testing Only)

**Configuration**: Developer base + 2 platforms + 6 skills
**Token Budget**: ~20,000 tokens
**Use Case**: TESTING ONLY - Not recommended for production

```yaml
polyglot_developer:
  base: "base/software-developer.md"
  platforms:
    - "platforms/web/frontend-developer.md"
    - "platforms/web/backend-developer.md"
  skills:
    - "core/web-artifacts-builder"
    - "core/mcp-builder"
    - "core/webapp-testing"
    - "design/theme-factory"
    - "documents/xlsx"
    - "communication/internal-comms"
```

**Capabilities**:
- Everything from full-stack developer
- Plus design, documentation, and communication

**WARNING**: Not recommended for production because:
- Very high token budget (20,000)
- Too many capabilities may dilute focus
- Likely to have unused skills
- Better to use specialized agents

**When to Test**:
- Understanding upper limits
- Token budget analysis
- Skill interaction testing

---

## Token Budget Comparison

| Agent Configuration    | Token Budget | Increase vs Minimal | Skills Count |
|------------------------|--------------|---------------------|--------------|
| Minimal Developer      | ~3,000       | Baseline            | 0            |
| Testing Specialist     | ~7,000       | +133%               | 1            |
| Frontend Specialist    | ~13,000      | +333%               | 3            |
| Full-Stack Developer   | ~16,000      | +433%               | 3            |
| QA Engineer            | ~14,000      | +367%               | 4            |
| Engineering Manager    | ~14,000      | +367%               | 4            |
| System Architect       | ~17,000      | +467%               | 4            |
| UI/UX Developer        | ~14,000      | +367%               | 4            |
| Technical Writer       | ~13,000      | +333%               | 4            |
| Polyglot Developer     | ~20,000      | +567%               | 6            |

## Recommendations by Team Size

### Solo Developer (1 person)
**Recommended**: Full-Stack Developer (~16,000 tokens)
- Covers both frontend and backend
- Testing capabilities
- Balanced for solo work

### Small Team (2-3 people)
**Recommended**:
- Frontend Specialist (~13,000 tokens)
- Backend Developer + mcp-builder (~12,000 tokens)
- **Total**: ~25,000 tokens

### Standard Team (4-5 people)
**Recommended**:
- Engineering Manager (~14,000 tokens)
- Frontend Specialist (~13,000 tokens)
- Backend Developer (~12,000 tokens)
- QA Engineer (~14,000 tokens)
- **Total**: ~53,000 tokens

### Large Team (6+ people)
**Recommended**:
- System Architect (~17,000 tokens)
- Engineering Manager (~14,000 tokens)
- 2x Frontend Specialist (~26,000 tokens)
- 2x Backend Developer (~24,000 tokens)
- QA Engineer (~14,000 tokens)
- **Total**: ~95,000 tokens

## How to Choose Skills

### Step 1: Identify Primary Function
What is the agent's main role?
- Development → web-artifacts-builder or mcp-builder
- Testing → webapp-testing
- Management → internal-comms
- Architecture → skill-creator

### Step 2: Add Secondary Capabilities
What tasks will the agent do frequently?
- Needs reports? → Add xlsx or pdf
- Needs presentations? → Add pptx
- Needs styling? → Add theme-factory

### Step 3: Consider Team Overlap
- Avoid giving all agents the same skills
- Specialize agents for efficiency
- One agent with internal-comms is usually enough

### Step 4: Test and Measure
- Start with 2-3 skills
- Monitor which skills get used
- Remove skills unused after 5+ sessions
- Add skills when gaps are identified

## Usage Examples

### Compose a Frontend Specialist

```bash
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent frontend_specialist \
  --output /tmp/frontend-specialist.md
```

### Compare Minimal vs Skilled

```bash
# Compose both
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent minimal_developer \
  --output /tmp/minimal.md

python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent frontend_specialist \
  --output /tmp/frontend.md

# Compare sizes
echo "Minimal: $(wc -w < /tmp/minimal.md) words"
echo "Frontend Specialist: $(wc -w < /tmp/frontend.md) words"
echo "Skills add: $(($(wc -w < /tmp/frontend.md) - $(wc -w < /tmp/minimal.md))) words"
```

### Test All Configurations

```bash
# Compose all agents to see token budgets
for agent in minimal_developer testing_specialist frontend_specialist \
             fullstack_developer qa_engineer engineering_manager \
             system_architect ui_ux_developer technical_writer \
             polyglot_developer; do
  echo "Composing $agent..."
  python scripts/compose-agent.py \
    --config examples/skills-showcase/config.yml \
    --agent $agent \
    --output /tmp/showcase-$agent.md
done
```

## Best Practices

### 1. Start Minimal, Add Incrementally
- Begin with base prompt only
- Add one skill at a time
- Test each addition
- Measure impact on capabilities and token usage

### 2. Aim for 2-4 Skills per Agent
- Sweet spot for most production use cases
- Provides specialization without bloat
- Typically 10,000-15,000 tokens total

### 3. Remove Unused Skills
- Track skill usage in production
- If skill unused after 5+ sessions, remove it
- Re-evaluate quarterly

### 4. Consider Team Composition
- Don't duplicate skills across all agents
- Specialize agents for their roles
- Use skill synergies (e.g., testing + reporting)

### 5. Monitor Token Usage
- Set alerts at 80% context window
- Use checkpointing for long conversations
- Consider skill-on-demand for future optimization

## Common Patterns

### Developer Team Pattern
```yaml
frontend:
  skills: [web-artifacts-builder, theme-factory, webapp-testing]

backend:
  skills: [mcp-builder, webapp-testing, xlsx]

qa:
  skills: [webapp-testing, xlsx, pdf]
```

### Documentation Team Pattern
```yaml
tech_writer:
  skills: [docx, pdf, pptx, internal-comms]

developer:
  skills: [web-artifacts-builder]  # Keep docs separate from dev
```

### Management Pattern
```yaml
manager:
  skills: [internal-comms, pptx, xlsx, skill-creator]

architect:
  skills: [skill-creator, mcp-builder, pptx]
```

## Further Reading

- [COMPARISON.md](COMPARISON.md) - Detailed side-by-side comparisons
- [TESTING.md](TESTING.md) - How to test these configurations
- [Skills Catalog](../../skills/CATALOG.md) - Complete skills reference
- [Integration Guide](../../skills/INTEGRATION.md) - Technical details

---

**Last Updated**: 2025-11-20
**Purpose**: Skills configuration examples and guidance
**Total Configurations**: 10 (minimal → maximum)
