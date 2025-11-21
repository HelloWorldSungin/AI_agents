# Web App Team Example

This example demonstrates how to configure a multi-agent team for a full-stack web application project.

## Team Composition

- **Team Manager**: Coordinates all agents, manages tasks, resolves conflicts
- **Frontend Developer**: React + TypeScript development
- **Backend Developer**: Node.js + Express API development
- **QA Tester**: Testing and quality assurance

## Skills Integration

This example demonstrates how Anthropic Skills enhance each agent's capabilities beyond their base prompts.

### Team Manager Skills

**Skills**: `communication/internal-comms`, `documents/pptx`, `core/skill-creator`
**Token Budget**: ~11,000 tokens (3,000 base + ~8,000 skills)

The manager uses skills to:
- Generate standardized team status updates (3P format: Progress/Plans/Problems)
- Create professional stakeholder presentations
- Understand and compose new team capabilities

**Example Usage**:
```
User: "Create a weekly status update for the engineering team"
Manager: Uses internal-comms skill to generate a formatted 3P update
```

### Frontend Developer Skills

**Skills**: `core/web-artifacts-builder`, `core/webapp-testing`, `design/theme-factory`
**Token Budget**: ~13,000 tokens (3,000 base + 3,000 platform + ~7,000 skills)

The frontend developer uses skills to:
- Build interactive React components with Tailwind CSS and shadcn/ui
- Test components and UI behavior with Playwright
- Apply professional themes and styling consistently

**Example Usage**:
```
User: "Create a responsive product card component"
Frontend Dev: Uses web-artifacts-builder to generate React component with Tailwind
              Uses theme-factory to apply Ocean Depths theme
              Uses webapp-testing to verify responsive behavior
```

### Backend Developer Skills

**Skills**: `core/mcp-builder`, `core/webapp-testing`, `documents/xlsx`
**Token Budget**: ~12,000 tokens (3,000 base + 3,000 platform + ~6,000 skills)

The backend developer uses skills to:
- Design and implement MCP servers for API integrations
- Test API endpoints and backend functionality
- Generate data exports and reports

**Example Usage**:
```
User: "Create an MCP server for the Stripe API"
Backend Dev: Uses mcp-builder skill to design and implement TypeScript MCP server
             Uses webapp-testing to verify API endpoints
```

### QA Tester Skills

**Skills**: `core/webapp-testing`, `documents/xlsx`, `documents/pdf`
**Token Budget**: ~11,000 tokens (3,000 base + ~8,000 skills)

The QA tester uses skills to:
- Perform end-to-end testing with Playwright
- Track test results in structured spreadsheets
- Generate professional test reports

**Example Usage**:
```
User: "Test the checkout flow"
QA Tester: Uses webapp-testing to automate E2E test
           Captures screenshots at each step
           Uses xlsx to log test results
           Uses pdf to generate test report
```

### Total Team Token Budget

**Without Skills**: ~12,000 tokens (4 agents x 3,000 base)
**With Skills**: ~47,000 tokens (base + platforms + skills)

This represents a ~4x increase in context usage, providing significantly enhanced capabilities.

## Project Setup

### 1. Install the AI Agents Library

```bash
# Clone the AI agents library
git clone git@github.com:org/AI_agents.git

# Or add as git submodule
git submodule add git@github.com:org/AI_agents.git .ai-agents/library
```

### 2. Create Project Structure

```bash
# In your project root
mkdir -p .ai-agents/{context,state,checkpoints,memory,workflows}

# Copy the example configuration
cp AI_agents/examples/web-app-team/config.yml .ai-agents/config.yml
```

### 3. Create Context Files

Create the following files in `.ai-agents/context/`:

**architecture.md**
```markdown
# System Architecture

## Overview
E-commerce platform with React frontend and Node.js backend.

## Architecture Diagram
[Add your architecture diagram]

## Key Components
- Frontend: React SPA
- Backend: RESTful API (Express)
- Database: PostgreSQL for data, Redis for cache
- Authentication: JWT-based

## Design Decisions
See ADRs in .ai-agents/memory/decisions/
```

**api-contracts.md**
```markdown
# API Contracts

## Authentication Endpoints

### POST /api/auth/login
Request:
{
  "email": "string",
  "password": "string"
}

Response:
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
```

**coding-standards.md**
```markdown
# Coding Standards

## JavaScript/TypeScript
- Use TypeScript for all new code
- Follow Airbnb style guide
- Use functional components with hooks
- Prefer const over let

## Naming Conventions
- Components: PascalCase
- Functions: camelCase
- Constants: UPPER_SNAKE_CASE
- Files: kebab-case or PascalCase (for components)

## Testing
- Minimum 80% code coverage
- Test file naming: `*.test.ts` or `*.spec.ts`
- Use descriptive test names
```

### 4. Initialize Agent System

```bash
# Using the composition script (to be created)
python .ai-agents/library/scripts/compose-agent.py \
  --config .ai-agents/config.yml \
  --agent frontend_developer

# This will create a complete agent prompt by composing:
# 1. Base prompt (base/software-developer.md)
# 2. Platform augmentation (platforms/web/frontend-developer.md)
# 3. Project context files
# 4. Tool definitions
```

## Usage

### Composing Agents with Skills

```bash
# Compose frontend developer with all skills
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent frontend_developer \
  --output .ai-agents/prompts/frontend-developer-full.md

# Verify skills are loaded
grep "web-artifacts-builder" .ai-agents/prompts/frontend-developer-full.md
```

The composed prompt will include:
1. Base software developer prompt (~3,000 tokens)
2. Web frontend platform augmentation (~3,000 tokens)
3. Three skills (~7,000 tokens):
   - web-artifacts-builder
   - webapp-testing
   - theme-factory
4. Project context files (variable)

### Starting a New Feature

1. **Manager receives user request**
   ```
   User: "Implement user authentication"
   ```

2. **Manager breaks down the task and uses internal-comms skill**
   ```
   Manager creates tasks and generates 3P update:

   PROGRESS:
   - Analyzed authentication requirements
   - Created task breakdown for 4 agents

   PLANS:
   - TASK-001: Design auth architecture (Architect)
   - TASK-002: Implement JWT service (Backend Dev)
   - TASK-003: Create auth API (Backend Dev)
   - TASK-004: Build login form (Frontend Dev)
   - TASK-005: Write tests (QA Tester)

   PROBLEMS:
   - None currently
   ```

3. **Agents work in parallel (using skills)**
   ```
   Backend Dev → Uses mcp-builder to design JWT service
              → feature/user-auth/agent/backend-dev/jwt-service

   Frontend Dev → Uses web-artifacts-builder to create login form
               → Uses theme-factory for professional styling
               → feature/user-auth/agent/frontend-dev/login-form

   QA Tester → Uses webapp-testing to prepare test scenarios
   ```

4. **Agents report progress**
   ```json
   {
     "type": "status_update",
     "agent_id": "frontend-dev-001",
     "task_id": "TASK-004",
     "status": "in_progress",
     "progress": 75
   }
   ```

5. **Manager coordinates integration**
   - Ensures API contract is followed
   - Resolves any conflicts
   - Coordinates testing

6. **Merge and deploy**
   - QA approves
   - Manager merges all agent branches
   - CI/CD deploys to staging

## Project State

The project state is maintained in `.ai-agents/state/project-state.json`:

```json
{
  "project_id": "ecommerce-web-app",
  "updated_at": "2025-11-20T21:00:00Z",
  "active_tasks": [
    {
      "task_id": "TASK-004",
      "assigned_to": "frontend-dev-001",
      "status": "in_progress",
      "progress": 75
    }
  ],
  "agent_states": {
    "frontend-dev-001": {
      "status": "active",
      "current_task": "TASK-004",
      "branch": "feature/user-auth/agent/frontend-dev/login-form"
    }
  }
}
```

## Best Practices

### 1. Always Define Interfaces First
Before implementation, have agents agree on API contracts and type definitions.

### 2. Use Branch Isolation
Each agent works on their own branch to avoid conflicts:
```
feature/user-auth/
  ├── agent/backend-dev/jwt-service
  ├── agent/backend-dev/auth-api
  └── agent/frontend-dev/login-form
```

### 3. Regular Status Updates
Agents should report progress at 25%, 50%, 75%, and 100% completion.

### 4. Context Management
Monitor context usage and create checkpoints regularly:
```
Context at 75% → Create checkpoint
Context at 85% → Compress old messages
Context at 95% → Emergency checkpoint and restart
```

### 5. Quality Gates
Don't merge until:
- All tests pass
- Code review approved
- Coverage > 80%
- No linting errors

## Troubleshooting

### Agent Conflict
```
Problem: Two agents modified the same file
Solution: Manager coordinates resolution, usually based on task dependencies
```

### Context Overflow
```
Problem: Agent approaching context limit
Solution: Create checkpoint, compress history, or start fresh session
```

### Blocker
```
Problem: Frontend blocked waiting for backend API
Solution: Frontend uses mock API, backend prioritizes completion
```

## Tech Stack

- **Frontend**: React 18, TypeScript, Redux Toolkit, React Router, Tailwind CSS
- **Backend**: Node.js 18, Express, TypeScript, Prisma
- **Database**: PostgreSQL 15, Redis 7
- **Testing**: Jest, React Testing Library, Supertest
- **CI/CD**: GitHub Actions
- **Hosting**: AWS (Frontend: S3 + CloudFront, Backend: ECS)

## Team Velocity Metrics

Track these metrics in `.ai-agents/state/project-state.json`:

- **Tasks completed per sprint**: Target: 20-30
- **Average task completion time**: Target: < 6 hours
- **Test pass rate**: Target: > 95%
- **Code review turnaround**: Target: < 4 hours
- **Deployment frequency**: Target: Daily to staging

## Further Reading

- [Context Engineering Guide](../../Context_Engineering.md)
- [Architecture Documentation](../../ARCHITECTURE.md)
- [Agent Composition](../../scripts/README.md)
