#!/usr/bin/env python3
"""
AppFlowy Documentation Sync Script (Database-based)

Syncs AI_agents documentation to AppFlowy workspace using database rows.
Instead of creating pages/folders (unsupported), this script creates rows in a
"Documentation" database with Title, Content, Category, and LastUpdated fields.

SETUP REQUIRED:
1. Create a "Documentation" database in AppFlowy UI with these fields:
   - Title (Text) - Primary field
   - Content (Long Text)
   - Category (Select: Getting Started, Guides, Reference, Examples)
   - LastUpdated (Date)
   - FilePath (Text)
   - Status (Select: Draft, Published, Archived)

2. Set APPFLOWY_DOCS_DATABASE_ID in .env file

Usage:
    python sync_docs_database.py [--dry-run] [--force] [--env-file PATH]

Options:
    --dry-run    Show what would be synced without making changes
    --force      Force re-sync all files, ignoring sync status
    --env-file   Path to .env file (default: auto-detect)

Environment Variables:
    APPFLOWY_API_URL            AppFlowy API base URL
    APPFLOWY_API_TOKEN          JWT authentication token
    APPFLOWY_WORKSPACE_ID       Target workspace ID
    APPFLOWY_DOCS_DATABASE_ID   Documentation database ID

Author: AI Agents Team
Version: 2.0.0 (Database-based)
"""

import os
import sys
import json
import argparse
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
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
    """AppFlowy REST API client for database-based sync."""

    def __init__(self, api_url: str, token: str, workspace_id: str, database_id: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.workspace_id = workspace_id
        self.database_id = database_id
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.field_mapping = None  # Cache for field ID mapping

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated API request."""
        url = f"{self.api_url}{endpoint}"
        kwargs['headers'] = self.headers

        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()

            # Handle empty responses
            if not response.content:
                return {}

            # Parse JSON response
            data = response.json()

            # Check for AppFlowy error codes
            if isinstance(data, dict) and data.get('code', 0) != 0:
                error_msg = data.get('message', 'Unknown error')
                raise AppFlowyAPIError(f"API error: {error_msg}")

            return data

        except HTTPError as e:
            if e.response.status_code == 401:
                raise AppFlowyAuthError("Authentication failed - check API token")
            elif e.response.status_code == 403:
                raise AppFlowyAuthError("Permission denied - check workspace access")
            elif e.response.status_code == 404:
                raise AppFlowyNotFoundError(f"Resource not found: {endpoint}")
            elif e.response.status_code == 405:
                raise AppFlowyAPIError(f"Method not allowed: {method} {endpoint}")
            else:
                raise AppFlowyAPIError(f"API error {e.response.status_code}: {e.response.text}")
        except RequestException as e:
            raise AppFlowyAPIError(f"Failed to connect to AppFlowy: {e}")

    def list_workspaces(self) -> List[dict]:
        """List all accessible workspaces."""
        result = self._make_request('GET', '/api/workspace')
        # Handle both direct list and wrapped response
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'data' in result:
            return result['data']
        return []

    def get_database_schema(self) -> dict:
        """Get database schema including field definitions."""
        return self._make_request(
            'GET',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}'
        )

    def get_field_mapping(self) -> Dict[str, str]:
        """Auto-detect field IDs from database schema.

        Returns a mapping of field names to field IDs.
        Expected fields: Title, Content, Category, FilePath, LastUpdated, Status
        """
        if self.field_mapping is not None:
            return self.field_mapping

        schema = self.get_database_schema()

        # Extract fields from schema
        fields = {}
        if isinstance(schema, dict):
            field_list = schema.get('fields', [])
            for field in field_list:
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                if field_name and field_id:
                    fields[field_name] = field_id

        # Cache the mapping
        self.field_mapping = fields
        return fields

    def get_database_rows(self) -> List[dict]:
        """Get all row IDs from database."""
        result = self._make_request(
            'GET',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row'
        )
        # Extract row IDs from response
        if isinstance(result, dict) and 'data' in result:
            return result['data']
        return []

    def create_row(self, data: dict) -> dict:
        """Create a new row in the database.

        Args:
            data: Dictionary with field names as keys (e.g., {'Title': 'My Doc', 'Content': '...'})
        """
        # Convert field names to field IDs
        field_mapping = self.get_field_mapping()
        row_data = {}

        for field_name, value in data.items():
            field_id = field_mapping.get(field_name)
            if field_id:
                row_data[field_id] = value
            else:
                logger.warning(f"Field '{field_name}' not found in database schema")

        return self._make_request(
            'POST',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row',
            json={'data': row_data}
        )

    def update_row(self, row_id: str, data: dict) -> dict:
        """Update an existing row.

        Args:
            row_id: Row ID to update
            data: Dictionary with field names as keys (e.g., {'Title': 'My Doc', 'Content': '...'})
        """
        # Convert field names to field IDs
        field_mapping = self.get_field_mapping()
        row_data = {}

        for field_name, value in data.items():
            field_id = field_mapping.get(field_name)
            if field_id:
                row_data[field_id] = value
            else:
                logger.warning(f"Field '{field_name}' not found in database schema")

        return self._make_request(
            'PATCH',
            f'/api/workspace/{self.workspace_id}/database/{self.database_id}/row',
            json={'row_id': row_id, 'data': row_data}
        )


class DocumentSyncManager:
    """Manages documentation sync to AppFlowy database."""

    # Repository root
    REPO_ROOT = Path('/Users/sunginkim/GIT/AI_agents')

    # Sync status file
    SYNC_STATUS_FILE = REPO_ROOT / 'skills/custom/appflowy-integration/.sync-status-db.json'

    # Document mappings: local_path -> (category, title)
    DOCUMENTS = {
        'README.md': ('Getting Started', 'README'),
        'docs/guides/ARCHITECTURE.md': ('Guides', 'Architecture'),
        'docs/guides/Context_Engineering.md': ('Guides', 'Context Engineering'),
        'docs/guides/SKILLS_GUIDE.md': ('Guides', 'Skills Guide'),
        'docs/guides/PRACTICAL_WORKFLOW_GUIDE.md': ('Guides', 'Practical Workflow'),
        'docs/reference/CHEAT_SHEET.md': ('Reference', 'Cheat Sheet Index'),
        'docs/reference/FAQ.md': ('Reference', 'FAQ'),
        'docs/reference/CHEAT_SHEET/01-state-files.md': ('Reference', 'State Files'),
        'docs/reference/CHEAT_SHEET/00-quick-start.md': ('Getting Started', 'Quick Start'),
        'examples/web-app-team/README.md': ('Examples', 'Web App Team'),
        'examples/mobile-app-team/README.md': ('Examples', 'Mobile App Team'),
        'docs/guides/E2E_TESTING.md': ('Guides', 'E2E Testing'),
        'docs/guides/LONG_RUNNING_AGENTS.md': ('Guides', 'Long Running Agents'),
        'starter-templates/README.md': ('Getting Started', 'Starter Templates'),
    }

    def __init__(self, client: AppFlowyClient, dry_run: bool = False, force: bool = False):
        self.client = client
        self.dry_run = dry_run
        self.force = force
        self.sync_status = self._load_sync_status()

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
            'synced_files': {}
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

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of file content."""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            md5.update(f.read())
        return md5.hexdigest()

    def _needs_sync(self, file_path: Path) -> Tuple[bool, str]:
        """Check if file needs to be synced."""
        if self.force:
            return True, "force sync requested"

        file_str = str(file_path.relative_to(self.REPO_ROOT))

        if not file_path.exists():
            return False, "file does not exist"

        current_hash = self._compute_file_hash(file_path)

        if file_str not in self.sync_status['synced_files']:
            return True, "never synced"

        last_hash = self.sync_status['synced_files'][file_str].get('hash')
        if last_hash != current_hash:
            return True, "content changed"

        return False, "up to date"

    def _sync_document(self, local_path: str, category: str, title: str) -> bool:
        """Sync a single document to AppFlowy database."""
        file_path = self.REPO_ROOT / local_path

        # Check if sync needed
        needs_sync, reason = self._needs_sync(file_path)

        if not needs_sync:
            logger.info(f"Skip {local_path} - {reason}")
            return True

        logger.info(f"Sync {local_path} -> {category}/{title} ({reason})")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {local_path}: {e}")
            return False

        # Prepare row data
        row_data = {
            'Title': title,
            'Content': content,
            'Category': category,
            'FilePath': local_path,
            'LastUpdated': datetime.now(timezone.utc).isoformat(),
            'Status': 'Published'
        }

        # Create or update row
        if self.dry_run:
            logger.info(f"DRY RUN: Would sync '{title}' ({len(content)} bytes)")
            success = True
            row_id = f"dry-run-{title}"
        else:
            try:
                file_str = str(file_path.relative_to(self.REPO_ROOT))

                # Check if document already synced
                if file_str in self.sync_status['synced_files']:
                    row_id = self.sync_status['synced_files'][file_str].get('row_id')
                    if row_id:
                        # Update existing row
                        result = self.client.update_row(row_id, row_data)
                        logger.info(f"Updated '{title}'")
                    else:
                        # Create new row
                        result = self.client.create_row(row_data)
                        row_id = result.get('data', {}).get('id', result.get('id'))
                        logger.info(f"Created '{title}' (ID: {row_id})")
                else:
                    # Create new row
                    result = self.client.create_row(row_data)
                    row_id = result.get('data', {}).get('id', result.get('id'))
                    logger.info(f"Created '{title}' (ID: {row_id})")

                success = True
            except AppFlowyAPIError as e:
                logger.error(f"Failed to sync '{title}': {e}")
                return False

        # Update sync status
        file_str = str(file_path.relative_to(self.REPO_ROOT))
        self.sync_status['synced_files'][file_str] = {
            'hash': self._compute_file_hash(file_path),
            'row_id': row_id,
            'title': title,
            'category': category,
            'last_sync': datetime.now(timezone.utc).isoformat()
        }

        return success

    def _validate_database_schema(self) -> bool:
        """Validate that database has required fields."""
        required_fields = {'Title', 'Content', 'Category', 'FilePath', 'LastUpdated'}

        try:
            field_mapping = self.client.get_field_mapping()

            logger.info("Database fields detected:")
            for field_name, field_id in field_mapping.items():
                logger.info(f"  - {field_name}: {field_id}")

            missing_fields = required_fields - set(field_mapping.keys())

            if missing_fields:
                logger.error(f"Missing required fields: {', '.join(missing_fields)}")
                logger.error("Please create these fields in the Documentation database")
                return False

            logger.info("Database schema validation: PASSED")
            return True

        except Exception as e:
            logger.error(f"Failed to validate database schema: {e}")
            return False

    def sync_all(self) -> Tuple[int, int, int]:
        """Sync all documents."""
        logger.info("=" * 60)
        logger.info("AppFlowy Documentation Sync (Database Mode)")
        logger.info("=" * 60)
        logger.info(f"Repository: {self.REPO_ROOT}")
        logger.info(f"Workspace ID: {self.client.workspace_id}")
        logger.info(f"Database ID: {self.client.database_id}")
        logger.info(f"Total documents: {len(self.DOCUMENTS)}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}")
        if self.force:
            logger.info("Force sync: YES")
        logger.info("=" * 60)

        # Validate database schema
        if not self._validate_database_schema():
            logger.error("Database schema validation failed - aborting sync")
            return 0, 0, len(self.DOCUMENTS)

        logger.info("=" * 60)

        synced = 0
        skipped = 0
        failed = 0

        for local_path, (category, title) in self.DOCUMENTS.items():
            try:
                file_path = self.REPO_ROOT / local_path
                if not file_path.exists():
                    logger.warning(f"File not found: {local_path}")
                    failed += 1
                    continue

                success = self._sync_document(local_path, category, title)

                if success:
                    needs_sync, _ = self._needs_sync(file_path)
                    if needs_sync or self.force:
                        synced += 1
                    else:
                        skipped += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"Unexpected error syncing {local_path}: {e}")
                failed += 1

        # Update last sync time
        self.sync_status['last_sync'] = datetime.now(timezone.utc).isoformat()

        # Save sync status
        self._save_sync_status()

        # Print summary
        logger.info("=" * 60)
        logger.info("Sync Summary")
        logger.info("=" * 60)
        logger.info(f"Synced:  {synced}")
        logger.info(f"Skipped: {skipped}")
        logger.info(f"Failed:  {failed}")
        logger.info(f"Total:   {synced + skipped + failed}")
        logger.info("=" * 60)

        return synced, skipped, failed


def load_env_file(env_file: Optional[Path] = None) -> Dict[str, str]:
    """Load environment variables from .env file."""
    if env_file is None:
        env_file = Path('/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env')

    if not env_file.exists():
        logger.warning(f".env file not found: {env_file}")
        return {}

    env_vars = {}

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
        return env_vars
    except ImportError:
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
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    env_vars[key] = value
                    os.environ[key] = value

    return env_vars


def validate_environment() -> Tuple[str, str, str, str]:
    """Validate required environment variables."""
    api_url = os.getenv('APPFLOWY_API_URL')
    api_token = os.getenv('APPFLOWY_API_TOKEN')
    workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')
    database_id = os.getenv('APPFLOWY_DOCS_DATABASE_ID')

    missing = []
    if not api_url:
        missing.append('APPFLOWY_API_URL')
    if not api_token:
        missing.append('APPFLOWY_API_TOKEN')
    if not workspace_id:
        missing.append('APPFLOWY_WORKSPACE_ID')
    if not database_id:
        missing.append('APPFLOWY_DOCS_DATABASE_ID')

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return api_url, api_token, workspace_id, database_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync AI_agents documentation to AppFlowy database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SETUP REQUIRED:
  Create a "Documentation" database in AppFlowy with these fields:
    - Title (Text) - Primary field
    - Content (Long Text)
    - Category (Select: Getting Started, Guides, Reference, Examples)
    - LastUpdated (Date)
    - FilePath (Text)
    - Status (Select: Draft, Published, Archived)

  Set APPFLOWY_DOCS_DATABASE_ID in .env file

Examples:
  python sync_docs_database.py --dry-run
  python sync_docs_database.py
  python sync_docs_database.py --force
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be synced without making changes')
    parser.add_argument('--force', action='store_true',
                        help='Force re-sync all files')
    parser.add_argument('--env-file', type=Path,
                        help='Path to .env file')

    args = parser.parse_args()

    try:
        # Load environment
        load_env_file(args.env_file)

        # Validate environment
        api_url, api_token, workspace_id, database_id = validate_environment()

        # Create client
        client = AppFlowyClient(api_url, api_token, workspace_id, database_id)

        # Test connection
        logger.info("Testing AppFlowy connection...")
        try:
            workspaces = client.list_workspaces()
            logger.info(f"Connected - {len(workspaces)} workspace(s) accessible")
        except AppFlowyAPIError as e:
            logger.error(f"Failed to connect: {e}")
            return 1

        # Create sync manager
        sync_manager = DocumentSyncManager(client, dry_run=args.dry_run, force=args.force)

        # Sync all documents
        synced, skipped, failed = sync_manager.sync_all()

        # Return exit code
        if failed > 0:
            return 1
        elif synced == 0 and skipped == 0:
            logger.warning("No documents were processed")
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
