#!/usr/bin/env python3
"""
Verify AppFlowy page content by fetching it via the API.

Usage:
    python verify_page_content.py <file_key>
"""

import sys
import json
import requests
from pathlib import Path
from update_page_content import load_credentials, load_sync_status


def get_page_content(api_url: str, workspace_id: str, page_id: str, token: str):
    """Fetch page content from AppFlowy API."""
    endpoint = f"{api_url}/api/workspace/{workspace_id}/page-view/{page_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    return response.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_page_content.py <file_key>")
        print("\nExample: python verify_page_content.py README.md")
        sys.exit(1)

    file_key = sys.argv[1]

    # Load configuration
    try:
        credentials = load_credentials()
        sync_status = load_sync_status()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Find page
    synced_files = sync_status.get("synced_files", {})
    if file_key not in synced_files:
        print(f"ERROR: File '{file_key}' not found")
        sys.exit(1)

    page_info = synced_files[file_key]
    page_id = page_info["page_id"]
    page_name = page_info["page_name"]

    print(f"Fetching page content...")
    print(f"  Page: {page_name}")
    print(f"  Page ID: {page_id}")
    print()

    try:
        content = get_page_content(
            api_url=credentials["APPFLOWY_API_URL"],
            workspace_id=credentials["APPFLOWY_WORKSPACE_ID"],
            page_id=page_id,
            token=credentials["APPFLOWY_API_TOKEN"]
        )

        print("✅ Page retrieved successfully!")
        print()
        print("Response structure:")
        print(json.dumps(content, indent=2)[:1000] + "..." if len(json.dumps(content)) > 1000 else json.dumps(content, indent=2))

    except Exception as e:
        print(f"❌ Failed to retrieve page: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
