# AppFlowy Integration Skill

Integration skill for AppFlowy, an open-source project management and collaborative workspace tool.

## Overview

This skill enables AI agents to:
- Create and update tasks in AppFlowy databases
- Manage workspaces and folders
- Track project progress
- Generate project dashboards
- Sync agent work with AppFlowy

## Quick Start

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

## Directory Structure

```
appflowy-integration/
├── SKILL.md                    # Main skill documentation
├── README.md                   # This file
├── scripts/
│   ├── appflowy_client.py      # Python API client
│   └── task_tracker.py         # CLI task tracker
└── references/
    ├── docker-compose.yml      # Docker deployment
    └── setup_guide.md          # Detailed setup guide
```

## Requirements

- Python 3.7+
- `requests` library: `pip install requests`
- AppFlowy instance (self-hosted or cloud)
- JWT authentication token

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
