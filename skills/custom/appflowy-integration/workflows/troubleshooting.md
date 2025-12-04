# AppFlowy Troubleshooting Guide

<overview>
Common issues, symptoms, and solutions for AppFlowy integration. This guide covers environment configuration, WebSocket issues, view-database associations, authentication problems, and container behavior.
</overview>

## Table of Contents

1. [Environment Variables Not Taking Effect](#environment-variables-not-taking-effect)
2. [WebSocket Connection Issues](#websocket-connection-issues)
3. [View-Database Association Problems](#view-database-association-problems)
4. [API Authentication Failures](#api-authentication-failures)
5. [Container Restart Behavior](#container-restart-behavior)
6. [Network Connectivity Issues](#network-connectivity-issues)
7. [Database Connection Problems](#database-connection-problems)
8. [Performance Issues](#performance-issues)

---

## Environment Variables Not Taking Effect

<env_vars_issue>
**Symptom:** Changed `.env` file but containers still use old values

**Cause:** Docker Compose caches environment variables in container configuration at creation time. `docker compose restart` does NOT reload `.env` files - it only restarts the container process without recreating the container.

**Solution:**

```bash
# WRONG - doesn't reload .env
docker compose restart

# RIGHT - recreates containers with new .env
docker compose down
docker compose up -d
```

**Why This Happens:**

Docker Compose reads the `.env` file and injects variables into container configuration when you run `docker compose up`. The variables are stored in the container's config. When you `restart`, Docker just stops and starts the same container with the same config.

To pick up new environment variables, you must:
1. `docker compose down` - Removes containers (but keeps volumes/data)
2. `docker compose up -d` - Creates new containers with fresh config from .env

**When to Use Each Command:**

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `docker compose restart` | Restarts container process | Code changes, service glitch |
| `docker compose down && up -d` | Recreates containers | .env changes, config updates |
| `docker compose down -v` | Removes containers AND volumes | Complete reset (⚠️ loses data) |

**Verification:**

```bash
# Check environment variables in running container
docker compose exec appflowy env | grep APPFLOWY

# Should show your new values after down/up
```

**Reference:** See session document INFRA-027 for detailed diagnosis.
</env_vars_issue>

---

## WebSocket Connection Issues

<websocket_issues>
**Symptom:** "Disconnected from cloud" message in AppFlowy UI

**Common Causes:**
1. Wrong WebSocket endpoint (using `/ws/v1` instead of `/ws/v2`)
2. Stale environment variables in containers
3. Domain not resolving (DNS issue)
4. Nginx proxy misconfiguration
5. Firewall blocking WebSocket connections

**Solution 1: Verify WebSocket Endpoint**

```bash
# Correct endpoint for ArkNode-AI
export APPFLOWY_WS_BASE_URL="ws://appflowy.arknode-ai.home/ws/v2/"

# Note: Must be /ws/v2/ NOT /ws/v1/
```

**Check `.env` file:**
```bash
cd /opt/appflowy-cloud
grep APPFLOWY_WS_BASE_URL .env

# Should show: APPFLOWY_WS_BASE_URL=ws://appflowy.arknode-ai.home/ws/v2/
```

**Solution 2: Recreate Containers**

```bash
# Stale environment variables - recreate containers
cd /opt/appflowy-cloud
docker compose down
docker compose up -d

# Wait for services to start
sleep 10
docker compose ps
```

**Solution 3: Test DNS Resolution**

```bash
# Test DNS resolution
nslookup appflowy.arknode-ai.home 192.168.68.10

# Should resolve to 192.168.68.55 (CT102)
```

**Solution 4: Check Browser Console**

1. Open AppFlowy in browser
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Look for WebSocket connection errors

**Common Console Errors:**

```
WebSocket connection to 'ws://appflowy.arknode-ai.home/ws/v1/' failed
→ Wrong endpoint version (should be /ws/v2/)

WebSocket connection refused
→ Service not running or firewall blocking

DNS lookup failed for appflowy.arknode-ai.home
→ DNS issue, check DNS configuration
```

**Solution 5: Verify Nginx Proxy**

```bash
# Check Nginx configuration
ssh root@192.168.68.55
cat /etc/nginx/sites-available/appflowy

# Should include WebSocket upgrade headers:
# proxy_http_version 1.1;
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";
```

**Solution 6: Test WebSocket Connection**

```bash
# Install wscat (WebSocket client)
npm install -g wscat

# Test WebSocket endpoint
wscat -c ws://appflowy.arknode-ai.home/ws/v2/

# Should connect successfully
```

**Permanent Fix Checklist:**

- [ ] `.env` has correct `APPFLOWY_WS_BASE_URL=ws://appflowy.arknode-ai.home/ws/v2/`
- [ ] Containers recreated with `docker compose down && up -d`
- [ ] DNS resolves correctly
- [ ] Nginx proxy configured for WebSocket
- [ ] Browser console shows successful connection
- [ ] UI no longer shows "Disconnected" message

**Reference:** See session document APPFLOWY-004 for detailed WebSocket troubleshooting.
</websocket_issues>

---

## View-Database Association Problems

<view_database_issues>
**Symptom:** Tasks created via API don't appear in AppFlowy UI

**Cause:** AppFlowy requires view objects (Grid, Board, Calendar) to exist as separate collab records in PostgreSQL. The REST API cannot create these view-database associations - only the UI can.

**Detailed Explanation:**

In AppFlowy's architecture:
- **Database** = Container for data (rows/columns)
- **View** = UI representation of database (Grid, Board, Calendar)
- **Association** = Link between view and database (stored in `af_collab` table)

When you create a database via UI:
1. Database record is created
2. Default view is created automatically
3. View-database association is established via WebSocket
4. View appears in UI sidebar

When you create a database via REST API:
1. Database record is created ✅
2. NO view is created ❌
3. NO association exists ❌
4. Tasks exist in database but have no view to display them ❌

**Symptoms:**
- Task created successfully via API (returns row ID)
- Task exists in database (verified in PostgreSQL)
- Task does NOT appear in UI
- Browser console shows: `[useViewOperations] databaseId not found for view`
- No errors in API response

**Solution 1: Create View in UI First (Recommended)**

```
1. Open AppFlowy: http://appflowy.arknode-ai.home
2. Navigate to workspace
3. Find or create your database
4. Click "+" button in database header
5. Select view type:
   - Grid: Spreadsheet view
   - Board: Kanban board
   - Calendar: Calendar view
6. Name your view and click "Create"

Now API-created tasks will appear in this view!
```

**Solution 2: Create Tasks via Browser Console**

This uses your existing session and WebSocket connection (like the UI does):

```javascript
// Open browser console (F12) on AppFlowy page
const WORKSPACE_ID = '22bcbccd-9cf3-41ac-aa0b-28fe144ba71d';
const DATABASE_ID = 'bb7a9c66-8088-4f71-a7b7-551f4c1adc5d';

fetch(`/api/workspace/${WORKSPACE_ID}/database/${DATABASE_ID}/row`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    cells: {
      phVRgL: 'Task Title',     // Description field
      YAgo8T: 'Task details',   // Text field
      SqwRg1: 'CEZD'            // Status: To Do
    }
  })
})
.then(r => r.json())
.then(d => console.log('Created:', d.data));
```

**Solution 3: Verify Database in PostgreSQL**

```bash
# SSH into CT102
ssh root@192.168.68.55

# Access PostgreSQL
docker exec -it appflowy-db psql -U appflowy_user -d appflowy

# Check if task exists
SELECT * FROM af_collab WHERE object_id = 'bb7a9c66-8088-4f71-a7b7-551f4c1adc5d';

# Check views for this database
SELECT * FROM af_collab WHERE object_id LIKE '%view%';
```

**Diagnostic Checklist:**

- [ ] Database exists (check via API)
- [ ] At least one view exists for database (check in UI)
- [ ] View is visible in UI sidebar
- [ ] Task created via API returns success
- [ ] Task appears in view after refresh

**Why This Is Important:**

This is a **fundamental limitation** of AppFlowy's REST API. Until AppFlowy adds view creation to the REST API, you MUST:
1. Create databases and views via UI
2. Then use API for task operations

**Workaround for Automation:**

```python
def ensure_view_exists(client, workspace_id, database_id, database_name):
    """Check if database has views, provide instructions if not."""
    views = client.list_database_views(workspace_id, database_id)

    if len(views) == 0:
        print(f"⚠️  Database '{database_name}' has no views!")
        print("\nCreate a view manually:")
        print(f"1. Open http://appflowy.arknode-ai.home")
        print(f"2. Find database: {database_name}")
        print(f"3. Click '+' → Select 'Grid' or 'Board'")
        print(f"4. Name it and click 'Create'")
        print(f"\nAfter creating view, run your script again.")
        return False

    return True

# Usage before creating tasks
if not ensure_view_exists(client, client.workspace_id, database_id, 'To-dos'):
    exit(1)

# Now safe to create tasks
task = client.create_row(...)
```

**Reference:** See session documents APPFLOWY-006 and APPFLOWY-008 for detailed troubleshooting.
</view_database_issues>

---

## API Authentication Failures

<auth_failures>
**Symptom:** API calls return 401 Unauthorized or 403 Forbidden

**Causes:**
1. JWT token expired
2. Invalid or missing token
3. Wrong API endpoint
4. Token doesn't have required permissions
5. Token for wrong workspace

**Solution 1: Token Expired - Get New Token**

```bash
# Get fresh JWT token
curl -X POST "http://appflowy.arknode-ai.home/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@arknode.local",
    "password": "your-password",
    "grant_type": "password"
  }'

# Response includes:
# - access_token: Use this for API calls
# - refresh_token: Use to get new access token
# - expires_in: Token lifetime in seconds (usually 3600 = 1 hour)
```

**Solution 2: Use Refresh Token**

```bash
# Refresh token without password
curl -X POST "http://appflowy.arknode-ai.home/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token",
    "grant_type": "refresh_token"
  }'
```

**Solution 3: Implement Automatic Token Refresh**

```python
import os
import time
import requests
from datetime import datetime, timedelta

class AppFlowyClient:
    def __init__(self):
        self.api_url = os.getenv('APPFLOWY_API_URL')
        self.email = os.getenv('APPFLOWY_EMAIL')
        self.password = os.getenv('APPFLOWY_PASSWORD')
        self.token = None
        self.refresh_token = None
        self.token_expires_at = None

    def authenticate(self):
        """Get new JWT token."""
        response = requests.post(
            f"{self.api_url}/gotrue/token",
            json={
                "email": self.email,
                "password": self.password,
                "grant_type": "password"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        print(f"✅ Authenticated, token expires at {self.token_expires_at}")

    def refresh_token_if_needed(self):
        """Check if token is expired and refresh if needed."""
        if not self.token or not self.token_expires_at:
            self.authenticate()
            return

        # Refresh if expiring in next 5 minutes
        if datetime.utcnow() + timedelta(minutes=5) > self.token_expires_at:
            print("🔄 Token expiring soon, refreshing...")
            response = requests.post(
                f"{self.api_url}/gotrue/token",
                json={
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()

            data = response.json()
            self.token = data['access_token']
            self.refresh_token = data['refresh_token']
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            print(f"✅ Token refreshed, expires at {self.token_expires_at}")

    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated API request with auto-refresh."""
        self.refresh_token_if_needed()

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers

        url = f"{self.api_url}{endpoint}"
        response = requests.request(method, url, **kwargs)

        # Retry once if token expired
        if response.status_code == 401:
            print("⚠️  Token expired, re-authenticating...")
            self.authenticate()
            headers['Authorization'] = f'Bearer {self.token}'
            response = requests.request(method, url, **kwargs)

        response.raise_for_status()
        return response.json()
```

**Solution 4: Verify Token with Test Request**

```bash
# Test token validity
curl -X GET "http://appflowy.arknode-ai.home/api/workspace" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"

# Should return workspace list
# If 401: Token expired or invalid
# If 403: Token valid but insufficient permissions
# If 404: Wrong endpoint URL
```

**Solution 5: Check Token Permissions**

```python
def verify_token_access(client):
    """Verify token has required permissions."""
    tests = []

    # Test 1: Can list workspaces
    try:
        workspaces = client.list_workspaces()
        tests.append(("List workspaces", True))
    except Exception as e:
        tests.append(("List workspaces", False, str(e)))

    # Test 2: Can access specific workspace
    try:
        workspace_info = client.get_workspace_info(client.workspace_id)
        tests.append(("Access workspace", True))
    except Exception as e:
        tests.append(("Access workspace", False, str(e)))

    # Test 3: Can list databases
    try:
        databases = client.list_databases(client.workspace_id)
        tests.append(("List databases", True))
    except Exception as e:
        tests.append(("List databases", False, str(e)))

    # Print results
    print("Token Permission Tests:")
    for test in tests:
        status = "✅" if test[1] else "❌"
        message = test[0]
        error = test[2] if len(test) > 2 else ""
        print(f"{status} {message} {error}")

# Usage
verify_token_access(client)
```

**Common Error Messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Token expired or invalid | Get new token |
| 403 Forbidden | Token lacks permissions | Check workspace access |
| 404 Not Found | Wrong endpoint or resource | Verify URL and IDs |
| 500 Server Error | AppFlowy server issue | Check server logs |
</auth_failures>

---

## Container Restart Behavior

<container_restart>
**Understanding Docker Compose Commands:**

```bash
# restart - Restarts container process (keeps same container)
docker compose restart
# Use when: Code changes, service glitch, doesn't need config reload

# down/up - Removes and recreates containers (new config)
docker compose down && docker compose up -d
# Use when: .env changes, docker-compose.yml changes, config updates

# down -v - Removes containers AND volumes (deletes data!)
docker compose down -v && docker compose up -d
# Use when: Complete reset needed, database corruption
```

**Container State Persistence:**

| What | Persists After Restart | Persists After Down/Up | Lost After down -v |
|------|----------------------|----------------------|-------------------|
| Container config | ✅ Yes | ❌ No (recreated) | ❌ No |
| Environment variables | ✅ Yes | ❌ No (reloaded from .env) | ❌ No |
| Running processes | ❌ No (restarted) | ❌ No (restarted) | ❌ No |
| Volume data | ✅ Yes | ✅ Yes | ❌ No (deleted!) |
| Network settings | ✅ Yes | ❌ No (recreated) | ❌ No |

**Common Scenarios:**

**Scenario 1: Changed WebSocket URL in .env**
```bash
# Wrong approach
docker compose restart  # ❌ Won't pick up new .env

# Correct approach
docker compose down
docker compose up -d    # ✅ Recreates with new config
```

**Scenario 2: AppFlowy Not Responding**
```bash
# Try restart first (faster)
docker compose restart appflowy

# If that doesn't work, recreate
docker compose down
docker compose up -d
```

**Scenario 3: Database Corruption**
```bash
# Backup data first!
docker compose exec postgres pg_dump -U appflowy_user appflowy > backup.sql

# Complete reset
docker compose down -v  # ⚠️ Deletes database!
docker compose up -d

# Restore data
docker compose exec -T postgres psql -U appflowy_user appflowy < backup.sql
```

**Scenario 4: Upgrade AppFlowy Image**
```bash
# Pull new image
docker compose pull

# Recreate containers with new image
docker compose down
docker compose up -d
```

**Check Container Status:**

```bash
# View running containers
docker compose ps

# Check if containers are healthy
docker compose ps | grep healthy

# View container logs
docker compose logs -f appflowy

# Check resource usage
docker stats appflowy appflowy-db
```
</container_restart>

---

## Network Connectivity Issues

<network_issues>
**Symptom:** Cannot reach AppFlowy instance

**Diagnostic Steps:**

**Step 1: Test Basic Connectivity**
```bash
# Ping the host
ping appflowy.arknode-ai.home

# Should respond with: 192.168.68.55 (CT102)
```

**Step 2: Test DNS Resolution**
```bash
# Test with your DNS server
nslookup appflowy.arknode-ai.home 192.168.68.10

# Should return: 192.168.68.55
```

**Step 3: Test Port Accessibility**
```bash
# Test if port 80 is open
nc -zv appflowy.arknode-ai.home 80

# Or use telnet
telnet appflowy.arknode-ai.home 80
```

**Step 4: Test API Endpoint**
```bash
# Test health endpoint
curl -v http://appflowy.arknode-ai.home/health

# Test API endpoint
curl -v http://appflowy.arknode-ai.home/api/workspace
```

**Common Network Issues:**

**Issue 1: DNS Not Resolving**
```bash
# Check DNS configuration
cat /etc/resolv.conf

# Should include: nameserver 192.168.68.10

# Temporarily use IP address
curl http://192.168.68.55/api/workspace
```

**Issue 2: Firewall Blocking**
```bash
# Check firewall rules (on CT102)
ssh root@192.168.68.55
iptables -L -n | grep 80

# Check if Nginx is listening
netstat -tuln | grep :80
```

**Issue 3: Container Not Running**
```bash
# Check container status
ssh root@192.168.68.55
cd /opt/appflowy-cloud
docker compose ps

# Should show "running" and "healthy"
```

**Issue 4: Nginx Not Proxying Correctly**
```bash
# Check Nginx logs
ssh root@192.168.68.55
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```
</network_issues>

---

## Database Connection Problems

<database_issues>
**Symptom:** AppFlowy can't connect to PostgreSQL

**Diagnostic Steps:**

**Step 1: Verify PostgreSQL is Running**
```bash
docker compose ps postgres

# Should show "running" status
```

**Step 2: Test Database Connection**
```bash
# Connect to database
docker exec -it appflowy-db psql -U appflowy_user -d appflowy

# If successful, you should see:
# appflowy=#
```

**Step 3: Check DATABASE_URL**
```bash
# Verify format
grep DATABASE_URL .env

# Should be:
# DATABASE_URL=postgresql://appflowy_user:password@postgres:5432/appflowy
```

**Step 4: Check Database Logs**
```bash
docker compose logs postgres

# Look for connection errors
```

**Common Database Issues:**

**Issue 1: Wrong Password**
```bash
# Update password in .env
DB_PASSWORD=new_secure_password
DATABASE_URL=postgresql://appflowy_user:new_secure_password@postgres:5432/appflowy

# Recreate containers
docker compose down
docker compose up -d
```

**Issue 2: Database Not Ready**
```bash
# AppFlowy started before PostgreSQL was ready
# Check if PostgreSQL is healthy
docker compose ps postgres

# Restart AppFlowy
docker compose restart appflowy
```

**Issue 3: Connection Pool Exhausted**
```bash
# Check PostgreSQL connections
docker exec -it appflowy-db psql -U appflowy_user -d appflowy -c \
  "SELECT count(*) FROM pg_stat_activity;"

# If too many connections, restart AppFlowy
docker compose restart appflowy
```
</database_issues>

---

## Performance Issues

<performance_issues>
**Symptom:** AppFlowy is slow or unresponsive

**Diagnostic Steps:**

**Step 1: Check Resource Usage**
```bash
# View container resource usage
docker stats appflowy appflowy-db

# Look for:
# - High CPU usage (>80%)
# - High memory usage (>80%)
# - High I/O
```

**Step 2: Check Container Logs**
```bash
# Look for errors or warnings
docker compose logs --tail=100 appflowy

# Look for:
# - Database query timeouts
# - Memory errors
# - Connection pool issues
```

**Step 3: Check Database Size**
```bash
# Connect to database
docker exec -it appflowy-db psql -U appflowy_user -d appflowy

# Check database size
SELECT pg_size_pretty(pg_database_size('appflowy'));

# Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

**Solutions:**

**Solution 1: Increase Container Resources**
```yaml
# Edit docker-compose.yml
services:
  appflowy:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

**Solution 2: Clean Up Old Data**
```bash
# Backup first!
docker compose exec postgres pg_dump -U appflowy_user appflowy > backup.sql

# Vacuum database
docker exec -it appflowy-db psql -U appflowy_user -d appflowy -c "VACUUM FULL;"
```

**Solution 3: Optimize PostgreSQL**
```bash
# Edit PostgreSQL configuration
docker exec -it appflowy-db vi /var/lib/postgresql/data/postgresql.conf

# Add/update:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB

# Restart PostgreSQL
docker compose restart postgres
```
</performance_issues>

---

## Related Documentation

- **API Reference**: See `references/api-reference.md` for API details
- **Task Management**: See `workflows/task-management.md` for task operations
- **Workspace Operations**: See `workflows/workspace-operations.md` for workspace setup
- **Server Deployment**: See `workflows/server-deployment.md` for deployment guides
