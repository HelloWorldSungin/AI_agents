#!/usr/bin/env python3
"""
AppFlowy Documentation Sync Script

Syncs AI_agents documentation to AppFlowy workspace with hierarchical folder structure.
Supports incremental updates by tracking sync status in a local JSON file.
Uses Delta block format for page content (not raw markdown).

Usage:
    python sync_docs.py [--dry-run] [--force] [--env-file PATH]

Options:
    --dry-run    Show what would be synced without making changes
    --force      Force re-sync all files, ignoring sync status
    --env-file   Path to .env file (default: auto-detect)

Environment Variables:
    APPFLOWY_API_URL            AppFlowy API base URL
    APPFLOWY_API_TOKEN          JWT authentication token
    APPFLOWY_WORKSPACE_ID       Target workspace ID
    APPFLOWY_DOCS_PARENT_ID     (Optional) Parent page ID for "Documentation"

Author: AI Agents Team
Version: 2.0.0

Changelog:
  v2.0.0 - Integrated markdown_to_blocks converter
         - Use append-block endpoint for content (Delta format)
         - Removed broken PATCH content update
         - Two-step process: create page, then append blocks
  v1.1.0 - Added hierarchical nesting inside Documentation page
         - Added duplicate folder prevention
         - Added APPFLOWY_DOCS_PARENT_ID environment variable support
  v1.0.0 - Initial release
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


def markdown_to_blocks(markdown: str) -> List[Dict[str, Any]]:
    """
    Convert markdown content to AppFlowy Delta block format.

    Supports:
    - Headings (# through ######)
    - Bullet lists (-, *)
    - Numbered lists (1., 2., etc.)
    - Code blocks (```)
    - Blockquotes (>)
    - Regular paragraphs
    """
    blocks = []
    lines = markdown.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Headings (# through ######)
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            blocks.append({
                "type": "heading",
                "data": {
                    "level": level,
                    "delta": [{"insert": text}]
                }
            })
            i += 1
            continue

        # Bullet lists (-, *)
        bullet_match = re.match(r'^[\-\*]\s+(.+)$', line)
        if bullet_match:
            text = bullet_match.group(1)
            blocks.append({
                "type": "bulleted_list",
                "data": {
                    "delta": [{"insert": text}]
                }
            })
            i += 1
            continue

        # Numbered lists (1., 2., etc.)
        numbered_match = re.match(r'^\d+\.\s+(.+)$', line)
        if numbered_match:
            text = numbered_match.group(1)
            blocks.append({
                "type": "numbered_list",
                "data": {
                    "delta": [{"insert": text}]
                }
            })
            i += 1
            continue

        # Blockquotes (>)
        quote_match = re.match(r'^>\s+(.+)$', line)
        if quote_match:
            text = quote_match.group(1)
            blocks.append({
                "type": "quote",
                "data": {
                    "delta": [{"insert": text}]
                }
            })
            i += 1
            continue

        # Code blocks (```)
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip() or "plain"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1

            code_content = '\n'.join(code_lines)
            blocks.append({
                "type": "code",
                "data": {
                    "language": lang,
                    "delta": [{"insert": code_content}]
                }
            })
            i += 1  # Skip closing ```
            continue

        # Regular paragraph
        blocks.append({
            "type": "paragraph",
            "data": {
                "delta": [{"insert": line}]
            }
        })
        i += 1

    return blocks


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
    """Simple AppFlowy REST API client for documentation sync."""

    def __init__(self, api_url: str, token: str, workspace_id: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.workspace_id = workspace_id
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

    def get_workspace_folder(self) -> List[dict]:
        """Get workspace folder structure."""
        return self._make_request('GET', f'/api/workspace/{self.workspace_id}/folder')

    def find_page_by_name(self, name: str, folder_structure: Optional[dict] = None) -> Optional[str]:
        """
        Find a page/folder by name in the workspace folder structure.

        Returns the view_id if found, None otherwise.
        """
        if folder_structure is None:
            folder_structure = self.get_workspace_folder()

        # Handle both dict (API response) and the data within it
        if isinstance(folder_structure, dict) and 'data' in folder_structure:
            folder_structure = folder_structure['data']

        def search_recursive(item: dict) -> Optional[str]:
            if item.get('name') == name:
                return item.get('view_id')
            # Search in children if present
            children = item.get('children', [])
            if children:
                for child in children:
                    result = search_recursive(child)
                    if result:
                        return result
            return None

        return search_recursive(folder_structure)

    def find_child_by_name(self, parent_id: str, name: str, folder_structure: Optional[dict] = None) -> Optional[str]:
        """
        Find a direct child page/folder by name under a specific parent.

        Returns the view_id if found, None otherwise.
        """
        if folder_structure is None:
            folder_structure = self.get_workspace_folder()

        # Handle both dict (API response) and the data within it
        if isinstance(folder_structure, dict) and 'data' in folder_structure:
            folder_structure = folder_structure['data']

        def find_parent_and_search(item: dict) -> Optional[str]:
            if item.get('view_id') == parent_id:
                # Found the parent, search its children
                children = item.get('children', [])
                for child in children:
                    if child.get('name') == name:
                        return child.get('view_id')
                return None
            # Search recursively in children
            children = item.get('children', [])
            if children:
                for child in children:
                    result = find_parent_and_search(child)
                    if result:
                        return result
            return None

        return find_parent_and_search(folder_structure)

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> dict:
        """Create a folder in the workspace."""
        data = {
            'name': name,
            'layout': 0  # 0 = Document layout for folders
        }
        if parent_id:
            data['parent_view_id'] = parent_id

        return self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view', json=data)

    def create_page(self, name: str, content: str, parent_id: Optional[str] = None) -> dict:
        """
        Create a page/document in the workspace with content.

        Uses two-step process:
        1. Create empty page (POST page-view)
        2. Append content blocks (POST append-block)
        """
        data = {
            'name': name,
            'layout': 0  # 0 = Document layout
        }
        if parent_id:
            data['parent_view_id'] = parent_id

        # Step 1: Create the page (empty)
        result = self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view', json=data)

        # Get the created view_id
        view_id = result.get('data', {}).get('view_id')

        # Step 2: Append content blocks if view_id was returned and content exists
        if view_id and content:
            try:
                # Convert markdown to blocks
                blocks = markdown_to_blocks(content)
                # Append blocks to page
                self.append_blocks(view_id, blocks)
            except Exception as e:
                logger.warning(f"Failed to append content to page {view_id}: {e}")

        return result

    def append_blocks(self, page_id: str, blocks: List[Dict[str, Any]]) -> dict:
        """
        Append content blocks to an existing page.

        Args:
            page_id: Target page view ID
            blocks: List of Delta block objects

        Returns:
            API response
        """
        data = {'blocks': blocks}
        return self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view/{page_id}/append-block', json=data)

    def update_page(self, page_id: str, name: str, content: str) -> dict:
        """
        Update an existing page with new content.

        Note: PATCH only updates metadata (name, icon). For content, we need to:
        1. Clear existing blocks (not supported via API)
        2. Append new blocks

        Current implementation: Appends new blocks without clearing old ones.
        """
        # Update metadata (name)
        try:
            self._make_request('PATCH', f'/api/workspace/{self.workspace_id}/page-view/{page_id}', json={'name': name})
        except Exception as e:
            logger.warning(f"Failed to update page metadata: {e}")

        # Append new content blocks
        if content:
            try:
                blocks = markdown_to_blocks(content)
                return self.append_blocks(page_id, blocks)
            except Exception as e:
                logger.error(f"Failed to append content blocks: {e}")
                raise

        return {}


class DocumentSyncManager:
    """Manages documentation sync to AppFlowy."""

    # Repository root (working directory)
    REPO_ROOT = Path('/Users/sunginkim/GIT/AI_agents')

    # Sync status file
    SYNC_STATUS_FILE = REPO_ROOT / 'skills/custom/appflowy-integration/.sync-status.json'

    # Document mappings: local_path -> (folder_path, page_name)
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
        'docs/guides/TEST-PUSHSYNC.md': ('Guides', 'Test PushSync'),
    }

    def __init__(self, client: AppFlowyClient, dry_run: bool = False, force: bool = False):
        self.client = client
        self.dry_run = dry_run
        self.force = force
        self.sync_status = self._load_sync_status()
        self.folder_ids: Dict[str, str] = {}
        self.docs_parent_id: Optional[str] = None
        self.folder_structure: Optional[dict] = None

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
            'synced_files': {},
            'folder_ids': {}
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

    def _get_documentation_parent_id(self) -> str:
        """
        Get or discover the Documentation parent page ID.

        Returns the view_id of the Documentation page.
        """
        # Check if already cached
        if self.docs_parent_id:
            return self.docs_parent_id

        # Check environment variable
        env_parent_id = os.getenv('APPFLOWY_DOCS_PARENT_ID')
        if env_parent_id:
            logger.info(f"Using Documentation parent ID from environment: {env_parent_id}")
            self.docs_parent_id = env_parent_id
            return env_parent_id

        # Check sync status
        if 'docs_parent_id' in self.sync_status:
            parent_id = self.sync_status['docs_parent_id']
            logger.info(f"Using Documentation parent ID from sync status: {parent_id}")
            self.docs_parent_id = parent_id
            return parent_id

        # Try to find "Documentation" page in workspace
        if self.dry_run:
            logger.info("DRY RUN: Would discover or create Documentation parent page")
            self.docs_parent_id = "dry-run-docs-parent"
            return self.docs_parent_id

        try:
            # Get workspace folder structure
            if not self.folder_structure:
                self.folder_structure = self.client.get_workspace_folder()

            # Search for "Documentation" page
            parent_id = self.client.find_page_by_name("Documentation", self.folder_structure)

            if parent_id:
                logger.info(f"Found existing Documentation page (ID: {parent_id})")
            else:
                # Create "Documentation" page at workspace root
                logger.info("Documentation page not found, creating it...")
                result = self.client.create_folder("Documentation")
                parent_id = result.get('data', {}).get('view_id')
                logger.info(f"Created Documentation page (ID: {parent_id})")
                # Refresh folder structure
                self.folder_structure = None

            # Cache it
            self.docs_parent_id = parent_id
            self.sync_status['docs_parent_id'] = parent_id

            return parent_id

        except AppFlowyAPIError as e:
            logger.error(f"Failed to get Documentation parent: {e}")
            raise

    def _ensure_folder(self, folder_name: str) -> str:
        """
        Ensure folder exists inside Documentation parent, create if needed.

        This creates category folders (Getting Started, Guides, Reference, Examples)
        as children of the Documentation page.
        """
        # Check cache first
        if folder_name in self.folder_ids:
            return self.folder_ids[folder_name]

        # Check sync status
        if folder_name in self.sync_status.get('folder_ids', {}):
            folder_id = self.sync_status['folder_ids'][folder_name]
            self.folder_ids[folder_name] = folder_id
            logger.info(f"Using cached folder '{folder_name}' (ID: {folder_id})")
            return folder_id

        # Get Documentation parent ID
        docs_parent_id = self._get_documentation_parent_id()

        # Create folder
        if self.dry_run:
            logger.info(f"DRY RUN: Would create folder '{folder_name}' inside Documentation (parent: {docs_parent_id})")
            folder_id = f"dry-run-folder-{folder_name}"
        else:
            try:
                # Check if folder already exists under Documentation
                if not self.folder_structure:
                    self.folder_structure = self.client.get_workspace_folder()

                existing_id = self.client.find_child_by_name(docs_parent_id, folder_name, self.folder_structure)

                if existing_id:
                    logger.info(f"Found existing folder '{folder_name}' (ID: {existing_id})")
                    folder_id = existing_id
                else:
                    # Create new folder under Documentation
                    result = self.client.create_folder(folder_name, parent_id=docs_parent_id)
                    # Response format: {"data": {"view_id": "...", "database_id": null}, "code": 0, "message": "..."}
                    folder_id = result.get('data', {}).get('view_id')
                    logger.info(f"Created folder '{folder_name}' inside Documentation (ID: {folder_id})")
                    # Refresh folder structure to include new folder
                    self.folder_structure = None

            except AppFlowyAPIError as e:
                logger.error(f"Failed to ensure folder '{folder_name}': {e}")
                raise

        self.folder_ids[folder_name] = folder_id
        self.sync_status['folder_ids'][folder_name] = folder_id
        return folder_id

    def _sync_document(self, local_path: str, folder_name: str, page_name: str) -> bool:
        """Sync a single document to AppFlowy."""
        file_path = self.REPO_ROOT / local_path

        # Check if sync needed
        needs_sync, reason = self._needs_sync(file_path)

        if not needs_sync:
            logger.info(f"⏭️  Skipping {local_path} - {reason}")
            return True

        logger.info(f"📄 Syncing {local_path} -> {folder_name}/{page_name} ({reason})")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {local_path}: {e}")
            return False

        # Ensure folder exists
        try:
            folder_id = self._ensure_folder(folder_name)
        except AppFlowyAPIError as e:
            logger.error(f"Failed to ensure folder for {local_path}: {e}")
            return False

        # Create or update page
        if self.dry_run:
            logger.info(f"DRY RUN: Would sync '{page_name}' to folder '{folder_name}'")
            logger.info(f"         Content size: {len(content)} bytes")
            success = True
            page_id = f"dry-run-page-{page_name}"
        else:
            try:
                # Check if page already exists
                file_str = str(file_path.relative_to(self.REPO_ROOT))
                if file_str in self.sync_status['synced_files']:
                    page_id = self.sync_status['synced_files'][file_str].get('page_id')
                    if page_id:
                        # Update existing page
                        result = self.client.update_page(page_id, page_name, content)
                        logger.info(f"✅ Updated page '{page_name}'")
                    else:
                        # Create new page
                        result = self.client.create_page(page_name, content, folder_id)
                        # Response format: {"data": {"view_id": "...", "database_id": null}, "code": 0, "message": "..."}
                        page_id = result.get('data', {}).get('view_id')
                        logger.info(f"✅ Created page '{page_name}' (ID: {page_id})")
                else:
                    # Create new page
                    result = self.client.create_page(page_name, content, folder_id)
                    # Response format: {"data": {"view_id": "...", "database_id": null}, "code": 0, "message": "..."}
                    page_id = result.get('data', {}).get('view_id')
                    logger.info(f"✅ Created page '{page_name}' (ID: {page_id})")

                success = True
            except AppFlowyAPIError as e:
                logger.error(f"❌ Failed to sync '{page_name}': {e}")
                return False

        # Update sync status
        file_str = str(file_path.relative_to(self.REPO_ROOT))
        self.sync_status['synced_files'][file_str] = {
            'hash': self._compute_file_hash(file_path),
            'page_id': page_id,
            'page_name': page_name,
            'folder_name': folder_name,
            'last_sync': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        return success

    def sync_all(self) -> Tuple[int, int, int]:
        """
        Sync all documents.

        Returns:
            Tuple of (synced, skipped, failed) counts
        """
        logger.info("=" * 60)
        logger.info("AppFlowy Documentation Sync v2.0.0")
        logger.info("=" * 60)
        logger.info(f"Repository: {self.REPO_ROOT}")
        logger.info(f"Workspace ID: {self.client.workspace_id}")
        logger.info(f"Total documents: {len(self.DOCUMENTS)}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}")
        if self.force:
            logger.info("Force sync: YES")
        logger.info("")
        logger.info("Target Structure: Documentation/[Category]/[Page]")
        logger.info("=" * 60)

        synced = 0
        skipped = 0
        failed = 0

        for local_path, (folder_name, page_name) in self.DOCUMENTS.items():
            try:
                # Check if file exists
                file_path = self.REPO_ROOT / local_path
                if not file_path.exists():
                    logger.warning(f"⚠️  File not found: {local_path}")
                    failed += 1
                    continue

                # Sync document
                success = self._sync_document(local_path, folder_name, page_name)

                if success:
                    # Check if actually synced or skipped
                    needs_sync, _ = self._needs_sync(file_path)
                    if needs_sync or self.force:
                        synced += 1
                    else:
                        skipped += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"❌ Unexpected error syncing {local_path}: {e}")
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


def validate_environment() -> Tuple[str, str, str]:
    """
    Validate required environment variables are set.

    Returns:
        Tuple of (api_url, api_token, workspace_id)

    Raises:
        ValueError if required variables are missing
    """
    api_url = os.getenv('APPFLOWY_API_URL')
    api_token = os.getenv('APPFLOWY_API_TOKEN')
    workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')

    missing = []
    if not api_url:
        missing.append('APPFLOWY_API_URL')
    if not api_token:
        missing.append('APPFLOWY_API_TOKEN')
    if not workspace_id:
        missing.append('APPFLOWY_WORKSPACE_ID')

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return api_url, api_token, workspace_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync AI_agents documentation to AppFlowy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - show what would be synced
  python sync_docs.py --dry-run

  # Sync only changed files
  python sync_docs.py

  # Force sync all files
  python sync_docs.py --force

  # Use custom .env file
  python sync_docs.py --env-file /path/to/.env
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be synced without making changes')
    parser.add_argument('--force', action='store_true',
                        help='Force re-sync all files, ignoring sync status')
    parser.add_argument('--env-file', type=Path,
                        help='Path to .env file (default: auto-detect)')

    args = parser.parse_args()

    try:
        # Load environment variables
        load_env_file(args.env_file)

        # Validate environment
        api_url, api_token, workspace_id = validate_environment()

        # Create client
        client = AppFlowyClient(api_url, api_token, workspace_id)

        # Test connection
        logger.info("Testing AppFlowy connection...")
        try:
            workspaces = client.list_workspaces()
            logger.info(f"✅ Connected to AppFlowy - {len(workspaces)} workspace(s) accessible")
        except AppFlowyAPIError as e:
            logger.error(f"❌ Failed to connect to AppFlowy: {e}")
            return 1

        # Create sync manager
        sync_manager = DocumentSyncManager(client, dry_run=args.dry_run, force=args.force)

        # Sync all documents
        synced, skipped, failed = sync_manager.sync_all()

        # Return appropriate exit code
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
