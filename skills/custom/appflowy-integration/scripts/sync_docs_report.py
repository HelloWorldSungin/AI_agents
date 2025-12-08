#!/usr/bin/env python3
"""
AppFlowy Documentation Sync Report

Reports what documentation would be synced and provides manual instructions.

This script works within AppFlowy Cloud API limitations:
- CANNOT create folders via POST (405 error)
- CANNOT create pages via POST (405 error)
- CAN read workspace structure via GET
- CAN work with database rows

This script:
1. Checks existing folder structure
2. Reports what documents exist locally
3. Provides manual instructions for user to create pages in UI
4. Suggests database-based sync approach

Usage:
    python sync_docs_report.py [--env-file PATH]

Author: AI Agents Team
Version: 2.0.0
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
from requests.exceptions import RequestException, HTTPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class AppFlowyClient:
    """Minimal AppFlowy API client for read-only operations."""

    def __init__(self, api_url: str, token: str, workspace_id: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.workspace_id = workspace_id
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str) -> dict:
        """Make authenticated API request."""
        url = f"{self.api_url}{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers)
            response.raise_for_status()
            return response.json() if response.content else {}
        except HTTPError as e:
            logger.error(f"API error {e.response.status_code}: {e.response.text}")
            return {}
        except RequestException as e:
            logger.error(f"Connection error: {e}")
            return {}

    def list_workspaces(self) -> List[dict]:
        """List all accessible workspaces."""
        result = self._make_request('GET', '/api/workspace')
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'data' in result:
            return result['data']
        return []

    def get_folder_structure(self) -> List[dict]:
        """Get workspace folder structure."""
        result = self._make_request('GET', f'/api/workspace/{self.workspace_id}/folder')
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'data' in result:
            return result['data']
        return []


class DocumentReporter:
    """Reports documentation sync status and provides instructions."""

    REPO_ROOT = Path('/Users/sunginkim/GIT/AI_agents')

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

    def __init__(self, client: AppFlowyClient):
        self.client = client

    def generate_report(self):
        """Generate sync report and manual instructions."""
        logger.info("=" * 80)
        logger.info("AppFlowy Documentation Sync Report")
        logger.info("=" * 80)
        logger.info("")

        # Check connection
        logger.info("Checking AppFlowy connection...")
        workspaces = self.client.list_workspaces()
        if workspaces:
            logger.info(f"✓ Connected - {len(workspaces)} workspace(s) accessible")
        else:
            logger.error("✗ Failed to connect to AppFlowy")
            return

        logger.info("")

        # Check folder structure
        logger.info("Checking existing folder structure...")
        folders = self.client.get_folder_structure()
        if folders:
            logger.info(f"✓ Found {len(folders)} existing items")
        else:
            logger.info("  No existing folders found (or cannot read structure)")

        logger.info("")
        logger.info("=" * 80)
        logger.info("APPFLOWY CLOUD API LIMITATIONS")
        logger.info("=" * 80)
        logger.info("")
        logger.info("What works:")
        logger.info("  ✓ GET /api/workspace - list workspaces")
        logger.info("  ✓ GET /api/workspace/{id}/folder - get folder structure")
        logger.info("  ✓ GET/POST/PUT /api/workspace/{id}/database/{db_id}/row - database rows")
        logger.info("")
        logger.info("What doesn't work:")
        logger.info("  ✗ POST /api/workspace/{id}/folder - create folders (405 error)")
        logger.info("  ✗ POST /api/workspace/{id}/page - create pages (405 error)")
        logger.info("")
        logger.info("These operations require either:")
        logger.info("  1. Using the AppFlowy UI directly")
        logger.info("  2. Using WebSocket API (complex, undocumented)")
        logger.info("  3. Working with database rows instead of pages")
        logger.info("")

        # Check local files
        logger.info("=" * 80)
        logger.info("LOCAL DOCUMENTATION FILES")
        logger.info("=" * 80)
        logger.info("")

        existing_files = []
        missing_files = []

        for local_path, (category, title) in self.DOCUMENTS.items():
            file_path = self.REPO_ROOT / local_path
            if file_path.exists():
                size = file_path.stat().st_size
                existing_files.append((local_path, category, title, size))
            else:
                missing_files.append((local_path, category, title))

        # Report existing files by category
        categories = {}
        for local_path, category, title, size in existing_files:
            if category not in categories:
                categories[category] = []
            categories[category].append((title, local_path, size))

        for category in sorted(categories.keys()):
            logger.info(f"{category}:")
            for title, local_path, size in categories[category]:
                logger.info(f"  ✓ {title:30s} ({size:6d} bytes) - {local_path}")
            logger.info("")

        if missing_files:
            logger.info("Missing files:")
            for local_path, category, title in missing_files:
                logger.info(f"  ✗ {title} - {local_path}")
            logger.info("")

        logger.info(f"Total: {len(existing_files)} files ready to sync")
        logger.info("")

        # Provide options
        logger.info("=" * 80)
        logger.info("SYNC OPTIONS")
        logger.info("=" * 80)
        logger.info("")

        logger.info("OPTION A: Database-based sync (RECOMMENDED)")
        logger.info("-" * 80)
        logger.info("")
        logger.info("This approach works with AppFlowy's supported API:")
        logger.info("")
        logger.info("1. Create a 'Documentation' database in AppFlowy UI with these fields:")
        logger.info("   - Title (Text) - Primary field")
        logger.info("   - Content (Long Text)")
        logger.info("   - Category (Select: Getting Started, Guides, Reference, Examples)")
        logger.info("   - LastUpdated (Date)")
        logger.info("   - FilePath (Text)")
        logger.info("   - Status (Select: Draft, Published, Archived)")
        logger.info("")
        logger.info("2. Get the database ID:")
        logger.info("   - Right-click database → Copy link")
        logger.info("   - Extract ID from URL")
        logger.info("")
        logger.info("3. Add to .env file:")
        logger.info("   APPFLOWY_DOCS_DATABASE_ID=<database-id>")
        logger.info("")
        logger.info("4. Run database sync script:")
        logger.info("   python sync_docs_database.py --dry-run")
        logger.info("   python sync_docs_database.py")
        logger.info("")

        logger.info("")
        logger.info("OPTION B: Manual page creation")
        logger.info("-" * 80)
        logger.info("")
        logger.info("If you prefer traditional pages instead of database rows:")
        logger.info("")
        logger.info("1. Open AppFlowy UI")
        logger.info("2. Create these folders:")
        for category in sorted(categories.keys()):
            logger.info(f"   - {category}")
        logger.info("")
        logger.info("3. For each file, create a page:")
        for category in sorted(categories.keys()):
            logger.info(f"   {category}:")
            for title, local_path, _ in categories[category]:
                logger.info(f"     - {title} (copy from {local_path})")
            logger.info("")
        logger.info("")

        logger.info("")
        logger.info("OPTION C: Wait for future API support")
        logger.info("-" * 80)
        logger.info("")
        logger.info("AppFlowy Cloud may add page creation endpoints in the future.")
        logger.info("Monitor: https://github.com/AppFlowy-IO/AppFlowy-Cloud")
        logger.info("")

        logger.info("=" * 80)
        logger.info("RECOMMENDATION")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Use OPTION A (database-based sync) because:")
        logger.info("  ✓ Works with current AppFlowy Cloud API")
        logger.info("  ✓ Fully automated sync")
        logger.info("  ✓ Supports incremental updates")
        logger.info("  ✓ Easy to search and filter")
        logger.info("  ✓ Can use Kanban/Table/Calendar views")
        logger.info("")
        logger.info("Database rows are just as powerful as pages for documentation!")
        logger.info("")


def load_env_file(env_file: Optional[Path] = None):
    """Load environment variables from .env file."""
    if env_file is None:
        env_file = Path('/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env')

    if not env_file.exists():
        logger.warning(f".env file not found: {env_file}")
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
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
                    os.environ[key] = value


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate AppFlowy documentation sync report'
    )
    parser.add_argument('--env-file', type=Path, help='Path to .env file')

    args = parser.parse_args()

    try:
        # Load environment
        load_env_file(args.env_file)

        # Get credentials
        api_url = os.getenv('APPFLOWY_API_URL')
        api_token = os.getenv('APPFLOWY_API_TOKEN')
        workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')

        if not all([api_url, api_token, workspace_id]):
            logger.error("Missing environment variables:")
            logger.error("Required: APPFLOWY_API_URL, APPFLOWY_API_TOKEN, APPFLOWY_WORKSPACE_ID")
            return 1

        # Create client
        client = AppFlowyClient(api_url, api_token, workspace_id)

        # Generate report
        reporter = DocumentReporter(client)
        reporter.generate_report()

        return 0

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
