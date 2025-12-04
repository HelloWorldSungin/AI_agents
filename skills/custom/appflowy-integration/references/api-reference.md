# AppFlowy API Reference

<overview>
Complete reference for AppFlowy REST API endpoints, including authentication, workspace operations, database management, row operations, and error handling patterns.
</overview>

## Table of Contents

1. [Authentication](#authentication)
2. [Workspace API](#workspace-api)
3. [Database API](#database-api)
4. [Row Operations](#row-operations)
5. [Field Operations](#field-operations)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)

---

## Authentication

<authentication>
**Base URL:**
```
http://appflowy.arknode-ai.home  # Production (ArkNode-AI)
http://localhost:8080            # Development
```

### Get JWT Token

**Endpoint:** `POST /gotrue/token`

**Request:**
```bash
curl -X POST "http://appflowy.arknode-ai.home/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@arknode.local",
    "password": "your-password",
    "grant_type": "password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "email": "admin@arknode.local",
    "created_at": "2025-11-20T10:00:00Z"
  }
}
```

**Response Fields:**
- `access_token`: JWT token for API authentication (expires in 1 hour)
- `refresh_token`: Token to get new access token without password
- `expires_in`: Token lifetime in seconds (typically 3600)
- `user`: User information

### Refresh Token

**Endpoint:** `POST /gotrue/token`

**Request:**
```bash
curl -X POST "http://appflowy.arknode-ai.home/gotrue/token" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token",
    "grant_type": "refresh_token"
  }'
```

**Response:** Same as Get JWT Token response

### Using Token in Requests

**Authorization Header:**
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  -H "Content-Type: application/json"
```

### Python Authentication Example

```python
import os
import requests
from datetime import datetime, timedelta

class AppFlowyAuth:
    def __init__(self, api_url, email, password):
        self.api_url = api_url
        self.email = email
        self.password = password
        self.token = None
        self.refresh_token = None
        self.token_expires_at = None

    def authenticate(self):
        """Get new JWT token."""
        response = requests.post(
            f"{self.api_url}/gotrue/token",
            json={
                "email": self.email,
                "password": self.password,
                "grant_type": "password"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return self.token

    def refresh(self):
        """Refresh access token."""
        response = requests.post(
            f"{self.api_url}/gotrue/token",
            json={
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return self.token

    def get_valid_token(self):
        """Get valid token, refreshing if needed."""
        if not self.token or not self.token_expires_at:
            return self.authenticate()

        # Refresh if expiring in next 5 minutes
        if datetime.utcnow() + timedelta(minutes=5) > self.token_expires_at:
            return self.refresh()

        return self.token
```
</authentication>

---

## Workspace API

<workspace_api>
### List Workspaces

**Endpoint:** `GET /api/workspace`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "22bcbccd-9cf3-41ac-aa0b-28fe144ba71d",
    "name": "ArkNode Infrastructure",
    "created_at": "2025-11-20T10:00:00Z",
    "icon": "🏢",
    "member_count": 1
  }
]
```

### Get Workspace Details

**Endpoint:** `GET /api/workspace/{workspace_id}`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
{
  "id": "22bcbccd-9cf3-41ac-aa0b-28fe144ba71d",
  "name": "ArkNode Infrastructure",
  "created_at": "2025-11-20T10:00:00Z",
  "icon": "🏢",
  "member_count": 1,
  "databases": [
    {
      "id": "bb7a9c66-8088-4f71-a7b7-551f4c1adc5d",
      "name": "To-dos"
    }
  ]
}
```

### Get Workspace Folder Structure

**Endpoint:** `GET /api/workspace/{workspace_id}/folder`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/folder" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "folder-uuid-1",
    "name": "Projects",
    "type": "folder",
    "parent_id": null,
    "children": [
      {
        "id": "folder-uuid-2",
        "name": "Infrastructure",
        "type": "folder",
        "parent_id": "folder-uuid-1"
      }
    ]
  }
]
```

### Python Workspace API Example

```python
class WorkspaceAPI:
    def __init__(self, client):
        self.client = client

    def list_workspaces(self):
        """List all accessible workspaces."""
        return self.client._make_request('GET', '/api/workspace')

    def get_workspace(self, workspace_id):
        """Get workspace details."""
        return self.client._make_request('GET', f'/api/workspace/{workspace_id}')

    def get_folder_structure(self, workspace_id):
        """Get workspace folder structure."""
        return self.client._make_request('GET', f'/api/workspace/{workspace_id}/folder')

    def find_workspace_by_name(self, name):
        """Find workspace by name."""
        workspaces = self.list_workspaces()
        return next((w for w in workspaces if w['name'] == name), None)
```
</workspace_api>

---

## Database API

<database_api>
### List Databases

**Endpoint:** `GET /api/workspace/{workspace_id}/database`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "bb7a9c66-8088-4f71-a7b7-551f4c1adc5d",
    "name": "To-dos",
    "created_at": "2025-11-20T10:00:00Z",
    "row_count": 42,
    "field_count": 6
  }
]
```

### Get Database Fields

**Endpoint:** `GET /api/workspace/{workspace_id}/database/{database_id}/fields`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/fields" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "field-uuid-1",
    "name": "title",
    "type": "text",
    "is_primary": true
  },
  {
    "id": "field-uuid-2",
    "name": "status",
    "type": "select",
    "options": ["Todo", "In Progress", "Completed", "Blocked"]
  },
  {
    "id": "field-uuid-3",
    "name": "priority",
    "type": "select",
    "options": ["High", "Medium", "Low"]
  },
  {
    "id": "field-uuid-4",
    "name": "assignee",
    "type": "text"
  },
  {
    "id": "field-uuid-5",
    "name": "due_date",
    "type": "date"
  },
  {
    "id": "field-uuid-6",
    "name": "description",
    "type": "text"
  }
]
```

**Field Types:**
- `text`: Plain text
- `select`: Single select (dropdown)
- `multi_select`: Multiple selection
- `number`: Numeric value
- `date`: Date
- `checkbox`: Boolean (true/false)
- `url`: URL link
- `email`: Email address

### Python Database API Example

```python
class DatabaseAPI:
    def __init__(self, client):
        self.client = client

    def list_databases(self, workspace_id):
        """List databases in workspace."""
        endpoint = f'/api/workspace/{workspace_id}/database'
        return self.client._make_request('GET', endpoint)

    def get_database_fields(self, workspace_id, database_id):
        """Get database field definitions."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/fields'
        return self.client._make_request('GET', endpoint)

    def find_database_by_name(self, workspace_id, name):
        """Find database by name."""
        databases = self.list_databases(workspace_id)
        return next((db for db in databases if db['name'] == name), None)
```
</database_api>

---

## Row Operations

<row_operations>
### Get Database Rows

**Endpoint:** `GET /api/workspace/{workspace_id}/database/{database_id}/row`

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/row" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "row-uuid-1"
  },
  {
    "id": "row-uuid-2"
  }
]
```

**Note:** This endpoint returns only row IDs. Use Get Row Details to get full data.

### Get Row Details

**Endpoint:** `GET /api/workspace/{workspace_id}/database/{database_id}/row/detail`

**Query Parameters:**
- `row_ids`: Comma-separated list of row IDs

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/row/detail?row_ids=row-uuid-1,row-uuid-2" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "row-uuid-1",
    "title": "Implement user authentication",
    "status": "In Progress",
    "priority": "High",
    "assignee": "AI Agent",
    "due_date": "2025-12-15",
    "description": "Add JWT-based authentication with refresh tokens",
    "created_at": "2025-11-20T10:00:00Z",
    "updated_at": "2025-12-04T14:30:00Z"
  }
]
```

### Create Row

**Endpoint:** `POST /api/workspace/{workspace_id}/database/{database_id}/row`

**Request:**
```bash
curl -X POST "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/row" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review pull request #123",
    "status": "Todo",
    "priority": "Medium",
    "assignee": "Developer",
    "description": "Review changes in authentication module"
  }'
```

**Response:**
```json
{
  "id": "row-uuid-new",
  "title": "Review pull request #123",
  "status": "Todo",
  "priority": "Medium",
  "assignee": "Developer",
  "description": "Review changes in authentication module",
  "created_at": "2025-12-04T15:00:00Z"
}
```

### Update Row

**Endpoint:** `PUT /api/workspace/{workspace_id}/database/{database_id}/row`

**Request:**
```bash
curl -X PUT "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/row" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "row_id": "row-uuid-1",
    "status": "Completed",
    "completed_at": "2025-12-04T15:30:00Z"
  }'
```

**Response:**
```json
{
  "id": "row-uuid-1",
  "status": "Completed",
  "completed_at": "2025-12-04T15:30:00Z",
  "updated_at": "2025-12-04T15:30:00Z"
}
```

### Get Recently Updated Rows

**Endpoint:** `GET /api/workspace/{workspace_id}/database/{database_id}/row/updated`

**Query Parameters:**
- `since`: ISO 8601 timestamp (optional)

**Request:**
```bash
curl -X GET "http://appflowy.arknode-ai.home/api/workspace/22bcbccd-9cf3-41ac-aa0b-28fe144ba71d/database/bb7a9c66-8088-4f71-a7b7-551f4c1adc5d/row/updated?since=2025-12-04T00:00:00Z" \
  -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
```

**Response:**
```json
[
  {
    "id": "row-uuid-1",
    "updated_at": "2025-12-04T15:30:00Z"
  },
  {
    "id": "row-uuid-2",
    "updated_at": "2025-12-04T14:00:00Z"
  }
]
```

### Python Row Operations Example

```python
class RowAPI:
    def __init__(self, client):
        self.client = client

    def get_database_rows(self, workspace_id, database_id):
        """Get row IDs from database."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
        return self.client._make_request('GET', endpoint)

    def get_row_detail(self, workspace_id, database_id, row_ids):
        """Get detailed information for specific rows."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row/detail'
        params = {'row_ids': ','.join(row_ids)}
        return self.client._make_request('GET', endpoint, params=params)

    def create_row(self, workspace_id, database_id, data):
        """Create new row in database."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
        return self.client._make_request('POST', endpoint, json=data)

    def update_row(self, workspace_id, database_id, row_id, updates):
        """Update existing row."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row'
        data = {'row_id': row_id, **updates}
        return self.client._make_request('PUT', endpoint, json=data)

    def get_updated_rows(self, workspace_id, database_id, since_timestamp=None):
        """Get recently updated rows."""
        endpoint = f'/api/workspace/{workspace_id}/database/{database_id}/row/updated'
        params = {'since': since_timestamp} if since_timestamp else {}
        return self.client._make_request('GET', endpoint, params=params)
```
</row_operations>

---

## Field Operations

<field_operations>
### Field Types and Formats

**Text Field:**
```json
{
  "field_name": "string value"
}
```

**Select Field:**
```json
{
  "field_name": "option_value"
}
```

**Multi-Select Field:**
```json
{
  "field_name": ["option1", "option2"]
}
```

**Number Field:**
```json
{
  "field_name": 42
}
```

**Date Field:**
```json
{
  "field_name": "2025-12-15"
}
```

**Checkbox Field:**
```json
{
  "field_name": true
}
```

### Validate Field Data

```python
def validate_field_data(fields, data):
    """Validate data against field definitions."""
    validated = {}
    errors = []

    field_types = {f['name']: f['type'] for f in fields}
    field_options = {
        f['name']: f.get('options', [])
        for f in fields if f['type'] in ['select', 'multi_select']
    }

    for key, value in data.items():
        if key not in field_types:
            errors.append(f"Unknown field: {key}")
            continue

        field_type = field_types[key]

        # Validate select options
        if field_type == 'select' and key in field_options:
            if value not in field_options[key]:
                errors.append(f"Invalid option for {key}: {value}")
                continue

        # Validate multi-select options
        if field_type == 'multi_select' and key in field_options:
            invalid = [v for v in value if v not in field_options[key]]
            if invalid:
                errors.append(f"Invalid options for {key}: {invalid}")
                continue

        validated[key] = value

    return validated, errors
```
</field_operations>

---

## Error Handling

<error_handling>
### HTTP Status Codes

| Code | Meaning | Cause | Solution |
|------|---------|-------|----------|
| 200 | OK | Success | - |
| 201 | Created | Resource created | - |
| 400 | Bad Request | Invalid input | Check request format |
| 401 | Unauthorized | Invalid/expired token | Get new token |
| 403 | Forbidden | Insufficient permissions | Check workspace access |
| 404 | Not Found | Resource doesn't exist | Verify IDs |
| 429 | Too Many Requests | Rate limit exceeded | Implement backoff |
| 500 | Server Error | AppFlowy server issue | Check server logs |
| 503 | Service Unavailable | Server down/restarting | Wait and retry |

### Error Response Format

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": "Token expired at 2025-12-04T14:00:00Z"
  }
}
```

### Python Error Handling

```python
import logging
from requests.exceptions import RequestException, HTTPError

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

class AppFlowyRateLimitError(AppFlowyAPIError):
    """Rate limit exceeded."""
    pass

def handle_api_error(response):
    """Handle API error responses."""
    status_code = response.status_code

    if status_code == 401:
        raise AppFlowyAuthError("Authentication failed - check API token")
    elif status_code == 403:
        raise AppFlowyAuthError("Permission denied - check workspace access")
    elif status_code == 404:
        raise AppFlowyNotFoundError(f"Resource not found: {response.url}")
    elif status_code == 429:
        retry_after = response.headers.get('Retry-After', 60)
        raise AppFlowyRateLimitError(f"Rate limit exceeded, retry after {retry_after}s")
    elif status_code >= 500:
        raise AppFlowyAPIError(f"Server error: {status_code}")
    else:
        raise AppFlowyAPIError(f"API error {status_code}: {response.text}")

def safe_api_call(func):
    """Decorator for safe API calls."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            handle_api_error(e.response)
        except RequestException as e:
            logger.error(f"Network error: {e}")
            raise AppFlowyAPIError(f"Failed to connect to AppFlowy: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    return wrapper
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_error(max_retries=3, backoff=2):
    """Retry failed requests with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except AppFlowyRateLimitError as e:
                    wait_time = backoff ** retries
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    retries += 1
                except AppFlowyAPIError as e:
                    if retries < max_retries - 1:
                        wait_time = backoff ** retries
                        logger.warning(f"API error, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        raise
            raise AppFlowyAPIError(f"Max retries ({max_retries}) exceeded")
        return wrapper
    return decorator

# Usage
@retry_on_error(max_retries=3, backoff=2)
@safe_api_call
def create_row_with_retry(client, workspace_id, database_id, data):
    return client.create_row(workspace_id, database_id, data)
```
</error_handling>

---

## Rate Limiting

<rate_limiting>
### Rate Limit Headers

AppFlowy may return these headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying (on 429)

### Client-Side Rate Limiting

```python
import time
from functools import wraps
from collections import deque

class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.call_times = deque()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove calls older than 1 minute
        while self.call_times and self.call_times[0] < now - 60:
            self.call_times.popleft()

        # Check if we're at the limit
        if len(self.call_times) >= self.calls_per_minute:
            # Wait until oldest call is more than 60s ago
            sleep_time = 60 - (now - self.call_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Record this call
        self.call_times.append(time.time())

# Global rate limiter
rate_limiter = RateLimiter(calls_per_minute=60)

def rate_limited(func):
    """Decorator to enforce rate limiting."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait_if_needed()
        return func(*args, **kwargs)
    return wrapper

# Usage
@rate_limited
def create_row(client, workspace_id, database_id, data):
    return client.create_row(workspace_id, database_id, data)
```

### Batch Operations with Rate Limiting

```python
def batch_create_rows_with_rate_limit(client, workspace_id, database_id, rows_data, batch_size=10):
    """Create rows in batches to respect rate limits."""
    results = []
    total = len(rows_data)

    for i in range(0, total, batch_size):
        batch = rows_data[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")

        for data in batch:
            try:
                result = create_row_with_retry(client, workspace_id, database_id, data)
                results.append({'success': True, 'data': result})
            except Exception as e:
                results.append({'success': False, 'error': str(e), 'data': data})

        # Pause between batches
        if i + batch_size < total:
            time.sleep(1)

    return results
```
</rate_limiting>

---

## Complete Client Example

<complete_client>
```python
import os
import time
import logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, RequestException
import requests

logger = logging.getLogger(__name__)

class AppFlowyClient:
    """Complete AppFlowy REST API client with authentication, error handling, and rate limiting."""

    def __init__(self, api_url=None, email=None, password=None):
        self.api_url = api_url or os.getenv('APPFLOWY_API_URL')
        self.email = email or os.getenv('APPFLOWY_EMAIL')
        self.password = password or os.getenv('APPFLOWY_PASSWORD')
        self.workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')

        self.token = None
        self.refresh_token = None
        self.token_expires_at = None

        # Rate limiting
        self.rate_limiter = RateLimiter(calls_per_minute=60)

    def authenticate(self):
        """Get new JWT token."""
        response = requests.post(
            f"{self.api_url}/gotrue/token",
            json={
                "email": self.email,
                "password": self.password,
                "grant_type": "password"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        logger.info(f"Authenticated, token expires at {self.token_expires_at}")

    def _get_valid_token(self):
        """Get valid token, refreshing if needed."""
        if not self.token or not self.token_expires_at:
            self.authenticate()
        elif datetime.utcnow() + timedelta(minutes=5) > self.token_expires_at:
            self._refresh_token()
        return self.token

    def _refresh_token(self):
        """Refresh access token."""
        response = requests.post(
            f"{self.api_url}/gotrue/token",
            json={
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        logger.info("Token refreshed")

    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated API request with rate limiting and error handling."""
        self.rate_limiter.wait_if_needed()

        token = self._get_valid_token()
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers

        url = f"{self.api_url}{endpoint}"

        try:
            response = requests.request(method, url, **kwargs)

            # Retry once on 401
            if response.status_code == 401:
                logger.warning("Token expired, re-authenticating...")
                self.authenticate()
                headers['Authorization'] = f'Bearer {self.token}'
                response = requests.request(method, url, **kwargs)

            response.raise_for_status()
            return response.json()

        except HTTPError as e:
            handle_api_error(e.response)
        except RequestException as e:
            logger.error(f"Network error: {e}")
            raise AppFlowyAPIError(f"Failed to connect: {e}")

    # Workspace API
    def list_workspaces(self):
        return self._make_request('GET', '/api/workspace')

    def get_workspace(self, workspace_id):
        return self._make_request('GET', f'/api/workspace/{workspace_id}')

    # Database API
    def list_databases(self, workspace_id):
        return self._make_request('GET', f'/api/workspace/{workspace_id}/database')

    def get_database_fields(self, workspace_id, database_id):
        return self._make_request('GET', f'/api/workspace/{workspace_id}/database/{database_id}/fields')

    # Row API
    def get_database_rows(self, workspace_id, database_id):
        return self._make_request('GET', f'/api/workspace/{workspace_id}/database/{database_id}/row')

    def get_row_detail(self, workspace_id, database_id, row_ids):
        params = {'row_ids': ','.join(row_ids)}
        return self._make_request('GET', f'/api/workspace/{workspace_id}/database/{database_id}/row/detail', params=params)

    def create_row(self, workspace_id, database_id, data):
        return self._make_request('POST', f'/api/workspace/{workspace_id}/database/{database_id}/row', json=data)

    def update_row(self, workspace_id, database_id, row_id, updates):
        data = {'row_id': row_id, **updates}
        return self._make_request('PUT', f'/api/workspace/{workspace_id}/database/{database_id}/row', json=data)

    def get_updated_rows(self, workspace_id, database_id, since_timestamp=None):
        params = {'since': since_timestamp} if since_timestamp else {}
        return self._make_request('GET', f'/api/workspace/{workspace_id}/database/{database_id}/row/updated', params=params)
```
</complete_client>

---

## Related Documentation

- **Task Management**: See `workflows/task-management.md` for task operations
- **Workspace Operations**: See `workflows/workspace-operations.md` for workspace management
- **Troubleshooting**: See `workflows/troubleshooting.md` for common issues
- **Setup Guide**: See `references/setup_guide.md` for deployment instructions
