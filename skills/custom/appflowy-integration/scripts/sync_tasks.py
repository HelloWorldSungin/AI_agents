#!/usr/bin/env python3
"""
AppFlowy Task Sync Script

Syncs AI_agents tasks from various sources to AppFlowy Kanban board.
Supports incremental updates by tracking sync status in a local JSON file.

Usage:
    python sync_tasks.py [--dry-run] [--force] [--env-file PATH]

Options:
    --dry-run    Show what would be synced without making changes
    --force      Force re-sync all tasks, ignoring sync status
    --env-file   Path to .env file (default: auto-detect)

Environment Variables:
    APPFLOWY_API_URL        AppFlowy API base URL
    APPFLOWY_API_TOKEN      JWT authentication token
    APPFLOWY_WORKSPACE_ID   Target workspace ID
    APPFLOWY_DATABASE_ID    Tasks database ID (To-dos)

Data Sources:
    - .ai-agents/state/team-communication.json - Active task coordination
    - .ai-agents/state/feature-tracking.json - Feature status (if exists)
    - .planning/ROADMAP.md - Planned phases (parse for tasks)
    - whats-next.md - Session handoffs and pending items (if exists)

Author: AI Agents Team
Version: 1.0.0
"""

import os
import sys
import json
import argparse
import logging
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import requests
from requests.exceptions import RequestException, HTTPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AppFlowyAPIError(Exception):
    """Base exception for AppFlowy API errors."""
    pass


class AppFlowyAuthError(AppFlowyAPIError):
    """Authentication error."""
    pass


class AppFlowyNotFoundError(AppFlowyAPIError):
    """Resource not found."""
    pass


class AppFlowyClient:
    """Simple AppFlowy REST API client for task sync."""

    # Field ID mappings for the Project Management database
    FIELD_IDS = {
        'description': 'CdYtwn',  # Primary field (RichText)
        'status': 'x2ab-u',        # SingleSelect
    }

    # Status value mappings (status name -> option ID)
    STATUS_VALUES = {
        'To Do': 'I6i3',
        'Todo': 'I6i3',
        'Backlog': 'I6i3',
        'Doing': '72Je',
        'In Progress': '72Je',
        'Blocked': '72Je',  # Map to "Doing" since no blocked status
        'Review': '72Je',   # Map to "Doing"
        '✅ Done': '5roz',
        'Done': '5roz',
        'Completed': '5roz'
    }

    def __init__(self, api_url: str, token: str, workspace_id: str, database_id: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.workspace_id = workspace_id
        self.database_id = database_id
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated API request."""
        url = f"{self.api_url}{endpoint}"
        kwargs['headers'] = self.headers

        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except HTTPError as e:
            if e.response.status_code == 401:
                raise AppFlowyAuthError("Authentication failed - check API token")
            elif e.response.status_code == 403:
                raise AppFlowyAuthError("Permission denied - check workspace access")
            elif e.response.status_code == 404:
                raise AppFlowyNotFoundError(f"Resource not found: {endpoint}")
            else:
                raise AppFlowyAPIError(f"API error {e.response.status_code}: {e.response.text}")
        except RequestException as e:
            raise AppFlowyAPIError(f"Failed to connect to AppFlowy: {e}")

    def list_workspaces(self) -> List[dict]:
        """List all accessible workspaces."""
        return self._make_request('GET', '/api/workspace')

    def get_database_rows(self) -> List[dict]:
        """Get all row IDs from database."""
        return self._make_request('GET', f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row')

    def get_row_detail(self, row_ids: List[str]) -> List[dict]:
        """Get detailed information for specific rows."""
        if not row_ids:
            return []
        params = {'row_ids': ','.join(row_ids)}
        return self._make_request(
            'GET',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row/detail',
            params=params
        )

    def _prepare_cells_payload(self, task_data: dict) -> dict:
        """
        Convert task data to AppFlowy cells format.

        Args:
            task_data: Dict with keys like 'Title', 'Status', 'Notes', etc.

        Returns:
            Dict with 'cells' key containing field_id: value mappings
        """
        cells = {}

        # Map Title to Description field (primary)
        # Include metadata in the title since we only have Description and Status fields
        title_parts = []
        if 'Title' in task_data:
            title_parts.append(task_data['Title'])

        # Add metadata to title for better visibility
        metadata = []
        if 'Priority' in task_data and task_data['Priority']:
            metadata.append(f"[{task_data['Priority']}]")
        if 'Category' in task_data and task_data['Category']:
            metadata.append(f"({task_data['Category']})")
        if 'Source' in task_data and task_data['Source']:
            metadata.append(f"<{task_data['Source']}>")

        if metadata:
            title_parts.append(' '.join(metadata))

        if 'Notes' in task_data and task_data['Notes']:
            title_parts.append(f"\n{task_data['Notes']}")

        cells[self.FIELD_IDS['description']] = ' '.join(title_parts) if title_parts else 'Untitled'

        # Map Status to status field with proper option ID
        if 'Status' in task_data:
            status_name = task_data['Status']
            status_id = self.STATUS_VALUES.get(status_name, 'I6i3')  # Default to "To Do"
            cells[self.FIELD_IDS['status']] = status_id

        return {'cells': cells}

    def create_row(self, data: dict) -> dict:
        """
        Create a new task row in the database.

        Args:
            data: Task data dict with keys like 'Title', 'Status', 'Notes', etc.

        Returns:
            API response with created row ID
        """
        payload = self._prepare_cells_payload(data)
        result = self._make_request(
            'POST',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row',
            json=payload
        )
        # Return in expected format with 'id' key
        if 'data' in result:
            return {'id': result['data']}
        return result

    def update_row(self, row_id: str, updates: dict) -> dict:
        """
        Update an existing task row.

        Args:
            row_id: The row ID to update
            updates: Task data dict with keys like 'Title', 'Status', 'Notes', etc.

        Returns:
            API response
        """
        payload = self._prepare_cells_payload(updates)
        payload['row_id'] = row_id
        return self._make_request(
            'PUT',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row',
            json=payload
        )


class TaskSyncManager:
    """Manages task sync to AppFlowy Kanban board."""

    # Repository root (working directory)
    REPO_ROOT = Path('/Users/sunginkim/GIT/AI_agents')

    # Sync status file
    SYNC_STATUS_FILE = REPO_ROOT / 'skills/custom/appflowy-integration/.task-sync-status.json'

    # Data source files
    DATA_SOURCES = {
        'team_communication': REPO_ROOT / '.ai-agents/state/team-communication.json',
        'feature_tracking': REPO_ROOT / '.ai-agents/state/feature-tracking.json',
        'roadmap': REPO_ROOT / '.planning/ROADMAP.md',
        'whats_next': REPO_ROOT / 'whats-next.md',
    }

    # Status mapping: source status -> AppFlowy status
    STATUS_MAP = {
        'pending': 'Backlog',
        'in_progress': 'In Progress',
        'blocked': 'Blocked',
        'completed': 'Done',
        'todo': 'Todo',
        'review': 'Review',
        'not started': 'Backlog',
        'done': 'Done',
    }

    # Priority mapping
    PRIORITY_MAP = {
        'critical': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low',
    }

    def __init__(self, client: AppFlowyClient, dry_run: bool = False, force: bool = False):
        self.client = client
        self.dry_run = dry_run
        self.force = force
        self.sync_status = self._load_sync_status()
        self.tasks_to_sync: List[Dict[str, Any]] = []

    def _load_sync_status(self) -> dict:
        """Load sync status from JSON file."""
        if self.SYNC_STATUS_FILE.exists():
            try:
                with open(self.SYNC_STATUS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load sync status: {e}")
        return {
            'last_sync': None,
            'synced_tasks': {},
            'task_hashes': {}
        }

    def _save_sync_status(self):
        """Save sync status to JSON file."""
        if self.dry_run:
            logger.info("DRY RUN: Would save sync status")
            return

        try:
            self.SYNC_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.SYNC_STATUS_FILE, 'w') as f:
                json.dump(self.sync_status, f, indent=2)
            logger.info(f"Sync status saved to {self.SYNC_STATUS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save sync status: {e}")

    def _compute_task_hash(self, task_data: dict) -> str:
        """Compute hash of task data for change detection."""
        # Create a stable representation of the task
        stable_repr = json.dumps(task_data, sort_keys=True)
        return hashlib.md5(stable_repr.encode()).hexdigest()

    def _normalize_status(self, status: str) -> str:
        """Normalize status value to AppFlowy status."""
        status_lower = status.lower().strip()
        return self.STATUS_MAP.get(status_lower, 'Backlog')

    def _normalize_priority(self, priority: str) -> str:
        """Normalize priority value."""
        if not priority:
            return 'Medium'
        priority_lower = priority.lower().strip()
        return self.PRIORITY_MAP.get(priority_lower, 'Medium')

    def _extract_tasks_from_team_communication(self) -> List[Dict[str, Any]]:
        """Extract tasks from team-communication.json."""
        tasks = []
        file_path = self.DATA_SOURCES['team_communication']

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return tasks

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Extract active tasks
            for task in data.get('manager_instructions', {}).get('active_tasks', []):
                tasks.append({
                    'title': task.get('name', 'Untitled Task'),
                    'status': self._normalize_status(task.get('status', 'pending')),
                    'priority': self._normalize_priority(task.get('priority', 'medium')),
                    'category': 'Feature',
                    'source': 'team-communication.json',
                    'notes': f"Task ID: {task.get('id', 'N/A')}\nAgent: {task.get('agent', 'Unassigned')}",
                })

            # Extract completed tasks (optional, for tracking)
            for task in data.get('manager_instructions', {}).get('completed_tasks', [])[:5]:  # Last 5 completed
                tasks.append({
                    'title': task.get('name', 'Untitled Task'),
                    'status': 'Done',
                    'priority': self._normalize_priority(task.get('priority', 'medium')),
                    'category': 'Feature',
                    'source': 'team-communication.json',
                    'notes': f"Task ID: {task.get('id', 'N/A')}\nAgent: {task.get('agent', 'Completed')}",
                })

            # Extract blocked tasks
            for task in data.get('manager_instructions', {}).get('blocked_tasks', []):
                tasks.append({
                    'title': task.get('name', 'Untitled Task'),
                    'status': 'Blocked',
                    'priority': 'High',
                    'category': 'Feature',
                    'source': 'team-communication.json',
                    'notes': f"Task ID: {task.get('id', 'N/A')}\nBlocker: {task.get('blocker', 'Unknown')}",
                })

            logger.info(f"Extracted {len(tasks)} tasks from team-communication.json")

        except Exception as e:
            logger.error(f"Failed to parse team-communication.json: {e}")

        return tasks

    def _extract_tasks_from_feature_tracking(self) -> List[Dict[str, Any]]:
        """Extract tasks from feature-tracking.json (if exists)."""
        tasks = []
        file_path = self.DATA_SOURCES['feature_tracking']

        if not file_path.exists():
            logger.info("feature-tracking.json not found (optional)")
            return tasks

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Extract features as tasks
            for feature in data.get('features', []):
                tasks.append({
                    'title': feature.get('name', 'Untitled Feature'),
                    'status': self._normalize_status(feature.get('status', 'pending')),
                    'priority': self._normalize_priority(feature.get('priority', 'medium')),
                    'category': 'Feature',
                    'source': 'feature-tracking.json',
                    'notes': f"Feature: {feature.get('description', 'No description')}",
                })

            logger.info(f"Extracted {len(tasks)} tasks from feature-tracking.json")

        except Exception as e:
            logger.error(f"Failed to parse feature-tracking.json: {e}")

        return tasks

    def _extract_tasks_from_roadmap(self) -> List[Dict[str, Any]]:
        """Extract tasks from ROADMAP.md."""
        tasks = []
        file_path = self.DATA_SOURCES['roadmap']

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return tasks

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract phases (### Phase XX: Title)
            phase_pattern = r'###\s+Phase\s+(\d+):\s+(.+)'
            phases = re.findall(phase_pattern, content)

            for phase_num, phase_title in phases:
                # Determine status based on roadmap structure
                status = 'Backlog'  # Default for planned phases

                tasks.append({
                    'title': f"Phase {phase_num}: {phase_title}",
                    'status': status,
                    'priority': 'Medium',
                    'category': 'Infrastructure',
                    'source': 'ROADMAP.md',
                    'notes': f"Phase {phase_num} from project roadmap",
                })

            logger.info(f"Extracted {len(tasks)} tasks from ROADMAP.md")

        except Exception as e:
            logger.error(f"Failed to parse ROADMAP.md: {e}")

        return tasks

    def _extract_tasks_from_whats_next(self) -> List[Dict[str, Any]]:
        """Extract tasks from whats-next.md session handoff."""
        tasks = []
        file_path = self.DATA_SOURCES['whats_next']

        if not file_path.exists():
            logger.info("whats-next.md not found (optional)")
            return tasks

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract "Next Steps" or "What's Next" sections
            next_steps_pattern = r'##\s+(?:Next Steps|What\'s Next|Pending Items)[^\n]*\n((?:(?!##).*\n)*)'
            matches = re.findall(next_steps_pattern, content, re.MULTILINE)

            for match in matches:
                # Extract individual items (lines starting with -, *, or numbers)
                items = re.findall(r'^\s*[-*\d.]+\s+(.+)$', match, re.MULTILINE)
                for item in items:
                    tasks.append({
                        'title': item.strip(),
                        'status': 'Todo',
                        'priority': 'High',  # Items in handoff are usually important
                        'category': 'Documentation',
                        'source': 'whats-next.md',
                        'notes': 'From session handoff',
                    })

            logger.info(f"Extracted {len(tasks)} tasks from whats-next.md")

        except Exception as e:
            logger.error(f"Failed to parse whats-next.md: {e}")

        return tasks

    def collect_tasks(self) -> List[Dict[str, Any]]:
        """Collect tasks from all data sources."""
        all_tasks = []

        # Collect from each source
        all_tasks.extend(self._extract_tasks_from_team_communication())
        all_tasks.extend(self._extract_tasks_from_feature_tracking())
        all_tasks.extend(self._extract_tasks_from_roadmap())
        all_tasks.extend(self._extract_tasks_from_whats_next())

        # Deduplicate based on title (simple deduplication)
        seen_titles = set()
        unique_tasks = []
        for task in all_tasks:
            title_key = task['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_tasks.append(task)

        logger.info(f"Collected {len(unique_tasks)} unique tasks from {len(all_tasks)} total")
        return unique_tasks

    def _needs_sync(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if task needs to be synced."""
        if self.force:
            return True, "force sync requested"

        task_key = f"{task['source']}:{task['title']}"
        task_hash = self._compute_task_hash(task)

        if task_key not in self.sync_status['task_hashes']:
            return True, "never synced"

        last_hash = self.sync_status['task_hashes'][task_key]
        if last_hash != task_hash:
            return True, "task data changed"

        return False, "up to date"

    def _sync_task(self, task: Dict[str, Any]) -> bool:
        """Sync a single task to AppFlowy."""
        needs_sync, reason = self._needs_sync(task)

        if not needs_sync:
            logger.info(f"⏭️  Skipping '{task['title'][:50]}...' - {reason}")
            return True

        logger.info(f"📋 Syncing '{task['title'][:50]}...' ({reason})")

        # Prepare task data for AppFlowy
        task_data = {
            'Title': task['title'],
            'Status': task['status'],
            'Priority': task['priority'],
            'Category': task['category'],
            'Source': task['source'],
            'Notes': task.get('notes', ''),
        }

        # Create or update task
        if self.dry_run:
            logger.info(f"DRY RUN: Would sync task '{task['title'][:50]}...'")
            logger.info(f"         Status: {task['status']}, Priority: {task['priority']}")
            success = True
            row_id = f"dry-run-task-{task['title'][:20]}"
        else:
            try:
                # Check if task already exists
                task_key = f"{task['source']}:{task['title']}"
                if task_key in self.sync_status['synced_tasks']:
                    row_id = self.sync_status['synced_tasks'][task_key]
                    # Update existing task
                    result = self.client.update_row(row_id, task_data)
                    logger.info(f"✅ Updated task '{task['title'][:50]}...'")
                else:
                    # Create new task
                    result = self.client.create_row(task_data)
                    row_id = result.get('id')
                    logger.info(f"✅ Created task '{task['title'][:50]}...' (ID: {row_id})")

                success = True
            except AppFlowyAPIError as e:
                logger.error(f"❌ Failed to sync task '{task['title'][:50]}...': {e}")
                return False

        # Update sync status
        task_key = f"{task['source']}:{task['title']}"
        self.sync_status['synced_tasks'][task_key] = row_id
        self.sync_status['task_hashes'][task_key] = self._compute_task_hash(task)

        return success

    def sync_all(self) -> Tuple[int, int, int]:
        """
        Sync all tasks.

        Returns:
            Tuple of (synced, skipped, failed) counts
        """
        logger.info("=" * 60)
        logger.info("AppFlowy Task Sync")
        logger.info("=" * 60)
        logger.info(f"Repository: {self.REPO_ROOT}")
        logger.info(f"Workspace ID: {self.client.workspace_id}")
        logger.info(f"Database ID: {self.client.database_id}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}")
        if self.force:
            logger.info("Force sync: YES")
        logger.info("=" * 60)

        # Collect tasks from all sources
        tasks = self.collect_tasks()
        logger.info(f"Total tasks to process: {len(tasks)}")
        logger.info("=" * 60)

        synced = 0
        skipped = 0
        failed = 0

        for task in tasks:
            try:
                success = self._sync_task(task)

                if success:
                    # Check if actually synced or skipped
                    needs_sync, _ = self._needs_sync(task)
                    if needs_sync or self.force:
                        synced += 1
                    else:
                        skipped += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"❌ Unexpected error syncing task '{task['title'][:50]}...': {e}")
                failed += 1

        # Update last sync time
        self.sync_status['last_sync'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Save sync status
        self._save_sync_status()

        # Print summary
        logger.info("=" * 60)
        logger.info("Sync Summary")
        logger.info("=" * 60)
        logger.info(f"✅ Synced:  {synced}")
        logger.info(f"⏭️  Skipped: {skipped}")
        logger.info(f"❌ Failed:  {failed}")
        logger.info(f"📊 Total:   {synced + skipped + failed}")
        logger.info("=" * 60)

        return synced, skipped, failed


def load_env_file(env_file: Optional[Path] = None) -> Dict[str, str]:
    """
    Load environment variables from .env file.

    Uses python-dotenv if available, otherwise manual parsing.
    """
    if env_file is None:
        # Auto-detect .env file
        env_file = Path('/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env')

    # Override with AI Agents workspace IDs if not explicitly set
    if 'APPFLOWY_WORKSPACE_ID' not in os.environ:
        os.environ['APPFLOWY_WORKSPACE_ID'] = 'c9674d81-6037-4dc3-9aa6-e2d833162b0f'
    if 'APPFLOWY_DATABASE_ID' not in os.environ:
        os.environ['APPFLOWY_DATABASE_ID'] = '6f9c57aa-dda0-4aac-ba27-54544d85270e'

    if not env_file.exists():
        logger.warning(f".env file not found: {env_file}")
        return {}

    env_vars = {}

    try:
        # Try using python-dotenv if available
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file} (using python-dotenv)")
        return env_vars
    except ImportError:
        # Manual parsing
        logger.info(f"Loading environment from {env_file} (manual parsing)")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    env_vars[key] = value
                    os.environ[key] = value

    return env_vars


def validate_environment() -> Tuple[str, str, str, str]:
    """
    Validate required environment variables are set.

    Returns:
        Tuple of (api_url, api_token, workspace_id, database_id)

    Raises:
        ValueError if required variables are missing
    """
    api_url = os.getenv('APPFLOWY_API_URL')
    api_token = os.getenv('APPFLOWY_API_TOKEN')
    workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')
    database_id = os.getenv('APPFLOWY_DATABASE_ID')

    missing = []
    if not api_url:
        missing.append('APPFLOWY_API_URL')
    if not api_token:
        missing.append('APPFLOWY_API_TOKEN')
    if not workspace_id:
        missing.append('APPFLOWY_WORKSPACE_ID')
    if not database_id:
        missing.append('APPFLOWY_DATABASE_ID')

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return api_url, api_token, workspace_id, database_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync AI_agents tasks to AppFlowy Kanban board',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - show what would be synced
  python sync_tasks.py --dry-run

  # Sync only changed tasks
  python sync_tasks.py

  # Force sync all tasks
  python sync_tasks.py --force

  # Use custom .env file
  python sync_tasks.py --env-file /path/to/.env

Data Sources:
  - .ai-agents/state/team-communication.json
  - .ai-agents/state/feature-tracking.json (optional)
  - .planning/ROADMAP.md
  - whats-next.md (optional)
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be synced without making changes')
    parser.add_argument('--force', action='store_true',
                        help='Force re-sync all tasks, ignoring sync status')
    parser.add_argument('--env-file', type=Path,
                        help='Path to .env file (default: auto-detect)')

    args = parser.parse_args()

    try:
        # Load environment variables
        load_env_file(args.env_file)

        # Override with AI Agents workspace IDs (force override)
        os.environ['APPFLOWY_WORKSPACE_ID'] = 'c9674d81-6037-4dc3-9aa6-e2d833162b0f'
        os.environ['APPFLOWY_DATABASE_ID'] = '6f9c57aa-dda0-4aac-ba27-54544d85270e'

        # Validate environment
        api_url, api_token, workspace_id, database_id = validate_environment()

        # Create client
        client = AppFlowyClient(api_url, api_token, workspace_id, database_id)

        # Test connection
        logger.info("Testing AppFlowy connection...")
        try:
            workspaces = client.list_workspaces()
            logger.info(f"✅ Connected to AppFlowy - {len(workspaces)} workspace(s) accessible")
        except AppFlowyAPIError as e:
            logger.error(f"❌ Failed to connect to AppFlowy: {e}")
            return 1

        # Create sync manager
        sync_manager = TaskSyncManager(client, dry_run=args.dry_run, force=args.force)

        # Sync all tasks
        synced, skipped, failed = sync_manager.sync_all()

        # Return appropriate exit code
        if failed > 0:
            return 1
        elif synced == 0 and skipped == 0:
            logger.warning("No tasks were processed")
            return 1
        else:
            return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("\nSync interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
