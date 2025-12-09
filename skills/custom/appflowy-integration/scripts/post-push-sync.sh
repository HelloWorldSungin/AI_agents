#!/bin/bash
################################################################################
# AppFlowy Post-Push Sync Script
#
# Automatically syncs tasks and documentation to AppFlowy after git push.
# This script is designed to be triggered via a git alias or shell alias.
#
# Usage:
#   ./post-push-sync.sh
#
# Requirements:
#   - .env file with AppFlowy credentials
#   - Python 3 with required dependencies
#   - sync_tasks.py and sync_docs.py in same directory
################################################################################

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env"
REPO_ROOT="/Users/sunginkim/GIT/AI_agents"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         AppFlowy Post-Push Sync${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the right directory
if [ "$PWD" != "$REPO_ROOT" ]; then
    echo -e "${YELLOW}⚠️  Warning: Not in repository root${NC}"
    echo -e "   Current: $PWD"
    echo -e "   Expected: $REPO_ROOT"
    echo ""
fi

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "   Expected: $ENV_FILE"
    echo ""
    exit 1
fi

# Check if sync scripts exist
if [ ! -f "$SCRIPT_DIR/sync_tasks.py" ]; then
    echo -e "${RED}❌ Error: sync_tasks.py not found${NC}"
    echo -e "   Expected: $SCRIPT_DIR/sync_tasks.py"
    echo ""
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/sync_docs.py" ]; then
    echo -e "${RED}❌ Error: sync_docs.py not found${NC}"
    echo -e "   Expected: $SCRIPT_DIR/sync_docs.py"
    echo ""
    exit 1
fi

# Load environment variables
echo -e "${BLUE}📋 Loading environment from .env...${NC}"
set -a
source "$ENV_FILE"
set +a

# Export workspace IDs for AI_agents
export APPFLOWY_WORKSPACE_ID="c9674d81-6037-4dc3-9aa6-e2d833162b0f"
export APPFLOWY_DATABASE_ID="6f9c57aa-dda0-4aac-ba27-54544d85270e"

echo -e "${GREEN}✅ Environment loaded${NC}"
echo ""

# Sync tasks
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 Syncing Tasks to AppFlowy...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

cd "$SCRIPT_DIR"
if python3 sync_tasks.py --env-file "$ENV_FILE"; then
    echo ""
    echo -e "${GREEN}✅ Tasks synced successfully${NC}"
    TASKS_SUCCESS=true
else
    echo ""
    echo -e "${RED}❌ Task sync failed${NC}"
    TASKS_SUCCESS=false
fi

echo ""

# Sync documentation
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📄 Syncing Documentation to AppFlowy...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if python3 sync_docs.py --env-file "$ENV_FILE"; then
    echo ""
    echo -e "${GREEN}✅ Documentation synced successfully${NC}"
    DOCS_SUCCESS=true
else
    echo ""
    echo -e "${RED}❌ Documentation sync failed${NC}"
    DOCS_SUCCESS=false
fi

echo ""

# Print summary
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         Sync Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$TASKS_SUCCESS" = true ]; then
    echo -e "  📋 Tasks:         ${GREEN}✅ Success${NC}"
else
    echo -e "  📋 Tasks:         ${RED}❌ Failed${NC}"
fi

if [ "$DOCS_SUCCESS" = true ]; then
    echo -e "  📄 Documentation: ${GREEN}✅ Success${NC}"
else
    echo -e "  📄 Documentation: ${RED}❌ Failed${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Return appropriate exit code
if [ "$TASKS_SUCCESS" = true ] && [ "$DOCS_SUCCESS" = true ]; then
    echo -e "${GREEN}🎉 All syncs completed successfully!${NC}"
    echo ""
    exit 0
elif [ "$TASKS_SUCCESS" = true ] || [ "$DOCS_SUCCESS" = true ]; then
    echo -e "${YELLOW}⚠️  Some syncs completed with errors${NC}"
    echo ""
    exit 1
else
    echo -e "${RED}❌ All syncs failed${NC}"
    echo ""
    exit 1
fi
