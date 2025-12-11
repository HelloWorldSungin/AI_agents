#!/usr/bin/env python3
"""
Verify page content by fetching it from AppFlowy API.
Shows what was actually created in the test pages.
"""

import sys
import json
import requests
from pathlib import Path


def load_credentials():
    """Load AppFlowy credentials from .env file."""
    env_path = Path("/Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env")

    if not env_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {env_path}")

    credentials = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                credentials[key.strip()] = value.strip()

    return credentials


def get_page_content(api_url: str, workspace_id: str, page_id: str, token: str):
    """Fetch page content from AppFlowy."""
    # Note: This endpoint may not exist - AppFlowy API docs are limited
    # We'll try a few different endpoints

    endpoints_to_try = [
        f"{api_url}/api/workspace/{workspace_id}/page-view/{page_id}",
        f"{api_url}/api/workspace/{workspace_id}/document/{page_id}",
        f"{api_url}/api/workspace/{workspace_id}/page/{page_id}",
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    for endpoint in endpoints_to_try:
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            continue

    return None


def main():
    """Verify the test pages."""

    # Test page IDs from the test run
    code_block_page_id = "d5030ef5-ac17-4915-a7a0-8f7b431c6f74"
    grid_view_page_id = "3bb5e0b8-8397-4c1f-be20-fc8dcbbebf08"

    try:
        creds = load_credentials()
        api_url = creds["APPFLOWY_API_URL"]
        workspace_id = creds["APPFLOWY_WORKSPACE_ID"]
        token = creds["APPFLOWY_API_TOKEN"]

        print("="*70)
        print("VERIFYING TEST PAGES")
        print("="*70)

        # Code Block page
        print(f"\n1. Code Block Approach Page")
        print(f"   Page ID: {code_block_page_id}")
        print(f"   URL: {api_url}/view/{code_block_page_id}")

        content = get_page_content(api_url, workspace_id, code_block_page_id, token)
        if content:
            print(f"\n   ✓ Page content retrieved:")
            print(json.dumps(content, indent=2)[:500] + "...")
        else:
            print(f"\n   ℹ️  Note: Page content API endpoint not available")
            print(f"   → Visit URL in browser to view content")

        # Grid View page
        print(f"\n2. Grid View Approach Page")
        print(f"   Page ID: {grid_view_page_id}")
        print(f"   URL: {api_url}/view/{grid_view_page_id}")

        content = get_page_content(api_url, workspace_id, grid_view_page_id, token)
        if content:
            print(f"\n   ✓ Page content retrieved:")
            print(json.dumps(content, indent=2)[:500] + "...")
        else:
            print(f"\n   ℹ️  Note: Page content API endpoint not available")
            print(f"   → Visit URL in browser to view content")

        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70)
        print("\nTo see the full rendered pages:")
        print(f"1. Code Block: {api_url}/view/{code_block_page_id}")
        print(f"2. Grid View:  {api_url}/view/{grid_view_page_id}")
        print("\nExpected in Code Block page:")
        print("  - Rich text with bold, italic, code, links, strikethrough")
        print("  - Two tables rendered as code blocks")
        print("  - All formatting preserved")
        print("\nExpected in Grid View page:")
        print("  - Introduction with rich text")
        print("  - Two child Grid views (empty, awaiting manual setup)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
