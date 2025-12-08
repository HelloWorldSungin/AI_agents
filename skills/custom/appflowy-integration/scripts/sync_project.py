#!/usr/bin/env python3
"""
Generic AppFlowy Project Sync Script

A flexible, configuration-driven script that can sync any project's documentation
to AppFlowy. Supports multiple input methods, auto-discovery, and incremental sync.

Usage:
    # Sync with config file
    python sync_project.py --config appflowy-sync.yaml

    # Auto-discover and sync
    python sync_project.py --auto-discover --parent "Documentation"

    # Sync specific folder
    python sync_project.py --source docs/ --parent "API Docs"

    # Dry run
    python sync_project.py --config appflowy-sync.yaml --dry-run

    # Force re-sync
    python sync_project.py --config appflowy-sync.yaml --force

Environment Variables:
    APPFLOWY_API_URL            AppFlowy API base URL
    APPFLOWY_API_TOKEN          JWT authentication token
    APPFLOWY_WORKSPACE_ID       Target workspace ID
    APPFLOWY_PARENT_PAGE_ID     (Optional) Parent page ID

Author: AI Agents Team
Version: 1.0.0
"""

import os
import sys
import json
import yaml
import argparse
import logging
import hashlib
import re
import glob as glob_module
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
import requests
from requests.exceptions import RequestException, HTTPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Markdown to Delta Block Converter
# ============================================================================

def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """
    Parse inline markdown formatting into delta operations.

    Supports:
    - **bold** or __bold__
    - *italic* or _italic_
    - `code`
    - [text](url)
    - ~~strikethrough~~

    Returns list of delta objects with attributes.
    """
    delta = []
    pos = 0

    # Pattern order matters - more specific patterns first
    patterns = [
        # Links: [text](url)
        (r'\[([^\]]+)\]\(([^\)]+)\)', lambda m: {"insert": m.group(1), "attributes": {"href": m.group(2)}}),
        # Bold: **text** or __text__
        (r'\*\*([^\*]+)\*\*|__([^_]+)__', lambda m: {"insert": m.group(1) or m.group(2), "attributes": {"bold": True}}),
        # Strikethrough: ~~text~~
        (r'~~([^~]+)~~', lambda m: {"insert": m.group(1), "attributes": {"strikethrough": True}}),
        # Italic: *text* or _text_ (but not ** or __)
        (r'(?<!\*)\*([^\*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)', lambda m: {"insert": m.group(1) or m.group(2), "attributes": {"italic": True}}),
        # Code: `text`
        (r'`([^`]+)`', lambda m: {"insert": m.group(1), "attributes": {"code": True}}),
    ]

    while pos < len(text):
        # Find the earliest match among all patterns
        earliest_match = None
        earliest_pos = len(text)
        matched_pattern = None

        for pattern, formatter in patterns:
            match = re.search(pattern, text[pos:])
            if match and match.start() < earliest_pos:
                earliest_pos = match.start()
                earliest_match = match
                matched_pattern = formatter

        if earliest_match:
            # Add plain text before the match
            if earliest_pos > 0:
                plain_text = text[pos:pos + earliest_pos]
                if plain_text:
                    delta.append({"insert": plain_text})

            # Add formatted text
            delta.append(matched_pattern(earliest_match))
            pos += earliest_pos + len(earliest_match.group(0))
        else:
            # No more matches, add remaining text
            remaining = text[pos:]
            if remaining:
                delta.append({"insert": remaining})
            break

    return delta if delta else [{"insert": text}]


def is_table_row(line: str) -> bool:
    """Check if a line is a markdown table row."""
    return '|' in line and line.strip().startswith('|') or line.count('|') >= 2


def parse_table(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """
    Parse a markdown table starting at start_idx.

    Returns:
        Tuple of (table_lines, next_index)
    """
    table_lines = []
    i = start_idx

    while i < len(lines):
        line = lines[i]
        if is_table_row(line):
            table_lines.append(line)
            i += 1
        else:
            break

    return table_lines, i


def table_to_code_block(table_lines: List[str]) -> Dict[str, Any]:
    """Convert markdown table to a code block for simple display."""
    return {
        "type": "code",
        "data": {
            "language": "plaintext",
            "delta": [{"insert": "\n".join(table_lines)}]
        }
    }


def markdown_to_blocks(markdown: str) -> List[Dict[str, Any]]:
    """
    Convert markdown content to AppFlowy Delta block format.

    Supports:
    - Headings (# through ######) with rich text
    - Bullet lists (-, *) with rich text
    - Numbered lists (1., 2., etc.) with rich text
    - Code blocks (```)
    - Blockquotes (>) with rich text
    - Tables (as code blocks)
    - Regular paragraphs with rich text
    - Rich text formatting:
        - **bold** or __bold__
        - *italic* or _italic_
        - `code`
        - [text](url)
        - ~~strikethrough~~
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

        # Tables - detect and parse
        if is_table_row(line):
            table_lines, next_i = parse_table(lines, i)
            if len(table_lines) >= 2:  # At least header + separator
                blocks.append(table_to_code_block(table_lines))
                i = next_i
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
                    "delta": parse_inline_formatting(text)
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
                    "delta": parse_inline_formatting(text)
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
                    "delta": parse_inline_formatting(text)
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
                    "delta": parse_inline_formatting(text)
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
                "delta": parse_inline_formatting(line)
            }
        })
        i += 1

    return blocks


# ============================================================================
# AppFlowy API Client
# ============================================================================

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
    """Simple AppFlowy REST API client."""

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

    def get_workspace_folder(self) -> Dict:
        """Get workspace folder structure."""
        return self._make_request('GET', f'/api/workspace/{self.workspace_id}/folder')

    def find_page_by_name(self, name: str, folder_structure: Optional[dict] = None) -> Optional[str]:
        """Find a page/folder by name. Returns view_id if found."""
        if folder_structure is None:
            folder_structure = self.get_workspace_folder()

        if isinstance(folder_structure, dict) and 'data' in folder_structure:
            folder_structure = folder_structure['data']

        def search_recursive(item: dict) -> Optional[str]:
            if item.get('name') == name:
                return item.get('view_id')
            children = item.get('children', [])
            if children:
                for child in children:
                    result = search_recursive(child)
                    if result:
                        return result
            return None

        return search_recursive(folder_structure)

    def find_child_by_name(self, parent_id: str, name: str, folder_structure: Optional[dict] = None) -> Optional[str]:
        """Find a direct child by name under a specific parent."""
        if folder_structure is None:
            folder_structure = self.get_workspace_folder()

        if isinstance(folder_structure, dict) and 'data' in folder_structure:
            folder_structure = folder_structure['data']

        def find_parent_and_search(item: dict) -> Optional[str]:
            if item.get('view_id') == parent_id:
                children = item.get('children', [])
                for child in children:
                    if child.get('name') == name:
                        return child.get('view_id')
                return None
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
        data = {'name': name, 'layout': 0}
        if parent_id:
            data['parent_view_id'] = parent_id
        return self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view', json=data)

    def create_page(self, name: str, content: str, parent_id: Optional[str] = None) -> dict:
        """Create a page with content (two-step: create + append blocks)."""
        data = {'name': name, 'layout': 0}
        if parent_id:
            data['parent_view_id'] = parent_id

        result = self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view', json=data)
        view_id = result.get('data', {}).get('view_id')

        if view_id and content:
            try:
                blocks = markdown_to_blocks(content)
                self.append_blocks(view_id, blocks)
            except Exception as e:
                logger.warning(f"Failed to append content to page {view_id}: {e}")

        return result

    def append_blocks(self, page_id: str, blocks: List[Dict[str, Any]]) -> dict:
        """Append content blocks to an existing page."""
        data = {'blocks': blocks}
        return self._make_request('POST', f'/api/workspace/{self.workspace_id}/page-view/{page_id}/append-block', json=data)

    def update_page(self, page_id: str, name: str, content: str) -> dict:
        """Update an existing page (metadata + append blocks)."""
        try:
            self._make_request('PATCH', f'/api/workspace/{self.workspace_id}/page-view/{page_id}', json={'name': name})
        except Exception as e:
            logger.warning(f"Failed to update page metadata: {e}")

        if content:
            try:
                blocks = markdown_to_blocks(content)
                return self.append_blocks(page_id, blocks)
            except Exception as e:
                logger.error(f"Failed to append content blocks: {e}")
                raise

        return {}


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif config_path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")


def load_env_file(env_file: Optional[Path] = None):
    """Load environment variables from .env file."""
    if env_file and env_file.exists():
        logger.info(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def validate_environment() -> Tuple[str, str, str]:
    """Validate required environment variables."""
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


# ============================================================================
# Document Discovery
# ============================================================================

def discover_documents(root_dir: Path, patterns: Optional[List[str]] = None) -> List[Path]:
    """
    Auto-discover documentation files in a directory.

    Args:
        root_dir: Root directory to search
        patterns: List of glob patterns (default: common doc patterns)

    Returns:
        List of discovered file paths
    """
    if patterns is None:
        patterns = [
            'README.md',
            'docs/**/*.md',
            'documentation/**/*.md',
            'guides/**/*.md',
            'examples/**/README.md',
        ]

    discovered = []
    for pattern in patterns:
        matches = root_dir.glob(pattern)
        discovered.extend([p for p in matches if p.is_file()])

    return sorted(set(discovered))


def expand_glob_pattern(base_path: Path, pattern: str) -> List[Path]:
    """Expand a glob pattern relative to base path."""
    full_pattern = str(base_path / pattern)
    matches = glob_module.glob(full_pattern, recursive=True)
    return [Path(m) for m in matches if Path(m).is_file()]


# ============================================================================
# Sync Manager
# ============================================================================

class ProjectSyncManager:
    """Manages project documentation sync to AppFlowy."""

    def __init__(
        self,
        client: AppFlowyClient,
        project_root: Path,
        sync_status_file: Path,
        dry_run: bool = False,
        force: bool = False
    ):
        self.client = client
        self.project_root = project_root
        self.sync_status_file = sync_status_file
        self.dry_run = dry_run
        self.force = force
        self.sync_status = self._load_sync_status()
        self.folder_ids: Dict[str, str] = {}
        self.folder_structure: Optional[dict] = None

    def _load_sync_status(self) -> dict:
        """Load sync status from JSON file."""
        if self.sync_status_file.exists():
            try:
                with open(self.sync_status_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load sync status: {e}")
        return {
            'last_sync': None,
            'synced_files': {},
            'folder_ids': {},
            'parent_page_id': None
        }

    def _save_sync_status(self):
        """Save sync status to JSON file."""
        if self.dry_run:
            logger.info("DRY RUN: Would save sync status")
            return

        try:
            self.sync_status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sync_status_file, 'w') as f:
                json.dump(self.sync_status, f, indent=2)
            logger.debug(f"Sync status saved to {self.sync_status_file}")
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

        if not file_path.exists():
            return False, "file does not exist"

        try:
            file_str = str(file_path.relative_to(self.project_root))
        except ValueError:
            file_str = str(file_path)

        current_hash = self._compute_file_hash(file_path)

        if file_str not in self.sync_status['synced_files']:
            return True, "never synced"

        last_hash = self.sync_status['synced_files'][file_str].get('hash')
        if last_hash != current_hash:
            return True, "content changed"

        return False, "up to date"

    def _ensure_parent_page(self, parent_name: Optional[str] = None) -> Optional[str]:
        """Ensure parent page exists, create if needed."""
        if not parent_name:
            return None

        # Check cache
        if 'parent_page_id' in self.sync_status and self.sync_status['parent_page_id']:
            return self.sync_status['parent_page_id']

        # Check environment variable
        env_parent_id = os.getenv('APPFLOWY_PARENT_PAGE_ID')
        if env_parent_id:
            logger.info(f"Using parent page ID from environment: {env_parent_id}")
            self.sync_status['parent_page_id'] = env_parent_id
            return env_parent_id

        if self.dry_run:
            logger.info(f"DRY RUN: Would ensure parent page '{parent_name}'")
            return "dry-run-parent"

        # Find or create parent page
        try:
            if not self.folder_structure:
                self.folder_structure = self.client.get_workspace_folder()

            parent_id = self.client.find_page_by_name(parent_name, self.folder_structure)

            if parent_id:
                logger.info(f"Found existing parent page '{parent_name}' (ID: {parent_id})")
            else:
                logger.info(f"Creating parent page '{parent_name}'...")
                result = self.client.create_folder(parent_name)
                parent_id = result.get('data', {}).get('view_id')
                logger.info(f"Created parent page '{parent_name}' (ID: {parent_id})")
                self.folder_structure = None

            self.sync_status['parent_page_id'] = parent_id
            return parent_id

        except AppFlowyAPIError as e:
            logger.error(f"Failed to ensure parent page: {e}")
            raise

    def _ensure_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Ensure folder exists, create if needed."""
        cache_key = f"{parent_id}:{folder_name}" if parent_id else folder_name

        # Check cache
        if cache_key in self.folder_ids:
            return self.folder_ids[cache_key]

        # Check sync status
        if cache_key in self.sync_status.get('folder_ids', {}):
            folder_id = self.sync_status['folder_ids'][cache_key]
            self.folder_ids[cache_key] = folder_id
            logger.debug(f"Using cached folder '{folder_name}' (ID: {folder_id})")
            return folder_id

        if self.dry_run:
            logger.info(f"DRY RUN: Would create folder '{folder_name}'")
            folder_id = f"dry-run-folder-{folder_name}"
        else:
            try:
                if not self.folder_structure:
                    self.folder_structure = self.client.get_workspace_folder()

                # Check if folder exists
                if parent_id:
                    existing_id = self.client.find_child_by_name(parent_id, folder_name, self.folder_structure)
                else:
                    existing_id = self.client.find_page_by_name(folder_name, self.folder_structure)

                if existing_id:
                    logger.debug(f"Found existing folder '{folder_name}' (ID: {existing_id})")
                    folder_id = existing_id
                else:
                    result = self.client.create_folder(folder_name, parent_id=parent_id)
                    folder_id = result.get('data', {}).get('view_id')
                    logger.info(f"Created folder '{folder_name}' (ID: {folder_id})")
                    self.folder_structure = None

            except AppFlowyAPIError as e:
                logger.error(f"Failed to ensure folder '{folder_name}': {e}")
                raise

        self.folder_ids[cache_key] = folder_id
        if 'folder_ids' not in self.sync_status:
            self.sync_status['folder_ids'] = {}
        self.sync_status['folder_ids'][cache_key] = folder_id
        return folder_id

    def _sync_document(
        self,
        file_path: Path,
        folder_name: Optional[str],
        page_name: str,
        parent_id: Optional[str] = None
    ) -> bool:
        """Sync a single document to AppFlowy."""
        needs_sync, reason = self._needs_sync(file_path)

        if not needs_sync:
            logger.info(f"⏭️  Skipping {file_path.name} - {reason}")
            return True

        logger.info(f"📄 Syncing {file_path.name} -> {folder_name or 'root'}/{page_name} ({reason})")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return False

        # Determine target folder
        if folder_name:
            try:
                target_parent_id = self._ensure_folder(folder_name, parent_id)
            except AppFlowyAPIError as e:
                logger.error(f"Failed to ensure folder: {e}")
                return False
        else:
            target_parent_id = parent_id

        # Create or update page
        if self.dry_run:
            logger.info(f"DRY RUN: Would sync '{page_name}' ({len(content)} bytes)")
            success = True
            page_id = f"dry-run-page-{page_name}"
        else:
            try:
                try:
                    file_str = str(file_path.relative_to(self.project_root))
                except ValueError:
                    file_str = str(file_path)

                # Check if page already exists
                if file_str in self.sync_status['synced_files']:
                    page_id = self.sync_status['synced_files'][file_str].get('page_id')
                    if page_id:
                        self.client.update_page(page_id, page_name, content)
                        logger.info(f"✅ Updated page '{page_name}'")
                    else:
                        result = self.client.create_page(page_name, content, target_parent_id)
                        page_id = result.get('data', {}).get('view_id')
                        logger.info(f"✅ Created page '{page_name}' (ID: {page_id})")
                else:
                    result = self.client.create_page(page_name, content, target_parent_id)
                    page_id = result.get('data', {}).get('view_id')
                    logger.info(f"✅ Created page '{page_name}' (ID: {page_id})")

                success = True
            except AppFlowyAPIError as e:
                logger.error(f"❌ Failed to sync '{page_name}': {e}")
                return False

        # Update sync status
        try:
            file_str = str(file_path.relative_to(self.project_root))
        except ValueError:
            file_str = str(file_path)

        self.sync_status['synced_files'][file_str] = {
            'hash': self._compute_file_hash(file_path),
            'page_id': page_id,
            'page_name': page_name,
            'folder_name': folder_name,
            'last_sync': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        return success

    def sync_from_config(self, config: Dict[str, Any]) -> Tuple[int, int, int]:
        """
        Sync documents based on configuration.

        Returns:
            Tuple of (synced, skipped, failed) counts
        """
        parent_name = config.get('parent_page')
        parent_id = self._ensure_parent_page(parent_name)

        synced = 0
        skipped = 0
        failed = 0

        structure = config.get('structure', [])

        for item in structure:
            folder_name = item.get('folder')
            documents = item.get('documents', [])

            for doc in documents:
                source = doc.get('source')
                if not source:
                    logger.warning(f"Missing 'source' in document config: {doc}")
                    failed += 1
                    continue

                # Handle glob patterns
                if '*' in source:
                    file_paths = expand_glob_pattern(self.project_root, source)
                else:
                    file_paths = [self.project_root / source]

                for file_path in file_paths:
                    if not file_path.exists():
                        logger.warning(f"⚠️  File not found: {file_path}")
                        failed += 1
                        continue

                    # Determine page name
                    if doc.get('name_from_path'):
                        page_name = file_path.parent.name
                    else:
                        page_name = doc.get('name', file_path.stem)

                    # Sync document
                    success = self._sync_document(file_path, folder_name, page_name, parent_id)

                    if success:
                        needs_sync, _ = self._needs_sync(file_path)
                        if needs_sync or self.force:
                            synced += 1
                        else:
                            skipped += 1
                    else:
                        failed += 1

        # Update last sync time
        self.sync_status['last_sync'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self._save_sync_status()

        return synced, skipped, failed

    def sync_auto_discover(self, parent_name: Optional[str] = None) -> Tuple[int, int, int]:
        """
        Auto-discover and sync documents.

        Returns:
            Tuple of (synced, skipped, failed) counts
        """
        logger.info("Auto-discovering documentation files...")
        discovered = discover_documents(self.project_root)
        logger.info(f"Found {len(discovered)} files")

        parent_id = self._ensure_parent_page(parent_name)

        synced = 0
        skipped = 0
        failed = 0

        for file_path in discovered:
            # Determine folder structure from path
            try:
                rel_path = file_path.relative_to(self.project_root)
                parts = rel_path.parts
                if len(parts) > 1:
                    folder_name = parts[0].replace('-', ' ').replace('_', ' ').title()
                else:
                    folder_name = None
            except ValueError:
                folder_name = None

            page_name = file_path.stem.replace('-', ' ').replace('_', ' ').title()

            success = self._sync_document(file_path, folder_name, page_name, parent_id)

            if success:
                needs_sync, _ = self._needs_sync(file_path)
                if needs_sync or self.force:
                    synced += 1
                else:
                    skipped += 1
            else:
                failed += 1

        # Update last sync time
        self.sync_status['last_sync'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self._save_sync_status()

        return synced, skipped, failed

    def sync_source_folder(
        self,
        source_path: Path,
        parent_name: Optional[str] = None
    ) -> Tuple[int, int, int]:
        """
        Sync all markdown files in a source folder.

        Returns:
            Tuple of (synced, skipped, failed) counts
        """
        if not source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")

        parent_id = self._ensure_parent_page(parent_name)

        synced = 0
        skipped = 0
        failed = 0

        for file_path in source_path.rglob('*.md'):
            try:
                rel_path = file_path.relative_to(source_path)
                parts = rel_path.parts
                if len(parts) > 1:
                    folder_name = parts[0].replace('-', ' ').replace('_', ' ').title()
                else:
                    folder_name = None
            except ValueError:
                folder_name = None

            page_name = file_path.stem.replace('-', ' ').replace('_', ' ').title()

            success = self._sync_document(file_path, folder_name, page_name, parent_id)

            if success:
                needs_sync, _ = self._needs_sync(file_path)
                if needs_sync or self.force:
                    synced += 1
                else:
                    skipped += 1
            else:
                failed += 1

        # Update last sync time
        self.sync_status['last_sync'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self._save_sync_status()

        return synced, skipped, failed


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generic AppFlowy Project Sync Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync with config file
  python sync_project.py --config appflowy-sync.yaml

  # Auto-discover and sync
  python sync_project.py --auto-discover --parent "Documentation"

  # Sync specific folder
  python sync_project.py --source docs/ --parent "API Docs"

  # Dry run
  python sync_project.py --config appflowy-sync.yaml --dry-run

  # Force re-sync
  python sync_project.py --config appflowy-sync.yaml --force

Environment Variables:
  APPFLOWY_API_URL          AppFlowy API base URL
  APPFLOWY_API_TOKEN        JWT authentication token
  APPFLOWY_WORKSPACE_ID     Target workspace ID
  APPFLOWY_PARENT_PAGE_ID   (Optional) Parent page ID
        """
    )

    parser.add_argument('--config', type=Path, help='Path to config file (YAML or JSON)')
    parser.add_argument('--auto-discover', action='store_true', help='Auto-discover documentation files')
    parser.add_argument('--source', type=Path, help='Source folder to sync')
    parser.add_argument('--parent', type=str, help='Parent page name')
    parser.add_argument('--project-root', type=Path, help='Project root directory (default: current directory)')
    parser.add_argument('--sync-status', type=Path, help='Path to sync status file')
    parser.add_argument('--env-file', type=Path, help='Path to .env file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be synced without making changes')
    parser.add_argument('--force', action='store_true', help='Force re-sync all files')

    args = parser.parse_args()

    # Validate arguments
    if not args.config and not args.auto_discover and not args.source:
        parser.error("Must specify one of: --config, --auto-discover, or --source")

    try:
        # Load environment variables
        load_env_file(args.env_file)

        # Validate environment
        api_url, api_token, workspace_id = validate_environment()

        # Set project root
        project_root = args.project_root or Path.cwd()

        # Set sync status file
        sync_status_file = args.sync_status or project_root / '.appflowy-sync-status.json'

        # Create client
        client = AppFlowyClient(api_url, api_token, workspace_id)

        # Test connection
        logger.info("Testing AppFlowy connection...")
        try:
            folder = client.get_workspace_folder()
            logger.info(f"✅ Connected to AppFlowy")
        except AppFlowyAPIError as e:
            logger.error(f"❌ Failed to connect to AppFlowy: {e}")
            return 1

        # Create sync manager
        sync_manager = ProjectSyncManager(
            client=client,
            project_root=project_root,
            sync_status_file=sync_status_file,
            dry_run=args.dry_run,
            force=args.force
        )

        # Print header
        logger.info("=" * 60)
        logger.info("AppFlowy Project Sync v1.0.0")
        logger.info("=" * 60)
        logger.info(f"Project root: {project_root}")
        logger.info(f"Workspace ID: {workspace_id}")
        logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE SYNC'}")
        if args.force:
            logger.info("Force sync: YES")
        logger.info("=" * 60)

        # Sync based on mode
        if args.config:
            logger.info(f"Loading config from {args.config}")
            config = load_config(args.config)
            synced, skipped, failed = sync_manager.sync_from_config(config)
        elif args.auto_discover:
            synced, skipped, failed = sync_manager.sync_auto_discover(args.parent)
        elif args.source:
            synced, skipped, failed = sync_manager.sync_source_folder(args.source, args.parent)

        # Print summary
        logger.info("=" * 60)
        logger.info("Sync Summary")
        logger.info("=" * 60)
        logger.info(f"✅ Synced:  {synced}")
        logger.info(f"⏭️  Skipped: {skipped}")
        logger.info(f"❌ Failed:  {failed}")
        logger.info(f"📊 Total:   {synced + skipped + failed}")
        logger.info("=" * 60)

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
