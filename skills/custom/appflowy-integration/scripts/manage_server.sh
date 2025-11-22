#!/bin/bash
#
# AppFlowy Server Management Script
#
# Manages self-hosted AppFlowy instance with Docker Compose
#
# Usage:
#   ./manage_server.sh start    - Start the server
#   ./manage_server.sh stop     - Stop the server
#   ./manage_server.sh restart  - Restart the server
#   ./manage_server.sh status   - Show server status
#   ./manage_server.sh logs     - Follow server logs
#   ./manage_server.sh health   - Check server health
#   ./manage_server.sh backup   - Backup database

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$SCRIPT_DIR/../references/docker-compose.yml}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/appflowy-backups}"
API_URL="${APPFLOWY_API_URL:-http://localhost:8080}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        echo "Please set COMPOSE_FILE environment variable or use default location"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
}

# Get docker-compose command (handle both standalone and plugin)
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose -f $COMPOSE_FILE"
    else
        echo "docker compose -f $COMPOSE_FILE"
    fi
}

# Commands
cmd_start() {
    info "Starting AppFlowy server..."
    check_docker
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)

    # Start services
    $COMPOSE_CMD up -d

    info "Waiting for services to be healthy..."
    sleep 5

    # Check status
    $COMPOSE_CMD ps

    # Test API
    echo ""
    if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
        success "AppFlowy server is running at $API_URL"
    else
        warning "Server started but health check failed"
        warning "It may take a few more seconds to initialize"
    fi
}

cmd_stop() {
    info "Stopping AppFlowy server..."
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD down

    success "AppFlowy server stopped"
}

cmd_restart() {
    info "Restarting AppFlowy server..."
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD restart

    info "Waiting for services to restart..."
    sleep 5

    $COMPOSE_CMD ps
    success "AppFlowy server restarted"
}

cmd_status() {
    info "AppFlowy Server Status"
    echo ""
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)

    # Container status
    echo "📦 Containers:"
    $COMPOSE_CMD ps

    echo ""
    echo "💾 Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(docker ps --filter "name=appflowy" --format "{{.Names}}") 2>/dev/null || \
        warning "No AppFlowy containers running"

    # Health check
    echo ""
    echo "🏥 Health Check:"
    if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
        success "API is responding at $API_URL"
    else
        error "API is not responding at $API_URL"
    fi
}

cmd_logs() {
    info "Following AppFlowy logs (Ctrl+C to stop)..."
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD logs -f --tail=100
}

cmd_health() {
    info "Running health checks..."

    echo ""
    echo "🔌 Network connectivity:"
    if ping -c 1 localhost > /dev/null 2>&1; then
        success "localhost is reachable"
    else
        error "Cannot reach localhost"
    fi

    echo ""
    echo "🐳 Docker service:"
    if systemctl is-active --quiet docker 2>/dev/null || \
       docker info > /dev/null 2>&1; then
        success "Docker is running"
    else
        error "Docker is not running"
    fi

    echo ""
    echo "📦 Containers:"
    COMPOSE_CMD=$(get_compose_cmd)
    if $COMPOSE_CMD ps | grep -q "Up"; then
        success "AppFlowy containers are running"
        $COMPOSE_CMD ps
    else
        error "AppFlowy containers are not running"
    fi

    echo ""
    echo "🌐 API endpoint:"
    if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
        success "API is healthy at $API_URL"
        curl -s "$API_URL/health" | jq . 2>/dev/null || echo ""
    else
        error "API health check failed"
        warning "Trying to get more info..."
        curl -v "$API_URL/health" 2>&1 | grep -E "Connected|HTTP" || true
    fi

    echo ""
    echo "🔍 Port availability:"
    if netstat -tuln 2>/dev/null | grep -q ":8080" || \
       lsof -i :8080 > /dev/null 2>&1; then
        success "Port 8080 is in use (expected)"
    else
        warning "Port 8080 is not in use"
    fi
}

cmd_backup() {
    info "Backing up AppFlowy database..."
    check_compose_file

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Generate backup filename
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/appflowy_backup_${DATE}.sql.gz"

    COMPOSE_CMD=$(get_compose_cmd)

    # Backup database
    info "Dumping PostgreSQL database..."
    $COMPOSE_CMD exec -T postgres pg_dump -U appflowy_user appflowy | \
        gzip > "$BACKUP_FILE"

    if [ -f "$BACKUP_FILE" ]; then
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        success "Backup saved: $BACKUP_FILE ($SIZE)"

        # Show recent backups
        echo ""
        info "Recent backups:"
        ls -lht "$BACKUP_DIR" | head -6
    else
        error "Backup failed"
        exit 1
    fi
}

cmd_restore() {
    BACKUP_FILE="$1"

    if [ -z "$BACKUP_FILE" ]; then
        error "Please specify backup file"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    warning "This will restore the database from backup"
    warning "Current data will be replaced!"
    read -p "Are you sure? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        info "Restore cancelled"
        exit 0
    fi

    info "Restoring from: $BACKUP_FILE"
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)

    # Restore database
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        gunzip -c "$BACKUP_FILE" | $COMPOSE_CMD exec -T postgres \
            psql -U appflowy_user appflowy
    else
        $COMPOSE_CMD exec -T postgres psql -U appflowy_user appflowy < "$BACKUP_FILE"
    fi

    success "Database restored successfully"
    info "Restarting server..."
    cmd_restart
}

cmd_update() {
    info "Updating AppFlowy to latest version..."
    check_compose_file

    COMPOSE_CMD=$(get_compose_cmd)

    # Create backup first
    warning "Creating backup before update..."
    cmd_backup

    # Pull latest images
    info "Pulling latest images..."
    $COMPOSE_CMD pull

    # Restart with new images
    info "Restarting with new images..."
    $COMPOSE_CMD down
    $COMPOSE_CMD up -d

    info "Waiting for services to start..."
    sleep 10

    $COMPOSE_CMD ps
    success "Update complete"
}

# Main command handler
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs
        ;;
    health)
        cmd_health
        ;;
    backup)
        cmd_backup
        ;;
    restore)
        cmd_restore "$2"
        ;;
    update)
        cmd_update
        ;;
    *)
        echo "AppFlowy Server Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|health|backup|restore|update}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the AppFlowy server"
        echo "  stop     - Stop the AppFlowy server"
        echo "  restart  - Restart the AppFlowy server"
        echo "  status   - Show server status and resource usage"
        echo "  logs     - Follow server logs"
        echo "  health   - Run comprehensive health checks"
        echo "  backup   - Backup database to $BACKUP_DIR"
        echo "  restore  - Restore database from backup file"
        echo "  update   - Update to latest AppFlowy version"
        echo ""
        echo "Environment Variables:"
        echo "  COMPOSE_FILE   - Path to docker-compose.yml (default: ../references/docker-compose.yml)"
        echo "  BACKUP_DIR     - Backup directory (default: ~/appflowy-backups)"
        echo "  APPFLOWY_API_URL - API URL (default: http://localhost:8080)"
        exit 1
        ;;
esac
