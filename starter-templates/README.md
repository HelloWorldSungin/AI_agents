# AI Agents Library - Starter Templates

🚀 **Quick-start templates** for integrating AI Agents into your existing projects.

These templates provide pre-configured setups with context files, agent configurations, and best practices for different project types.

---

## 📦 Available Templates

| Template | Description | Best For |
|----------|-------------|----------|
| **web-app** | Full-stack web application | React + Node.js projects |
| **mobile-app** | Mobile application | React Native, Flutter, native apps |
| **full-stack** | Complex full-stack system | Multi-service applications |
| **api-service** | Backend API service | Microservices, REST APIs |
| **data-pipeline** | Data processing | ETL, analytics, data engineering |

---

## 🚀 Quick Start

### Option 1: Interactive Mode (Recommended)

```bash
cd starter-templates
python3 generate-template.py --interactive
```

Answer the prompts:
```
1. Select template type
2. Enter project name
3. Specify output directory
4. Confirm generation
```

### Option 2: Command Line

```bash
# Generate template for your project
python3 generate-template.py \
  --type web-app \
  --name "MyProject" \
  --output /path/to/your/project
```

### What Gets Generated

```
your-project/
└── .ai-agents/
    ├── context/                    # Project-specific context
    │   ├── architecture.md         # Tech stack, structure
    │   ├── api-contracts.md        # API specifications
    │   ├── coding-standards.md     # Team conventions
    │   └── current-features.md     # Features & roadmap
    ├── config.yml                  # Agent configuration
    ├── composed/                   # Generated agents (after compose)
    ├── state/                      # Agent state tracking
    ├── checkpoints/                # Conversation checkpoints
    ├── memory/                     # Project memory/RAG
    ├── workflows/                  # Custom workflows
    ├── .gitignore                  # Git ignore rules
    └── README.md                   # Setup instructions
```

---

## 📋 After Generation

### Step 1: Add AI Agents Library

If not already added:

```bash
cd your-project
git submodule add https://github.com/your-org/AI_agents.git .ai-agents/library
git submodule update --init --recursive
```

### Step 2: Customize Context Files

Edit the generated files in `.ai-agents/context/` to match your project:

```bash
vi .ai-agents/context/architecture.md      # Update tech stack
vi .ai-agents/context/api-contracts.md     # Add your API endpoints
vi .ai-agents/context/coding-standards.md  # Adjust coding rules
vi .ai-agents/context/current-features.md  # List your features
```

**💡 Tip**: The more accurate your context files, the better your agents will perform!

### Step 3: Configure Agents

Review and adjust `.ai-agents/config.yml`:

```yaml
agents:
  frontend_developer:
    skills:
      - "core/artifacts-builder"    # Keep or remove
      - "design/theme-factory"       # Add more if needed
```

**Token Budget**: Aim for 2-3 skills per agent (~6,000-9,000 tokens)

### Step 4: Compose Agents

```bash
cd .ai-agents/library
python3 scripts/compose-agent.py --config ../../config.yml --all
```

Output:
```
✓ Saved: frontend_developer.md (11,500 tokens)
✓ Saved: backend_developer.md (10,200 tokens)
✓ Saved: qa_tester.md (9,800 tokens)
✓ Saved: team_manager.md (11,000 tokens)
```

### Step 5: Use Your Agents

Copy the composed prompts:

```bash
# macOS
cat .ai-agents/composed/frontend_developer.md | pbcopy

# Linux
cat .ai-agents/composed/frontend_developer.md | xclip -selection clipboard

# Or just view
cat .ai-agents/composed/frontend_developer.md
```

Paste into Claude or your LLM API and start working!

---

## 📚 Template Details

### web-app Template

**Perfect for:**
- React + Node.js applications
- Vue + Express projects
- Full-stack JavaScript/TypeScript apps

**Includes:**
- Frontend developer with artifacts-builder + theme-factory
- Backend developer with mcp-builder
- QA tester with webapp-testing
- Team manager for coordination

**Context Files:**
- Architecture (tech stack, repo structure)
- API contracts (endpoints, auth, responses)
- Coding standards (TypeScript, React, testing)
- Current features (roadmap, status)

---

### mobile-app Template

**Perfect for:**
- React Native applications
- Flutter projects
- Native iOS/Android apps

**Includes:**
- Mobile developer with platform-specific skills
- QA tester for mobile testing
- UI designer with theme-factory

**Context Files:**
- Mobile architecture
- Platform-specific conventions
- App store requirements
- Feature roadmap

---

### full-stack Template

**Perfect for:**
- Multi-service architectures
- Microservices projects
- Complex distributed systems

**Includes:**
- Multiple specialized developers
- DevOps engineer
- System architect
- Full coordination setup

---

### api-service Template

**Perfect for:**
- REST API services
- GraphQL servers
- Microservices

**Includes:**
- Backend developer with API focus
- API documentation specialist
- Integration tester

---

### data-pipeline Template

**Perfect for:**
- ETL pipelines
- Data analytics projects
- ML/AI data processing

**Includes:**
- Data engineer
- Pipeline developer
- Quality assurance for data

---

## 🎯 Best Practices

### 1. Start Simple

Begin with minimal agent configuration:
- Start with 1-2 agents
- Add 1-2 essential skills per agent
- Expand based on actual needs

### 2. Keep Context Current

Update context files as your project evolves:
- Weekly: Update `current-features.md`
- Monthly: Review `architecture.md`
- As needed: Update `api-contracts.md`, `coding-standards.md`

After updates, recompose agents:
```bash
python3 .ai-agents/library/scripts/compose-agent.py --config .ai-agents/config.yml --all
```

### 3. Monitor Token Usage

Keep agents under 12,000 tokens:
- Check composition output for warnings
- Remove unused skills
- Split large context files
- Create specialized agents instead of generalists

### 4. Use Branch Isolation

Each agent works on their own branch:
```
feature/task-name/agent/role/subtask
```

Example:
```
feature/dark-mode/agent/frontend-dev/toggle-component
feature/dark-mode/agent/backend-dev/preferences-api
```

### 5. Version Control

Commit your `.ai-agents/` setup (except generated files):

```bash
# .ai-agents/.gitignore handles this automatically
git add .ai-agents/context/
git add .ai-agents/config.yml
git add .ai-agents/README.md
git commit -m "chore: configure AI agents for project"
```

---

## 🔧 Customization

### Adding Custom Skills

Create project-specific skills in `.ai-agents/library/skills/custom/`:

```bash
cd .ai-agents/library/skills/custom
cp -r template/ your-workflow-name/
vi your-workflow-name/SKILL.md
```

Reference in `config.yml`:
```yaml
skills:
  - "custom/your-workflow-name"
```

### Adding More Agents

Add to `.ai-agents/config.yml`:

```yaml
agents:
  devops_engineer:
    base: "base/software-developer.md"
    skills:
      - "core/skill-creator"
    project_context:
      - ".ai-agents/context/architecture.md"
```

### Modifying Existing Templates

Fork and customize:

```bash
cp -r starter-templates/web-app starter-templates/my-custom-template
# Customize files in my-custom-template/
```

Use your custom template:
```bash
python3 generate-template.py --type my-custom-template --name "MyProject"
```

---

## 📖 Examples

### Example 1: New React + Node.js Project

```bash
# 1. Generate template
cd AI_agents/starter-templates
python3 generate-template.py --type web-app --name "TaskFlow" --output ~/Projects/taskflow

# 2. Customize (edit files in ~/Projects/taskflow/.ai-agents/context/)

# 3. Compose
cd ~/Projects/taskflow/.ai-agents/library
python3 scripts/compose-agent.py --config ../../config.yml --all

# 4. Use agents!
cat ../../composed/frontend_developer.md | pbcopy
# Paste into Claude and start building
```

### Example 2: Existing Mobile App

```bash
# For an existing React Native app
cd existing-mobile-app
python3 ../AI_agents/starter-templates/generate-template.py \
  --type mobile-app \
  --name "MobileApp" \
  --output .

# Now you have .ai-agents/ configured for your existing project
```

---

## 🆘 Troubleshooting

### Template generation fails

**Error**: `Template not found`
- Check template name: `--type web-app` (not `webapp`)
- Ensure you're in `starter-templates/` directory

### Composition fails

**Error**: `PyYAML not installed`
```bash
pip3 install pyyaml
```

**Error**: `Config file not found`
- Ensure path is correct: `--config ../../config.yml`
- Use absolute path if needed

### Token budget exceeded

**Warning**: `Agent exceeds 12,000 tokens`

Solutions:
1. Remove 1-2 skills from agent configuration
2. Split large context files
3. Create more specialized agents

---

## 📚 Additional Resources

- [AI Agents Library Documentation](../README.md)
- [Skills Guide](../SKILLS_GUIDE.md)
- [Migration Guide](../MIGRATION_GUIDE.md)
- [Architecture Documentation](../ARCHITECTURE.md)

---

## 🤝 Contributing

Have a useful template to share?

1. Create your template directory in `starter-templates/`
2. Include context/, config.yml
3. Test with generate-template.py
4. Submit a PR!

**Template checklist:**
- [ ] Complete context files
- [ ] Tested config.yml
- [ ] README section above
- [ ] Example project tested

---

## 📝 Template Development

### Creating a New Template

```bash
mkdir starter-templates/my-template
mkdir starter-templates/my-template/context
```

Required files:
- `context/architecture.md`
- `context/api-contracts.md` (if applicable)
- `context/coding-standards.md`
- `context/current-features.md`
- `config.yml`

Use placeholders:
- `{{PROJECT_NAME}}` - will be replaced with actual project name

---

## 📄 License

Same as AI Agents Library - MIT License

---

**Questions?** Open an issue or check the main [AI Agents Library documentation](../README.md).

**Ready to start?** Run `python3 generate-template.py --interactive` now! 🚀
