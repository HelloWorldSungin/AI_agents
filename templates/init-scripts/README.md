# init.sh Templates

Environment setup script templates for common technology stacks. These templates enable the IT Specialist agent to generate project-specific setup scripts that automate the onboarding process.

## Available Templates

### 1. Node.js/React (`nodejs-react-init.sh`)

**Stack**: React + Vite + Node.js backend

**Features**:
- Node.js version check (v18+)
- npm dependency installation
- Environment variable setup (.env)
- Docker database support
- Database migrations
- Build verification
- Test execution

**Usage**:
```bash
# Customize template variables
PROJECT_NAME="my-react-app"
DEV_PORT="5173"
API_PORT="3000"

# Generate and run
./nodejs-react-init.sh
```

### 2. Python/Django (`python-django-init.sh`)

**Stack**: Django + PostgreSQL

**Features**:
- Python 3 version check
- Virtual environment creation
- pip dependency installation
- Environment variable setup
- Docker database support
- Django migrations
- Static files collection
- Superuser setup guidance
- Fixture loading

**Usage**:
```bash
# Customize template variables
PROJECT_NAME="my-django-app"
PYTHON_VERSION="3.11"

# Generate and run
./python-django-init.sh
```

### 3. Full-stack (`fullstack-init.sh`)

**Stack**: React (frontend) + Node.js/Express (backend) + PostgreSQL

**Features**:
- Separate frontend/backend setup
- Docker Compose database
- Environment files for both layers
- Database migrations and seeding
- Build verification for both layers
- Test execution for both layers
- Port conflict detection

**Usage**:
```bash
# Customize template variables
PROJECT_NAME="my-fullstack-app"
FRONTEND_PORT="5173"
BACKEND_PORT="3000"

# Generate and run
./fullstack-init.sh
```

## Template Variables

All templates support these placeholder variables:

- `{{PROJECT_NAME}}`: Name of the project
- `{{DEV_PORT}}`: Frontend development server port
- `{{API_PORT}}`: Backend API server port
- `{{PYTHON_VERSION}}`: Required Python version
- `{{FRONTEND_PORT}}`: Frontend-specific port
- `{{BACKEND_PORT}}`: Backend-specific port

## Using Templates

### For IT Specialist Agent

When generating init.sh for a new project:

1. Identify the technology stack
2. Select appropriate template
3. Replace template variables with project specifics
4. Add custom steps if needed
5. Save as `init.sh` in project root
6. Make executable: `chmod +x init.sh`
7. Test the script
8. Document in infrastructure setup report

### Customization Example

```bash
# Start with template
cp templates/init-scripts/nodejs-react-init.sh my-project/init.sh

# Replace variables
sed -i 's/{{PROJECT_NAME}}/my-awesome-app/g' my-project/init.sh
sed -i 's/{{DEV_PORT:-5173}}/5174/g' my-project/init.sh

# Add custom steps (e.g., install Playwright)
# Edit init.sh and add to install_dependencies():
#   npx playwright install

# Make executable and test
chmod +x my-project/init.sh
cd my-project && ./init.sh
```

## What Init Scripts Should Do

✅ **Must Have**:
- Prerequisite checks (Node, Python, Docker, etc.)
- Environment variable setup (.env from template)
- Dependency installation
- Database setup (if applicable)
- Basic verification (tests, build)
- Clear next steps output

✅ **Should Have**:
- Helpful error messages
- Progress indicators
- Version checks for critical tools
- Graceful handling of optional dependencies

❌ **Should NOT**:
- Make destructive changes without confirmation
- Require user input mid-script (except for credentials)
- Install system-level dependencies (only project deps)
- Modify existing .env files (create from template only)

## Best Practices

### Error Handling

```bash
set -e  # Exit on any error

# Check before proceeding
if ! command -v node &> /dev/null; then
    echo "❌ Node.js required"
    exit 1
fi
```

### User Feedback

```bash
echo "📋 Checking prerequisites..."     # What's happening
echo "✅ Node.js $(node --version)"    # Success
echo "❌ Missing dependency"            # Error
echo "⚠️  Optional tool not found"     # Warning
echo "ℹ️  Skipping optional step"      # Info
```

### Idempotency

```bash
# Can run multiple times safely
if [ ! -f .env ]; then
    cp .env.example .env
else
    echo "✅ .env already exists"
fi
```

### Clear Next Steps

```bash
echo ""
echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file"
echo "2. Run: npm run dev"
echo "3. Visit: http://localhost:3000"
```

## Adding New Templates

To add a template for a new stack:

1. Create new file: `{stack-name}-init.sh`
2. Include all standard sections:
   - Prerequisites check
   - Environment setup
   - Dependency installation
   - Database setup (if applicable)
   - Build/verification
   - Next steps
3. Add template variables
4. Document in this README
5. Test thoroughly

## Testing Templates

Before committing a new template:

```bash
# Create test project
mkdir test-project
cp template-name-init.sh test-project/init.sh

# Replace variables
cd test-project
sed -i 's/{{PROJECT_NAME}}/test/g' init.sh

# Run script
chmod +x init.sh
./init.sh

# Verify:
# - All dependencies installed
# - Environment configured
# - Tests pass (if applicable)
# - Clear next steps shown
```

## Related Documentation

- IT Specialist prompt: `prompts/it-specialist-agent.md`
- Infrastructure validation guide: `docs/guides/`
- Example projects: `examples/`
