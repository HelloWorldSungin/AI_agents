# AppFlowy Integration Skill

Integration skill for AppFlowy, an open-source project management and collaborative workspace tool.

## Overview

This skill enables AI agents to:
- ✅ Create and update tasks in AppFlowy databases
- ✅ Sync documentation with rich text formatting (bold, italic, code, links, strikethrough)
- ✅ Automated `git pushsync` workflow - push to GitHub + sync to AppFlowy in one command
- ✅ Set up new project workspaces automatically
- ✅ Manage and monitor self-hosted AppFlowy servers
- ✅ Track project progress and generate dashboards
- ✅ Sync agent work with AppFlowy
- ✅ Backup and restore AppFlowy data

## Quick Start

### Current Configuration (AI Agents Workspace)

**Workspace Info:**
- Workspace ID: `c9674d81-6037-4dc3-9aa6-e2d833162b0f`
- Documentation Parent: `c7f9f933-ca10-4206-8be4-a2967f1085aa`
- Credentials: `/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env`
- Web UI: https://appflowy.ark-node.com

**Recommended Workflow:**
```bash
# Make changes to documentation
git add .
git commit -m "docs: update"
git pushsync  # Push to GitHub + auto-sync to AppFlowy
```

**Mapping File:**
Create `appflowy-mapping.yaml` in project root to prevent duplicate pages:
```yaml
mappings:
  README.md: existing-page-id
  docs/guide.md: another-page-id
```

### 1. Deploy AppFlowy

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name appflowy \
  -p 8080:80 \
  -v ./appflowy-data:/data \
  appflowy/appflowy-cloud:latest
```

**Option B: Synology NAS**
1. Open Container Manager
2. Search for "appflowy"
3. Download and run with port 8080:80

**Option C: Docker Compose**
```bash
cd skills/custom/appflowy-integration/references/
docker-compose up -d
```

### 2. Configure Environment

Create `.env` file:
```bash
APPFLOWY_API_URL=http://localhost:8080
APPFLOWY_API_TOKEN=your_jwt_token_here
APPFLOWY_WORKSPACE_ID=your_workspace_id
APPFLOWY_DOCS_PARENT_ID=parent_page_id  # Optional: Parent page for docs hierarchy
APPFLOWY_DATABASE_ID=your_database_id   # For task sync
```

### 3. Get API Token

```bash
curl -X POST "http://localhost:8080/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password",
    "grant_type": "password"
  }'
```

Extract the `access_token` from the response.

### 4. Test Connection

```bash
cd scripts/
python appflowy_client.py
```

## Usage Examples

### Set Up New Project Workspace
```bash
# Interactive setup
python workspace_setup.py

# Or with command-line args
python workspace_setup.py --project "My New Project" --team dev1@team.com dev2@team.com
```

### Manage AppFlowy Server
```bash
# Start server
./manage_server.sh start

# Check status
./manage_server.sh status

# View logs
./manage_server.sh logs

# Backup database
./manage_server.sh backup

# Update to latest version
./manage_server.sh update
```

### Create a Task
```bash
python task_tracker.py create "Implement feature X" \
  --priority high \
  --status "In Progress" \
  --tags development feature
```

### Update Task Status
```bash
python task_tracker.py update <task_id> --status completed
```

### List Recent Tasks
```bash
python task_tracker.py list --hours 24 --limit 10
```

### Python Integration
```python
from appflowy_client import AppFlowyClient

client = AppFlowyClient()

# List workspaces
workspaces = client.list_workspaces()

# Create a task
task_data = {
    'title': 'Review pull request',
    'status': 'Todo',
    'priority': 'High'
}
task = client.create_row(database_id, task_data)
```

## Documentation Sync (NEW!)

Automatically sync AI_agents documentation to AppFlowy:

### Quick Setup
1. **Create Documentation database** in AppFlowy (see [SETUP_DOCUMENTATION_DATABASE.md](SETUP_DOCUMENTATION_DATABASE.md))
2. **Add database ID** to `.env`:
   ```bash
   APPFLOWY_DOCS_DATABASE_ID=your-database-id-here
   ```
3. **Test connection**:
   ```bash
   cd scripts/
   python3 test_connection.py
   ```
4. **Sync documentation**:
   ```bash
   python3 sync_documentation.py --dry-run  # Test first
   python3 sync_documentation.py            # Sync for real
   ```

### Features
- **Auto-detects field IDs** from database schema
- **Incremental sync** - only syncs changed files
- **14 documentation files** organized by category
- **Dry-run mode** for testing
- **Force sync** to re-sync all files

See [SETUP_DOCUMENTATION_DATABASE.md](SETUP_DOCUMENTATION_DATABASE.md) for detailed setup instructions.

## AppFlowy API: Delta Block Format

### Critical Information

**AppFlowy uses block-based Delta format, NOT raw markdown.** You must create pages first, then append content blocks.

**Correct API Endpoints:**

1. **Create Page (Empty):**
   ```
   POST /api/workspace/{workspace_id}/page-view
   {
     "name": "Page Title",
     "layout": 0,
     "parent_view_id": "parent_id"  // Optional: for nested pages
   }
   ```

2. **Append Content Blocks:**
   ```
   POST /api/workspace/{workspace_id}/page-view/{page_id}/append-block
   {
     "blocks": [
       {"type": "heading", "data": {"level": 1, "delta": [{"insert": "Title"}]}},
       {"type": "paragraph", "data": {"delta": [{"insert": "Text"}]}},
       {"type": "bulleted_list", "data": {"delta": [{"insert": "Item"}]}}
     ]
   }
   ```

3. **Update Metadata Only:**
   ```
   PATCH /api/workspace/{workspace_id}/page-view/{page_id}
   {
     "name": "Updated Title"
   }
   ```
   **Note:** PATCH does NOT update content. Use append-block for content.

### Markdown to Delta Blocks Converter

The `markdown_to_blocks()` function (in `update_page_content.py` and `sync_docs.py`) converts markdown to AppFlowy Delta blocks:

**Supported Markdown Elements:**
- ✅ **Headings** (# through ######)
- ✅ **Bullet lists** (-, *)
- ✅ **Numbered lists** (1., 2., etc.)
- ✅ **Code blocks** (``` with language detection)
- ✅ **Blockquotes** (>)
- ✅ **Paragraphs** (regular text)
- ✅ **Rich text formatting:**
  - **Bold** (`**text**`)
  - *Italic* (`*text*`)
  - `Code` (`` `text` ``)
  - [Links](url) (`[text](url)`)
  - ~~Strikethrough~~ (`~~text~~`)
- ✅ **Tables** (rendered as code blocks)

**Usage:**
```bash
# Update a single page with markdown content
cd scripts/
python3 update_page_content.py README.md

# Test first with dry run
python3 update_page_content.py README.md --dry-run

# Update all synced pages
python3 batch_update_all.py

# Verify page content
python3 verify_page_content.py README.md
```

**Integration Example:**
```python
from update_page_content import markdown_to_blocks, append_blocks_to_page

# Convert markdown to blocks
blocks = markdown_to_blocks(markdown_content)

# Append to page
append_blocks_to_page(api_url, workspace_id, page_id, blocks, token)
```

**Performance:**
- README.md: 675 blocks successfully converted
- Processing time: ~1.5 seconds for 52KB file
- API endpoint: `/api/workspace/{workspace_id}/page-view/{page_id}/append-block`
- Format: AppFlowy Delta blocks (compatible with Quill.js)

## Directory Structure

```
appflowy-integration/
├── SKILL.md                           # Main skill documentation
├── README.md                          # This file
├── SETUP_DOCUMENTATION_DATABASE.md    # Documentation sync setup guide
├── MARKDOWN_CONVERTER_REPORT.md       # Converter implementation report (NEW!)
├── .sync-status.json                  # Page ID mappings
├── scripts/
│   ├── appflowy_client.py             # Python API client
│   ├── sync_documentation.py          # Documentation sync script
│   ├── test_connection.py             # Connection test script
│   ├── update_page_content.py         # Markdown to AppFlowy converter (NEW!)
│   ├── batch_update_all.py            # Batch page updater (NEW!)
│   ├── verify_page_content.py         # Page verification tool (NEW!)
│   ├── task_tracker.py                # CLI task tracker
│   ├── workspace_setup.py             # Workspace setup helper
│   └── manage_server.sh               # Server management script
└── references/
    ├── docker-compose.yml             # Docker deployment
    └── setup_guide.md                 # Detailed setup guide
```

## Key Features

- 🚀 **Git PushSync Workflow** - Push to GitHub + auto-sync to AppFlowy in one command
- 📝 **Rich Text Support** - Bold, italic, code, links, strikethrough formatting
- 🗺️ **Mapping File** - Prevent duplicate pages with explicit page ID tracking
- 🔄 **Content Updates** - Rename-and-recreate strategy for clean updates
- 🚀 **Workspace Setup Automation** - Initialize project workspaces with one command
- 🔧 **Server Management** - Complete lifecycle management (start, stop, monitor, backup, update)
- 📋 **Task Tracking** - Create and manage tasks from command line or Python
- 📊 **Project Dashboards** - Generate status reports and team summaries
- 🏠 **Self-Hosted Support** - Full support for Synology NAS, Docker, home servers
- 🔐 **Secure** - JWT authentication with token refresh support

## Current Stats (AI Agents Workspace)

- 15 documentation pages synced
- 10 tasks synced to Kanban board
- Rich text formatting working end-to-end
- Git pushsync automation active

## Requirements

- Python 3.7+
- `requests` library: `pip install requests`
- AppFlowy instance (self-hosted or cloud)
- JWT authentication token
- Docker & Docker Compose (for self-hosted deployment)
- `jq` (optional, for JSON formatting in scripts)

## Self-Hosted Deployment

### Synology NAS (DS 923+)
- Use Container Manager
- Map port 8080:80
- Set volume for data persistence
- Access via `http://nas-ip:8080`

### AI Home Server
- Use Docker Compose (see `references/docker-compose.yml`)
- Configure reverse proxy for HTTPS (optional)
- Set up PostgreSQL for data storage

## Troubleshooting

### Connection Issues
```bash
# Test API endpoint
curl http://localhost:8080/api/workspace

# Check Docker container
docker ps | grep appflowy
docker logs appflowy
```

### Authentication Errors
- Verify token hasn't expired
- Check token is correctly set in environment
- Re-authenticate to get new token

### Database Not Found
- Create "Tasks" database in AppFlowy UI
- Or specify different database name in scripts

## Resources

- [AppFlowy GitHub](https://github.com/AppFlowy-IO/AppFlowy)
- [API Documentation](https://github.com/AppFlowy-IO/documentations/blob/main/documentation/appflowy-cloud/openapi/README.md)
- [AppFlowy Cloud](https://github.com/AppFlowy-IO/AppFlowy-Cloud)

## License

This skill is part of the AI Agents project and follows the same license.

AppFlowy is licensed under AGPLv3.
