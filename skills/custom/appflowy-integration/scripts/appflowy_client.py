#!/usr/bin/env python3
"""
AppFlowy API Client

Provides a simple Python client for interacting with AppFlowy's REST API.
Handles authentication, workspace management, and database operations.

Usage:
    from appflowy_client import AppFlowyClient

    client = AppFlowyClient()
    workspaces = client.list_workspaces()
    databases = client.list_databases(workspace_id)
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppFlowyError(Exception):
    """Base exception for AppFlowy client errors."""
    pass


class AuthenticationError(AppFlowyError):
    """Raised when authentication fails."""
    pass


class ResourceNotFoundError(AppFlowyError):
    """Raised when a requested resource is not found."""
    pass


class PermissionDeniedError(AppFlowyError):
    """Raised when permission is denied."""
    pass


def handle_api_errors(func):
    """Decorator to handle API errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed - check API token")
            elif e.response.status_code == 403:
                raise PermissionDeniedError("Permission denied - check workspace access")
            elif e.response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {e.request.url}")
            else:
                logger.error(f"HTTP error: {e}")
                raise AppFlowyError(f"API error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            raise AppFlowyError(f"Failed to connect to AppFlowy: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    return wrapper


class AppFlowyClient:
    """Client for interacting with AppFlowy API."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_token: Optional[str] = None,
        workspace_id: Optional[str] = None
    ):
        """
        Initialize AppFlowy client.

        Args:
            api_url: AppFlowy API base URL (or set APPFLOWY_API_URL env var)
            api_token: JWT authentication token (or set APPFLOWY_API_TOKEN env var)
            workspace_id: Default workspace ID (or set APPFLOWY_WORKSPACE_ID env var)
        """
        self.api_url = api_url or os.getenv('APPFLOWY_API_URL')
        self.api_token = api_token or os.getenv('APPFLOWY_API_TOKEN')
        self.workspace_id = workspace_id or os.getenv('APPFLOWY_WORKSPACE_ID')

        if not self.api_url:
            raise ValueError("API URL must be provided or set via APPFLOWY_API_URL")
        if not self.api_token:
            raise ValueError("API token must be provided or set via APPFLOWY_API_TOKEN")

        # Remove trailing slash from API URL
        self.api_url = self.api_url.rstrip('/')

        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

        logger.info(f"AppFlowy client initialized for {self.api_url}")

    @handle_api_errors
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Any:
        """
        Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON request body

        Returns:
            Response JSON data
        """
        url = f"{self.api_url}{endpoint}"
        logger.debug(f"{method} {url}")

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=json,
            timeout=30
        )

        response.raise_for_status()

        # Some endpoints return empty responses
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    # Workspace Operations

    @handle_api_errors
    def list_workspaces(self) -> List[Dict]:
        """
        Retrieve all available workspaces.

        Returns:
            List of workspace dictionaries
        """
        logger.info("Fetching workspaces")
        return self._make_request('GET', '/api/workspace')

    @handle_api_errors
    def get_workspace_folders(self, workspace_id: Optional[str] = None) -> Dict:
        """
        Get folder structure for a workspace.

        Args:
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Folder structure dictionary
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching folders for workspace {ws_id}")
        return self._make_request('GET', f'/api/workspace/{ws_id}/folder')

    # Database Operations

    @handle_api_errors
    def list_databases(self, workspace_id: Optional[str] = None) -> List[Dict]:
        """
        Retrieve all databases in a workspace.

        Args:
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            List of database dictionaries
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching databases for workspace {ws_id}")
        return self._make_request('GET', f'/api/workspace/{ws_id}/database')

    @handle_api_errors
    def get_database_fields(
        self,
        database_id: str,
        workspace_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch field definitions for a database.

        Args:
            database_id: Database ID
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            List of field definitions
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching fields for database {database_id}")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/fields'
        return self._make_request('GET', endpoint)

    # Row Operations

    @handle_api_errors
    def get_database_rows(
        self,
        database_id: str,
        workspace_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve row IDs from a database.

        Args:
            database_id: Database ID
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            List of row dictionaries with IDs
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching rows for database {database_id}")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/row'
        return self._make_request('GET', endpoint)

    @handle_api_errors
    def get_row_detail(
        self,
        database_id: str,
        row_ids: List[str],
        workspace_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get comprehensive information for specific rows.

        Args:
            database_id: Database ID
            row_ids: List of row IDs to fetch
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            List of detailed row dictionaries
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching details for {len(row_ids)} rows")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/row/detail'
        params = {'row_ids': ','.join(row_ids)}
        return self._make_request('GET', endpoint, params=params)

    @handle_api_errors
    def create_row(
        self,
        database_id: str,
        data: Dict,
        workspace_id: Optional[str] = None
    ) -> Dict:
        """
        Add a new row to database.

        Args:
            database_id: Database ID
            data: Dictionary with field values
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Created row dictionary
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Creating row in database {database_id}")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/row'
        return self._make_request('POST', endpoint, json=data)

    @handle_api_errors
    def update_row(
        self,
        database_id: str,
        row_id: str,
        updates: Dict,
        workspace_id: Optional[str] = None
    ) -> Dict:
        """
        Update existing row or create if doesn't exist (upsert).

        Args:
            database_id: Database ID
            row_id: ID of row to update
            updates: Dictionary of field updates
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Updated row dictionary
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Updating row {row_id} in database {database_id}")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/row'
        data = {'row_id': row_id, **updates}
        return self._make_request('PUT', endpoint, json=data)

    @handle_api_errors
    def get_updated_rows(
        self,
        database_id: str,
        since_timestamp: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve recently modified rows.

        Args:
            database_id: Database ID
            since_timestamp: ISO timestamp to get changes since
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            List of updated row dictionaries
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id must be provided or set as default")

        logger.info(f"Fetching updated rows since {since_timestamp or 'all time'}")
        endpoint = f'/api/workspace/{ws_id}/database/{database_id}/row/updated'
        params = {'since': since_timestamp} if since_timestamp else {}
        return self._make_request('GET', endpoint, params=params)

    # Helper Methods

    def find_database_by_name(
        self,
        name: str,
        workspace_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Find a database by name in the workspace.

        Args:
            name: Database name to search for
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Database dictionary or None if not found
        """
        databases = self.list_databases(workspace_id)
        return next((db for db in databases if db.get('name') == name), None)

    def validate_task_data(
        self,
        database_id: str,
        task_data: Dict,
        workspace_id: Optional[str] = None
    ) -> Dict:
        """
        Validate task data against database schema.

        Args:
            database_id: Database ID
            task_data: Task data to validate
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Validated task data (only fields that exist in database)
        """
        fields = self.get_database_fields(database_id, workspace_id)
        field_names = {f['name'] for f in fields}

        # Keep only fields that exist in database
        validated = {k: v for k, v in task_data.items() if k in field_names}

        # Warn about fields not in database
        missing = set(task_data.keys()) - field_names
        if missing:
            logger.warning(f"Fields not in database schema: {missing}")

        return validated


def main():
    """Example usage of AppFlowy client."""
    try:
        # Initialize client
        client = AppFlowyClient()

        # List workspaces
        print("\n📁 Workspaces:")
        workspaces = client.list_workspaces()
        for ws in workspaces:
            print(f"  - {ws.get('name', 'Unnamed')} (ID: {ws.get('id')})")

        if not client.workspace_id and workspaces:
            client.workspace_id = workspaces[0]['id']
            print(f"\n✓ Using workspace: {client.workspace_id}")

        # List databases
        print("\n🗄️  Databases:")
        databases = client.list_databases()
        for db in databases:
            print(f"  - {db.get('name', 'Unnamed')} (ID: {db.get('id')})")

        if databases:
            # Show fields for first database
            db_id = databases[0]['id']
            print(f"\n📋 Fields in '{databases[0].get('name')}':")
            fields = client.get_database_fields(db_id)
            for field in fields:
                print(f"  - {field.get('name')} ({field.get('type')})")

    except AppFlowyError as e:
        logger.error(f"AppFlowy error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
