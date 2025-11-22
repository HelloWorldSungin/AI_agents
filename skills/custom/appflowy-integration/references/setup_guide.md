# AppFlowy Self-Hosted Setup Guide

Complete guide for deploying AppFlowy on various platforms.

## Table of Contents

1. [Quick Start with Docker](#quick-start-with-docker)
2. [Synology NAS Deployment](#synology-nas-deployment)
3. [AI Home Server Deployment](#ai-home-server-deployment)
4. [Configuration](#configuration)
5. [Authentication Setup](#authentication-setup)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start with Docker

### Prerequisites
- Docker installed
- Docker Compose installed
- 2GB RAM minimum
- 10GB disk space

### Basic Deployment

```bash
# Create deployment directory
mkdir -p ~/appflowy-deploy
cd ~/appflowy-deploy

# Copy docker-compose.yml from references/
cp /path/to/skills/custom/appflowy-integration/references/docker-compose.yml .

# Create .env file
cat > .env <<EOF
DB_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f appflowy
```

### Access AppFlowy

- Web Interface: http://localhost:8080
- API Endpoint: http://localhost:8080/api

---

## Synology NAS Deployment

### Method 1: Container Manager (GUI)

1. **Open Container Manager**
   - Launch Container Manager from Package Center
   - Go to "Registry" tab

2. **Download AppFlowy Image**
   - Search for "appflowy"
   - Download `appflowy/appflowy-cloud:latest`

3. **Create PostgreSQL Container**
   - Search and download `postgres:15-alpine`
   - Create container with settings:
     - Container Name: `appflowy-db`
     - Port: `5432:5432`
     - Environment Variables:
       ```
       POSTGRES_DB=appflowy
       POSTGRES_USER=appflowy_user
       POSTGRES_PASSWORD=your_secure_password
       ```
     - Volume: `/volume1/docker/appflowy-db:/var/lib/postgresql/data`

4. **Create AppFlowy Container**
   - Create container from downloaded image
   - Container settings:
     - Container Name: `appflowy`
     - Port: `8080:80`
     - Environment Variables:
       ```
       DATABASE_URL=postgresql://appflowy_user:your_secure_password@appflowy-db:5432/appflowy
       APP_ENV=production
       ```
     - Volume: `/volume1/docker/appflowy:/data`
     - Links: Link to `appflowy-db` container

5. **Start Containers**
   - Start PostgreSQL container first
   - Then start AppFlowy container

### Method 2: SSH + Docker Compose

```bash
# SSH into Synology
ssh admin@nas-ip

# Create directory
mkdir -p /volume1/docker/appflowy
cd /volume1/docker/appflowy

# Copy docker-compose.yml
# (use WinSCP, FileStation, or create manually)

# Start with docker-compose
sudo docker-compose up -d

# Check status
sudo docker-compose ps
```

### Network Configuration

1. **Internal Access**
   - URL: `http://nas-ip:8080`
   - Use within local network

2. **External Access (Optional)**
   - Control Panel → Application Portal
   - Create reverse proxy:
     - Source: `appflowy.yourdomain.com` (port 443)
     - Destination: `localhost` (port 8080)
   - Set up SSL certificate
   - Configure DDNS if needed

### Firewall Configuration

1. Control Panel → Security → Firewall
2. Create rule allowing port 8080
3. Apply to appropriate network interface

---

## AI Home Server Deployment

### Ubuntu/Debian Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Create deployment directory
mkdir -p ~/appflowy
cd ~/appflowy

# Create docker-compose.yml and .env
# (copy from references/)

# Start services
docker compose up -d

# Enable autostart on reboot
docker compose restart unless-stopped
```

### NVIDIA Jetson / ARM Devices

```bash
# Same as above, but use ARM-compatible images
# Modify docker-compose.yml:

services:
  appflowy:
    image: appflowy/appflowy-cloud:latest
    platform: linux/arm64  # Add this line

  postgres:
    image: postgres:15-alpine
    platform: linux/arm64  # Add this line
```

### Reverse Proxy Setup (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/appflowy
```

```nginx
server {
    listen 80;
    server_name appflowy.local;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/appflowy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Configuration

### Environment Variables

Create `.env` file in deployment directory:

```bash
# Database
DB_PASSWORD=your_secure_database_password
POSTGRES_USER=appflowy_user
POSTGRES_DB=appflowy

# Authentication
JWT_SECRET=your_jwt_secret_32_chars_minimum
JWT_EXPIRY=3600

# Application
APP_ENV=production
LOG_LEVEL=info

# Optional: Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### Generate Secure Secrets

```bash
# Database password
openssl rand -hex 16

# JWT secret
openssl rand -hex 32
```

---

## Authentication Setup

### 1. Create Admin Account

```bash
# Access AppFlowy container
docker exec -it appflowy sh

# Run admin creation script (if available)
# Or use API to create user
```

### 2. Get JWT Token via API

```bash
# Create user and get token
curl -X POST "http://localhost:8080/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password",
    "grant_type": "password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": {...}
}
```

### 3. Configure Agent Environment

```bash
# Add to agent environment
export APPFLOWY_API_URL="http://localhost:8080"
export APPFLOWY_API_TOKEN="eyJhbGc..."
export APPFLOWY_WORKSPACE_ID="workspace-id"
```

### 4. Get Workspace ID

```bash
# List workspaces
curl -X GET "http://localhost:8080/api/workspace" \
  -H "Authorization: Bearer your_token"
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs appflowy

# Common issues:
# 1. Database not ready - wait 30 seconds and retry
# 2. Port already in use - change port in docker-compose.yml
# 3. Missing environment variables - check .env file
```

### Cannot Connect to Database

```bash
# Test database connection
docker exec -it appflowy-db psql -U appflowy_user -d appflowy

# If fails:
# 1. Check DATABASE_URL format
# 2. Verify postgres container is running
# 3. Check network connectivity between containers
```

### API Returns 401 Unauthorized

```bash
# Token may be expired - get new token
curl -X POST "http://localhost:8080/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password",
    "grant_type": "password"
  }'

# Or use refresh token
curl -X POST "http://localhost:8080/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token",
    "grant_type": "refresh_token"
  }'
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase container resources (if needed)
# Edit docker-compose.yml:
services:
  appflowy:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Data Persistence Issues

```bash
# Check volumes
docker volume ls

# Inspect volume
docker volume inspect appflowy_postgres-data

# Backup data
docker-compose exec postgres pg_dump -U appflowy_user appflowy > backup.sql

# Restore data
docker-compose exec -T postgres psql -U appflowy_user appflowy < backup.sql
```

---

## Maintenance

### Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# Backup database
docker-compose exec -T postgres pg_dump -U appflowy_user appflowy \
  | gzip > "${BACKUP_DIR}/appflowy_db_${DATE}.sql.gz"

# Backup volumes
docker-compose stop
tar -czf "${BACKUP_DIR}/appflowy_data_${DATE}.tar.gz" \
  -C /var/lib/docker/volumes appflowy_appflowy-data
docker-compose start
```

### Update AppFlowy

```bash
# Pull latest image
docker-compose pull

# Restart with new image
docker-compose down
docker-compose up -d

# Check version
docker-compose exec appflowy cat /app/version
```

### Monitor Logs

```bash
# Follow logs
docker-compose logs -f --tail=100

# Specific service
docker-compose logs -f appflowy

# Save logs to file
docker-compose logs > appflowy_logs_$(date +%Y%m%d).txt
```

---

## Security Best Practices

1. **Change Default Passwords**
   - Set strong database password
   - Use secure JWT secret

2. **Use HTTPS**
   - Set up reverse proxy with SSL
   - Use Let's Encrypt for certificates

3. **Firewall Rules**
   - Only expose necessary ports
   - Use VPN for external access

4. **Regular Updates**
   - Update Docker images weekly
   - Monitor security advisories

5. **Backup Regularly**
   - Daily database backups
   - Weekly full backups
   - Test restore procedures

---

## Resources

- [AppFlowy Documentation](https://docs.appflowy.io)
- [Docker Documentation](https://docs.docker.com)
- [Synology Docker Guide](https://kb.synology.com/en-global/DSM/help/Docker/docker)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
