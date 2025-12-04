# Server Deployment and Management

<overview>
Comprehensive guide for deploying, managing, and maintaining AppFlowy self-hosted instances. Covers container operations, monitoring, backup/restore, and automation.
</overview>

## Table of Contents

1. [Start and Stop Server](#start-and-stop-server)
2. [Monitor Server Health](#monitor-server-health)
3. [Backup and Restore](#backup-and-restore)
4. [Container Management](#container-management)
5. [Auto-Start Configuration](#auto-start-configuration)
6. [Server Management Script](#server-management-script)
7. [Upgrade Procedures](#upgrade-procedures)

---

## Start and Stop Server

<start_stop_server>
**Start AppFlowy Backend:**

```bash
# Navigate to deployment directory
cd /opt/appflowy-cloud

# Start services in background
docker-compose up -d

# Check startup status
docker-compose ps

# View startup logs
docker-compose logs -f appflowy

# Wait for healthy status
docker-compose ps | grep appflowy | grep healthy
```

**Start with Fresh Logs:**

```bash
# Remove old logs and start
docker-compose down
docker-compose up -d

# Follow startup process
docker-compose logs -f --tail=50
```

**Stop AppFlowy Backend:**

```bash
# Graceful shutdown (keeps data)
docker-compose down

# Shutdown takes 10-30 seconds
# Waits for connections to close
```

**Stop Services Only (Keep Containers):**

```bash
# Stop but keep container configuration
docker-compose stop

# Restart without recreating
docker-compose start
```

**Emergency Stop:**

```bash
# Force stop all containers
docker-compose kill

# Then clean up
docker-compose down
```

**Stop and Remove All Data (⚠️ Destructive!):**

```bash
# Backup first!
docker-compose exec postgres pg_dump -U appflowy_user appflowy > backup_$(date +%Y%m%d).sql

# Remove everything including volumes
docker-compose down -v

# This deletes:
# - All containers
# - All volumes (database data!)
# - All networks
```

**Restart Specific Service:**

```bash
# Restart just AppFlowy (not database)
docker-compose restart appflowy

# Restart just PostgreSQL
docker-compose restart postgres

# Restart all services
docker-compose restart
```
</start_stop_server>

---

## Monitor Server Health

<monitor_health>
**Check Service Status:**

```bash
# View all services
docker-compose ps

# Expected output:
# NAME               STATUS              PORTS
# appflowy           Up (healthy)        0.0.0.0:80->80/tcp
# appflowy-db        Up                  5432/tcp
```

**Health Check Script:**

```bash
#!/bin/bash
# save as: health_check.sh

echo "🏥 AppFlowy Health Check"
echo "=" * 60

# 1. Container status
echo "📦 Container Status:"
docker-compose ps

# 2. Container health
echo -e "\n💓 Health Status:"
docker inspect appflowy | jq '.[0].State.Health.Status'

# 3. API endpoint
echo -e "\n🌐 API Health:"
curl -s http://appflowy.arknode-ai.home/health | jq .

# 4. Database connectivity
echo -e "\n🗄️  Database Status:"
docker-compose exec -T postgres pg_isready -U appflowy_user

# 5. Disk usage
echo -e "\n💾 Disk Usage:"
docker system df

# 6. Resource usage
echo -e "\n📊 Resource Usage:"
docker stats --no-stream appflowy appflowy-db

echo "=" * 60
```

**Real-Time Monitoring:**

```bash
# Monitor resource usage (live)
docker stats appflowy appflowy-db

# Press Ctrl+C to exit
```

**Check API Health:**

```bash
# Test health endpoint
curl http://appflowy.arknode-ai.home/health

# Expected response:
# {"status":"ok"}

# Test API endpoint
curl -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  http://appflowy.arknode-ai.home/api/workspace

# Should return workspace list
```

**View Service Logs:**

```bash
# Real-time logs for all services
docker-compose logs -f

# Logs for specific service
docker-compose logs -f appflowy
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 appflowy

# Logs since specific time
docker-compose logs --since 2h appflowy

# Save logs to file
docker-compose logs > appflowy_logs_$(date +%Y%m%d).txt
```

**Monitor Disk Space:**

```bash
# Check Docker disk usage
docker system df

# Detailed breakdown
docker system df -v

# Check container volumes
docker volume ls
docker volume inspect appflowy_postgres-data
```

**Database Monitoring:**

```bash
# Connect to database
docker exec -it appflowy-db psql -U appflowy_user -d appflowy

# Check database size
SELECT pg_size_pretty(pg_database_size('appflowy'));

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
AND now() - query_start > interval '5 seconds';
```

**Set Up Monitoring Alerts:**

```bash
#!/bin/bash
# save as: monitoring_alert.sh

# Check if AppFlowy is running
if ! docker-compose ps appflowy | grep -q "Up"; then
    echo "❌ AppFlowy is DOWN!" | mail -s "AppFlowy Alert" admin@example.com
fi

# Check disk space
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  Disk usage is ${DISK_USAGE}%" | mail -s "Disk Alert" admin@example.com
fi

# Run every 5 minutes via cron:
# */5 * * * * /opt/appflowy-cloud/monitoring_alert.sh
```
</monitor_health>

---

## Backup and Restore

<backup_restore>
**Manual Database Backup:**

```bash
# Create backup directory
mkdir -p /opt/appflowy-backups

# Backup database
docker-compose exec -T postgres pg_dump -U appflowy_user appflowy | \
  gzip > /opt/appflowy-backups/appflowy_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify backup
ls -lh /opt/appflowy-backups/
```

**Automated Daily Backup:**

```bash
#!/bin/bash
# save as: backup_appflowy.sh

BACKUP_DIR="/opt/appflowy-backups"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Starting AppFlowy backup: $DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose -f /opt/appflowy-cloud/docker-compose.yml exec -T postgres \
  pg_dump -U appflowy_user appflowy | \
  gzip > "${BACKUP_DIR}/appflowy_db_${DATE}.sql.gz"

# Backup volumes
docker-compose -f /opt/appflowy-cloud/docker-compose.yml stop
tar -czf "${BACKUP_DIR}/appflowy_volumes_${DATE}.tar.gz" \
  -C /var/lib/docker/volumes appflowy_postgres-data appflowy_appflowy-data
docker-compose -f /opt/appflowy-cloud/docker-compose.yml start

# Backup .env file
cp /opt/appflowy-cloud/.env "${BACKUP_DIR}/appflowy_env_${DATE}.env"

# Remove old backups (older than retention period)
find "$BACKUP_DIR" -name "appflowy_*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "appflowy_*.env" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup complete: ${BACKUP_DIR}/appflowy_db_${DATE}.sql.gz"

# Add to crontab for daily 2 AM backup:
# 0 2 * * * /opt/appflowy-cloud/backup_appflowy.sh >> /var/log/appflowy_backup.log 2>&1
```

**Restore from Backup:**

```bash
# Stop AppFlowy
docker-compose down

# Restore database
gunzip < /opt/appflowy-backups/appflowy_20251204_120000.sql.gz | \
  docker-compose exec -T postgres psql -U appflowy_user appflowy

# Or restore with running containers
docker-compose up -d postgres
sleep 5  # Wait for PostgreSQL to be ready
gunzip < /opt/appflowy-backups/appflowy_20251204_120000.sql.gz | \
  docker-compose exec -T postgres psql -U appflowy_user appflowy

# Start AppFlowy
docker-compose up -d

# Verify restoration
docker-compose logs -f appflowy
```

**Restore Volumes:**

```bash
# Stop services
docker-compose down

# Extract volumes
tar -xzf /opt/appflowy-backups/appflowy_volumes_20251204_120000.tar.gz \
  -C /var/lib/docker/volumes

# Start services
docker-compose up -d
```

**Backup to Remote Server:**

```bash
#!/bin/bash
# save as: backup_to_remote.sh

REMOTE_HOST="backup-server.example.com"
REMOTE_USER="backup"
REMOTE_PATH="/backups/appflowy"
LOCAL_BACKUP="/opt/appflowy-backups"

# Create local backup
/opt/appflowy-cloud/backup_appflowy.sh

# Copy to remote server
rsync -avz --delete \
  "$LOCAL_BACKUP/" \
  "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"

echo "✅ Backup synced to remote server"
```

**Test Backup Restoration:**

```bash
#!/bin/bash
# save as: test_restore.sh

# Find latest backup
LATEST_BACKUP=$(ls -t /opt/appflowy-backups/appflowy_db_*.sql.gz | head -1)

echo "🧪 Testing restore from: $LATEST_BACKUP"

# Create test database
docker-compose exec -T postgres psql -U appflowy_user -c "CREATE DATABASE appflowy_test;"

# Restore to test database
gunzip < "$LATEST_BACKUP" | \
  docker-compose exec -T postgres psql -U appflowy_user appflowy_test

# Verify restoration
docker-compose exec -T postgres psql -U appflowy_user appflowy_test -c "\dt"

# Clean up
docker-compose exec -T postgres psql -U appflowy_user -c "DROP DATABASE appflowy_test;"

echo "✅ Backup restoration test passed"
```
</backup_restore>

---

## Container Management

<container_management>
**View Container Details:**

```bash
# List all containers
docker-compose ps

# Detailed container info
docker inspect appflowy | jq .

# Container resource limits
docker inspect appflowy | jq '.[0].HostConfig.Memory'
```

**Execute Commands in Containers:**

```bash
# Access AppFlowy container shell
docker-compose exec appflowy sh

# Access PostgreSQL container
docker-compose exec postgres bash

# Run one-off command
docker-compose exec appflowy env

# Run as specific user
docker-compose exec -u postgres postgres whoami
```

**View Container Logs:**

```bash
# All logs
docker-compose logs appflowy

# Follow logs (real-time)
docker-compose logs -f appflowy

# Last N lines
docker-compose logs --tail=50 appflowy

# Logs since timestamp
docker-compose logs --since="2025-12-04T10:00:00" appflowy

# Save logs
docker-compose logs appflowy > appflowy.log
```

**Clean Up Containers:**

```bash
# Remove stopped containers
docker-compose rm

# Remove all stopped containers (system-wide)
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes (⚠️ may delete data)
docker volume prune

# Complete cleanup (⚠️ removes everything unused)
docker system prune -a --volumes
```

**Update Container Configuration:**

```bash
# Edit docker-compose.yml
nano /opt/appflowy-cloud/docker-compose.yml

# Example: Add resource limits
services:
  appflowy:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Recreate containers with new config
docker-compose down
docker-compose up -d
```

**View Container Network:**

```bash
# List networks
docker network ls

# Inspect AppFlowy network
docker network inspect appflowy_default

# Test connectivity between containers
docker-compose exec appflowy ping postgres
```
</container_management>

---

## Auto-Start Configuration

<auto_start_config>
**Systemd Service (Linux):**

```bash
# Create systemd service
sudo nano /etc/systemd/system/appflowy.service
```

```ini
[Unit]
Description=AppFlowy Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/appflowy-cloud
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable appflowy.service
sudo systemctl start appflowy.service

# Check status
sudo systemctl status appflowy.service

# View logs
sudo journalctl -u appflowy.service -f
```

**Docker Compose Restart Policy:**

```yaml
# Edit docker-compose.yml
services:
  appflowy:
    restart: unless-stopped  # Auto-restart on boot
    # Options:
    # - no: Don't restart
    # - always: Always restart
    # - on-failure: Restart on error
    # - unless-stopped: Restart unless manually stopped

  postgres:
    restart: unless-stopped
```

**Synology NAS Auto-Start:**

**Method 1: Container Manager Settings**
1. Open Container Manager
2. Select AppFlowy containers
3. Settings → Enable "Auto-restart"
4. Click "Apply"

**Method 2: Task Scheduler**
```bash
# Create triggered task in Task Scheduler
# Trigger: Boot-up
# User: root
# Command:
docker-compose -f /volume1/docker/appflowy/docker-compose.yml up -d
```

**Verify Auto-Start:**

```bash
# Reboot system
sudo reboot

# After reboot, check if services started
docker-compose ps

# Check startup time
docker inspect appflowy | jq '.[0].State.StartedAt'
```

**Health Check with Auto-Restart:**

```yaml
# Add health check to docker-compose.yml
services:
  appflowy:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
```
</auto_start_config>

---

## Server Management Script

<management_script>
**Complete Management Script:**

```bash
#!/bin/bash
# save as: /opt/appflowy-cloud/manage_server.sh
# chmod +x /opt/appflowy-cloud/manage_server.sh

COMPOSE_FILE="/opt/appflowy-cloud/docker-compose.yml"
BACKUP_DIR="/opt/appflowy-backups"
API_URL="http://appflowy.arknode-ai.home"

case "$1" in
  start)
    echo "🚀 Starting AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" up -d
    echo "⏳ Waiting for server to be healthy..."
    sleep 10
    docker-compose -f "$COMPOSE_FILE" ps
    ;;

  stop)
    echo "🛑 Stopping AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" down
    ;;

  restart)
    echo "🔄 Restarting AppFlowy server..."
    docker-compose -f "$COMPOSE_FILE" restart
    ;;

  recreate)
    echo "🔄 Recreating AppFlowy containers (reloads .env)..."
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" up -d
    ;;

  status)
    echo "📊 AppFlowy server status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo -e "\n💾 Resource usage:"
    docker stats --no-stream appflowy appflowy-db
    ;;

  logs)
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
    ;;

  health)
    echo "🏥 Health check:"
    curl -s "$API_URL/health" | jq . || echo "❌ API not responding"
    echo -e "\nContainer health:"
    docker inspect appflowy | jq '.[0].State.Health.Status'
    ;;

  backup)
    mkdir -p "$BACKUP_DIR"
    DATE=$(date +%Y%m%d_%H%M%S)
    echo "💾 Backing up database..."
    docker-compose -f "$COMPOSE_FILE" exec -T postgres \
      pg_dump -U appflowy_user appflowy | \
      gzip > "${BACKUP_DIR}/appflowy_${DATE}.sql.gz"
    echo "✅ Backup saved: ${BACKUP_DIR}/appflowy_${DATE}.sql.gz"
    ;;

  restore)
    if [ -z "$2" ]; then
      echo "Usage: $0 restore <backup_file>"
      echo "Available backups:"
      ls -lh "$BACKUP_DIR"
      exit 1
    fi
    echo "🔄 Restoring from: $2"
    gunzip < "$2" | \
      docker-compose -f "$COMPOSE_FILE" exec -T postgres \
      psql -U appflowy_user appflowy
    echo "✅ Restore complete"
    ;;

  upgrade)
    echo "⬆️  Upgrading AppFlowy..."
    docker-compose -f "$COMPOSE_FILE" pull
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" up -d
    echo "✅ Upgrade complete"
    ;;

  clean)
    echo "🧹 Cleaning up Docker resources..."
    docker system prune -f
    echo "✅ Cleanup complete"
    ;;

  *)
    echo "AppFlowy Server Management"
    echo "=========================="
    echo "Usage: $0 {start|stop|restart|recreate|status|logs|health|backup|restore|upgrade|clean}"
    echo ""
    echo "Commands:"
    echo "  start     - Start AppFlowy services"
    echo "  stop      - Stop AppFlowy services"
    echo "  restart   - Restart containers (keeps config)"
    echo "  recreate  - Recreate containers (reloads .env)"
    echo "  status    - Show service status and resource usage"
    echo "  logs      - Follow service logs"
    echo "  health    - Run health checks"
    echo "  backup    - Backup database"
    echo "  restore   - Restore from backup"
    echo "  upgrade   - Pull and deploy latest images"
    echo "  clean     - Clean up Docker resources"
    exit 1
    ;;
esac
```

**Usage Examples:**

```bash
# Start server
./manage_server.sh start

# Check status
./manage_server.sh status

# View logs
./manage_server.sh logs

# Create backup
./manage_server.sh backup

# Restore backup
./manage_server.sh restore /opt/appflowy-backups/appflowy_20251204_120000.sql.gz

# Upgrade to latest version
./manage_server.sh upgrade

# Recreate containers after .env changes
./manage_server.sh recreate
```
</management_script>

---

## Upgrade Procedures

<upgrade_procedures>
**Check Current Version:**

```bash
# Check image version
docker-compose images appflowy

# Check container version
docker inspect appflowy | jq '.[0].Config.Image'
```

**Upgrade to Latest Version:**

```bash
# 1. Backup current installation
./manage_server.sh backup

# 2. Pull latest images
docker-compose pull

# 3. Stop current services
docker-compose down

# 4. Start with new images
docker-compose up -d

# 5. Verify upgrade
docker-compose ps
docker-compose logs -f appflowy

# 6. Test functionality
curl http://appflowy.arknode-ai.home/health
```

**Upgrade to Specific Version:**

```bash
# Edit docker-compose.yml
services:
  appflowy:
    image: appflowy/appflowy-cloud:v1.2.3  # Specify version

# Apply changes
docker-compose pull
docker-compose down
docker-compose up -d
```

**Rollback to Previous Version:**

```bash
# 1. Stop current version
docker-compose down

# 2. Restore from backup
gunzip < /opt/appflowy-backups/appflowy_20251204_120000.sql.gz | \
  docker-compose exec -T postgres psql -U appflowy_user appflowy

# 3. Edit docker-compose.yml to use previous image version
# 4. Start services
docker-compose up -d
```

**Zero-Downtime Upgrade (Advanced):**

```bash
# 1. Start new version on different port
# Edit docker-compose.yml, change port to 8081
docker-compose -f docker-compose-new.yml up -d

# 2. Test new version
curl http://localhost:8081/health

# 3. Switch Nginx proxy to new port
# Edit /etc/nginx/sites-available/appflowy
# proxy_pass http://localhost:8081;
sudo nginx -t && sudo systemctl reload nginx

# 4. Stop old version
docker-compose -f docker-compose-old.yml down
```
</upgrade_procedures>

---

## Related Documentation

- **Troubleshooting**: See `workflows/troubleshooting.md` for common issues
- **Setup Guide**: See `references/setup_guide.md` for deployment instructions
- **Task Management**: See `workflows/task-management.md` for API usage
- **Workspace Operations**: See `workflows/workspace-operations.md` for workspace management
