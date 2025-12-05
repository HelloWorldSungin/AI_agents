# Scripts & Tools

Automation scripts, starter templates, and development tools.

---

## Core Scripts

Essential scripts for agent composition and project setup.

| Script | Purpose | Location |
|--------|---------|----------|
| `compose-agent.py` | Compose agents from components (base + platform + context + skills) | `scripts/compose-agent.py` |
| `generate-template.py` | Generate starter templates for existing projects | `starter-templates/generate-template.py` |
| `setup-commands.py` | Install tool selector wrappers to other projects | `scripts/setup-commands.py` |
| `security_validator.py` | Security validation for autonomous execution | `scripts/security_validator.py` |

### compose-agent.py

**Purpose:** Compose complete agent prompts from modular components

**Usage:**
```bash
# Compose all agents from config
python scripts/compose-agent.py --config ../config.yml --all

# Compose specific agent
python scripts/compose-agent.py --config ../config.yml --agent backend_dev
```

**What it Does:**
- Reads config.yml
- Combines base agent + platform + skills + context
- Generates complete agent prompts
- Outputs to `.ai-agents/composed/`

**Example Output:**
```
.ai-agents/composed/
├── backend_developer.md      # Base + web/backend + mcp-builder skill
├── frontend_developer.md     # Base + web/frontend + web-artifacts skill
└── manager.md                # Manager base + create-plans skill
```

### generate-template.py

**Purpose:** Generate starter templates for existing projects

**Usage:**
```bash
# Interactive mode (recommended)
cd your-project
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive

# Direct mode
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

**What it Creates:**
- Complete `.ai-agents/` directory structure
- Pre-configured context files (architecture, API contracts, coding standards)
- Ready-to-use agent configurations
- Example config.yml

**See:** [Starter Templates](#starter-templates) section below

### setup-commands.py

**Purpose:** Install tool selector wrappers for cross-project tool access

**Usage:**
```bash
# List available tools
python scripts/setup-commands.py --list

# Install to current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py

# Install globally (all projects)
python /path/to/AI_agents/scripts/setup-commands.py --global
```

**What it Installs:**
- 30 wrapper commands (~200-300 bytes each)
- `/ai-tools` discovery command
- All `/consider:*` thinking models

**See:** [Tool Selector](#tool-selector-new-v130) section below

### security_validator.py

**Purpose:** Security validation for autonomous execution mode

**New in:** Autonomous agent integration (v1.2.0)

**Usage:**
```python
from scripts.security_validator import SecurityValidator

validator = SecurityValidator("schemas/security-policy.json")
result = validator.validate_command("rm -rf /tmp/cache")

if result.allowed:
    # Execute command
    pass
else:
    print(f"Blocked: {result.reason}")
```

**Features:**
- Three-layer defense-in-depth
- Command allowlist checking
- Destructive pattern detection
- Filesystem scope restrictions

**Security Layers:**
1. **Allowlist:** Only approved commands execute
2. **Destructive Patterns:** Block `rm -rf /`, `DROP TABLE`, etc.
3. **Filesystem Scope:** Restrict to project directory

**Config:** `schemas/security-policy.json`

**See:** `docs/guides/SECURITY.md` for complete guide

---

## Orchestration Scripts

Based on [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

**Location:** `scripts/orchestration/`

| Script | Purpose | Token Savings | Best For |
|--------|---------|---------------|----------|
| `simple_orchestrator.py` | Basic multi-agent orchestration via API | N/A | Learning, simple workflows |
| `prompt_cache.py` | Prompt caching for cost reduction | API cost savings | Repeated operations |
| `sandbox_executor.py` | Secure code execution sandbox | 37% per workflow | Multi-step workflows |
| `programmatic_orchestrator.py` | Programmatic tool calling | 37% reduction | Advanced automation |
| `file_based_orchestrator.py` | File-based agent coordination | N/A | Human-coordinated workflows |
| `custom_orchestrator_example.py` | Custom orchestration patterns | N/A | Custom use cases |

### Run Demos

```bash
# Test sandbox executor
python3 scripts/orchestration/sandbox_executor.py

# Run simple orchestrator
python3 scripts/orchestration/simple_orchestrator.py

# Test prompt caching
python3 scripts/orchestration/prompt_cache.py
```

### Key Patterns

**1. Prompt Caching** - Cache stable components for 5 minutes
**2. Sandbox Execution** - Execute code in isolated sandbox
**3. Programmatic Tools** - Generate code that calls tools (37% reduction)

**See:** [07-advanced.md](07-advanced.md) for detailed guide

---

## Tool Selector (NEW v1.3.0)

Enable `/command` style access to AI_agents tools from other projects.

### Installation

```bash
# List available tools
python scripts/setup-commands.py --list

# Install to current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py

# Install globally (all projects)
python /path/to/AI_agents/scripts/setup-commands.py --global
```

### What Gets Installed

**30 Wrapper Commands** (~200-300 bytes each):
- 12 thinking models (`/consider:*`)
- Workflow commands (`/debug`, `/create-plan`, `/whats-next`)
- Skill creation (`/create-agent-skill`)
- 1 discovery command (`/ai-tools`)

### Token Impact

**At-rest:** ~50 tokens (command names only)
**Per invocation:** +60 tokens (~1.5% overhead)

**Calculation:**
- 30 commands × 1.67 tokens per wrapper = 50 tokens at-rest
- Full skill load on invocation: 60 tokens overhead

### Usage in Target Project

```bash
# Discover available tools
/ai-tools

# Use thinking models
/consider:first-principles "Should we use microservices?"
/consider:pareto "Which features drive 80% of value?"

# Use workflow commands
/debug "Login fails after deployment"
/create-plan "Implement payment system"

# Create resources
/create-agent-skill "database migration skill"
/create-prompt "Analyze log files for errors"
```

### Benefits

1. **Access tools from any project** - No need to copy files
2. **Minimal footprint** - ~50 tokens at-rest
3. **Lazy loading** - Tools load on-demand
4. **Centralized updates** - Update AI_agents once, available everywhere
5. **Clean separation** - Project files stay minimal

### Removal

```bash
# Remove from current project
cd /path/to/your/project
python /path/to/AI_agents/scripts/setup-commands.py --remove

# Remove from all projects
python /path/to/AI_agents/scripts/setup-commands.py --remove --global
```

---

## Starter Templates

Quick-start templates for existing projects.

**New in:** v1.1.0
**Location:** `starter-templates/`

### Available Templates

| Template | Best For | Command | Location |
|----------|----------|---------|----------|
| `web-app` | Full-stack web apps (React/Vue + Node/Python) | `--type web-app` | `starter-templates/web-app/` |
| `mobile-app` | Mobile apps (React Native, Flutter, native) | `--type mobile-app` | `starter-templates/mobile-app/` |
| `full-stack` | Complete full-stack with multiple services | `--type full-stack` | `starter-templates/full-stack/` |
| `api-service` | Backend API service or microservice | `--type api-service` | `starter-templates/api-service/` |
| `data-pipeline` | Data processing or analytics project | `--type data-pipeline` | `starter-templates/data-pipeline/` |

### Interactive Mode (Recommended)

```bash
cd your-existing-project
python3 path/to/AI_agents/starter-templates/generate-template.py --interactive
```

**Prompts you through:**
1. Select template type
2. Enter project name
3. Choose output directory
4. Configure agents
5. Set context files

### Direct Mode

```bash
python3 path/to/AI_agents/starter-templates/generate-template.py \
  --type web-app \
  --name "YourProject" \
  --output .
```

### What You Get

```
your-project/
├── .ai-agents/
│   ├── config.yml                    # Agent configuration
│   ├── context/
│   │   ├── architecture.md           # System architecture
│   │   ├── api-contracts.md          # API documentation
│   │   ├── coding-standards.md       # Code style guide
│   │   └── tech-stack.md             # Technology choices
│   ├── state/
│   │   └── team-communication.json   # Initial state file
│   └── composed/                     # Generated agents (run compose-agent.py)
├── README.md                         # Updated with AI agent info
└── [your existing files]
```

### Template Details

#### web-app
**Best For:** React/Vue + Node/Python web applications

**Agents:**
- Manager
- Frontend Developer (React/Vue)
- Backend Developer (Node/Python)
- QA Tester

**Context Files:**
- Frontend architecture (components, routing, state)
- Backend architecture (API, database, auth)
- API contracts (endpoints, schemas)

#### mobile-app
**Best For:** React Native, Flutter, native iOS/Android

**Agents:**
- Manager
- Mobile Developer
- Backend Developer
- QA Tester

**Context Files:**
- Mobile architecture (navigation, state, native modules)
- Backend API contracts
- Platform-specific guidelines (iOS/Android)

#### full-stack
**Best For:** Multiple services, microservices, complex systems

**Agents:**
- Manager
- Frontend Developer
- Backend Developer × 2
- DevOps Engineer
- QA Tester

**Context Files:**
- Microservices architecture
- Service contracts
- Infrastructure setup
- Deployment pipeline

#### api-service
**Best For:** Backend API, microservice, REST/GraphQL service

**Agents:**
- Manager
- Backend Developer
- QA Tester

**Context Files:**
- API architecture
- Database schema
- Authentication/authorization
- Endpoint documentation

#### data-pipeline
**Best For:** ETL, data processing, analytics, ML pipelines

**Agents:**
- Manager
- Data Engineer
- Backend Developer
- QA Tester

**Context Files:**
- Pipeline architecture
- Data sources and schemas
- Processing logic
- Output formats

---

## Init Scripts Templates

Project-specific environment setup scripts generated by IT Specialist.

**New in:** Autonomous agent integration (v1.2.0)
**Location:** `templates/init-scripts/`

### Available Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `nodejs-react-init.sh` | Node.js + React projects | `templates/init-scripts/nodejs-react-init.sh` |
| `python-django-init.sh` | Python + Django projects | `templates/init-scripts/python-django-init.sh` |
| `fullstack-init.sh` | Full-stack multi-service projects | `templates/init-scripts/fullstack-init.sh` |
| `README.md` | Template documentation | `templates/init-scripts/README.md` |

### What Init Scripts Do

1. **Dependency Checks** - Verify required tools installed (node, python, docker, etc.)
2. **Installation** - Install project dependencies
3. **Configuration** - Set up environment variables
4. **Database Setup** - Create DB, run migrations
5. **Test Infrastructure** - Verify tests can run
6. **Build Verification** - Ensure project builds
7. **Documentation** - Display next steps

### When Generated

IT Specialist (Complex Mode, Phase 4) generates `init.sh` after validating infrastructure:
- Detects project type (Node, Python, etc.)
- Selects appropriate template
- Customizes for project specifics
- Outputs to project root

### Usage

```bash
# After IT Specialist generates init.sh
chmod +x init.sh
./init.sh

# Script will:
# ✓ Check dependencies
# ✓ Install packages
# ✓ Configure environment
# ✓ Set up database
# ✓ Run test suite
# ✓ Build project
```

**See:** `prompts/it-specialist-agent.md` (Phase 4: Environment Automation)

---

## Best Practices

### Script Usage

1. **Use compose-agent.py** - Always compose agents from config, don't edit manually
2. **Version control config.yml** - Track agent configurations
3. **Generate templates once** - Don't regenerate, modify config instead
4. **Test init scripts** - Run on clean environment before sharing

### Tool Selector

5. **Install selectively** - Only install in projects that need it
6. **Update regularly** - Pull AI_agents updates for new tools
7. **Monitor token usage** - Track overhead if using many tools

### Security

8. **Review security-policy.json** - Adjust allowlist for your needs
9. **Test validator** - Verify blocked commands before autonomous execution
10. **Restrict scope** - Limit filesystem access to project directory

---

## See Also

- **Advanced Features:** [07-advanced.md](07-advanced.md)
- **Orchestration Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`
- **Starter Templates:** `starter-templates/README.md`
- **Security Guide:** `docs/guides/SECURITY.md`
- **IT Specialist:** [02-agents.md](02-agents.md#it-specialist)

---

[← Back to Index](index.md) | [Previous: Workflows](05-workflows.md) | [Next: Advanced Features →](07-advanced.md)
