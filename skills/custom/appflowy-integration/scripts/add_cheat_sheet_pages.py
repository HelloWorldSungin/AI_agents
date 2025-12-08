#!/usr/bin/env python3
"""
Add Missing Cheat Sheet Pages to AppFlowy

Creates nested pages inside "Cheat Sheet Index" for all cheat sheet documents.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from update_page_content import load_credentials, markdown_to_blocks, append_blocks_to_page


# Cheat Sheet Index page ID (parent for all cheat sheet pages)
CHEAT_SHEET_INDEX_PAGE_ID = "1623381e-e896-4119-92d1-431d23f376e7"

# Files to sync (file_path -> page_name)
CHEAT_SHEET_FILES = {
    "docs/reference/CHEAT_SHEET/02-agents.md": "Agents",
    "docs/reference/CHEAT_SHEET/03-skills.md": "Skills",
    "docs/reference/CHEAT_SHEET/04-commands.md": "Commands",
    "docs/reference/CHEAT_SHEET/05-workflows.md": "Workflows",
    "docs/reference/CHEAT_SHEET/06-scripts-tools.md": "Scripts & Tools",
    "docs/reference/CHEAT_SHEET/07-advanced.md": "Advanced",
    "docs/reference/CHEAT_SHEET/08-schemas.md": "Schemas",
    "docs/reference/CHEAT_SHEET/09-best-practices.md": "Best Practices",
    "docs/reference/CHEAT_SHEET/10-reference.md": "Reference"
}


def create_page(
    api_url: str,
    workspace_id: str,
    parent_view_id: str,
    page_name: str,
    token: str
) -> Dict[str, Any]:
    """
    Create a new page in AppFlowy as a child of parent_view_id.

    Args:
        api_url: Base AppFlowy API URL
        workspace_id: Workspace ID
        parent_view_id: Parent page ID
        page_name: Name for the new page
        token: JWT authentication token

    Returns:
        API response containing the new page's view_id
    """
    endpoint = f"{api_url}/api/workspace/{workspace_id}/page-view"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "parent_view_id": parent_view_id,
        "name": page_name,
        "layout": 0  # 0 = Document layout for text pages
    }

    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to create page: {response.status_code} - {response.text}")

    return response.json()


def add_cheat_sheet_page(
    file_path: str,
    page_name: str,
    credentials: Dict[str, str],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Create a cheat sheet page and populate it with content.

    Args:
        file_path: Path to markdown file (relative to repo root)
        page_name: Name for the page in AppFlowy
        credentials: API credentials
        dry_run: If True, only show what would be done

    Returns:
        Result dictionary with page_id and status
    """
    repo_root = Path("/Users/sunginkim/GIT/AI_agents")
    markdown_path = repo_root / file_path

    if not markdown_path.exists():
        return {
            "status": "error",
            "file_path": file_path,
            "page_name": page_name,
            "error": f"File not found: {markdown_path}"
        }

    # Read and convert markdown
    with open(markdown_path) as f:
        markdown_content = f.read()

    blocks = markdown_to_blocks(markdown_content)

    result = {
        "file_path": file_path,
        "page_name": page_name,
        "blocks_count": len(blocks),
        "dry_run": dry_run
    }

    if dry_run:
        result["message"] = "DRY RUN - Would create page and add blocks"
        result["blocks_preview"] = blocks[:3]
        return result

    try:
        # Step 1: Create the page
        print(f"  Creating page: {page_name}...")
        create_response = create_page(
            api_url=credentials["APPFLOWY_API_URL"],
            workspace_id=credentials["APPFLOWY_WORKSPACE_ID"],
            parent_view_id=CHEAT_SHEET_INDEX_PAGE_ID,
            page_name=page_name,
            token=credentials["APPFLOWY_API_TOKEN"]
        )

        # The API returns view_id nested in 'data' object
        page_id = create_response.get("data", {}).get("view_id")
        if not page_id:
            raise Exception(f"No view_id in create response: {create_response}")

        result["page_id"] = page_id
        print(f"    ✓ Page created with ID: {page_id}")

        # Step 2: Add content blocks
        print(f"  Adding {len(blocks)} blocks...")
        append_response = append_blocks_to_page(
            api_url=credentials["APPFLOWY_API_URL"],
            workspace_id=credentials["APPFLOWY_WORKSPACE_ID"],
            page_id=page_id,
            blocks=blocks,
            token=credentials["APPFLOWY_API_TOKEN"]
        )

        result["status"] = "success"
        result["api_response"] = append_response
        print(f"    ✓ Content added successfully")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"    ✗ Error: {e}")

    return result


def load_sync_status() -> Dict[str, Any]:
    """Load sync status file."""
    status_path = Path("/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/.sync-status.json")

    if not status_path.exists():
        return {"last_sync": "", "synced_files": {}, "folder_ids": {}}

    with open(status_path) as f:
        return json.load(f)


def save_sync_status(status: Dict[str, Any]) -> None:
    """Save updated sync status."""
    status_path = Path("/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/.sync-status.json")

    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2)


def update_sync_status_for_page(
    sync_status: Dict[str, Any],
    file_path: str,
    page_id: str,
    page_name: str,
    markdown_content: str
) -> None:
    """Update sync status with new page info."""
    import hashlib
    from datetime import datetime, timezone

    # Calculate hash
    content_hash = hashlib.md5(markdown_content.encode()).hexdigest()

    # Add to synced_files
    sync_status["synced_files"][file_path] = {
        "hash": content_hash,
        "page_id": page_id,
        "page_name": page_name,
        "folder_name": "Cheat Sheet Index",
        "last_sync": datetime.now(timezone.utc).isoformat()
    }


def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    print("=" * 70)
    print("Adding Missing Cheat Sheet Pages to AppFlowy")
    print("=" * 70)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    # Load credentials
    try:
        credentials = load_credentials()
        print(f"✓ Loaded credentials")
        print(f"  API URL: {credentials['APPFLOWY_API_URL']}")
        print(f"  Workspace ID: {credentials['APPFLOWY_WORKSPACE_ID']}")
        print(f"  Parent Page ID: {CHEAT_SHEET_INDEX_PAGE_ID}")
        print()
    except Exception as e:
        print(f"✗ Failed to load credentials: {e}")
        sys.exit(1)

    # Load sync status
    sync_status = load_sync_status()

    # Process each file
    results = []
    repo_root = Path("/Users/sunginkim/GIT/AI_agents")

    print(f"Processing {len(CHEAT_SHEET_FILES)} cheat sheet pages:")
    print()

    for file_path, page_name in CHEAT_SHEET_FILES.items():
        print(f"[{len(results) + 1}/{len(CHEAT_SHEET_FILES)}] {page_name}")

        result = add_cheat_sheet_page(
            file_path=file_path,
            page_name=page_name,
            credentials=credentials,
            dry_run=dry_run
        )

        results.append(result)

        # Update sync status if successful
        if not dry_run and result.get("status") == "success":
            markdown_path = repo_root / file_path
            with open(markdown_path) as f:
                markdown_content = f.read()

            update_sync_status_for_page(
                sync_status=sync_status,
                file_path=file_path,
                page_id=result["page_id"],
                page_name=page_name,
                markdown_content=markdown_content
            )

        print()

    # Save updated sync status
    if not dry_run:
        from datetime import datetime, timezone
        sync_status["last_sync"] = datetime.now(timezone.utc).isoformat()
        save_sync_status(sync_status)
        print("✓ Updated sync status")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    print(f"Total pages: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print()

    if successful:
        print("✅ Successfully created pages:")
        for r in successful:
            page_url = f"{credentials['APPFLOWY_API_URL']}/view/{r['page_id']}"
            print(f"  - {r['page_name']} ({r['blocks_count']} blocks)")
            if not dry_run:
                print(f"    URL: {page_url}")

    if failed:
        print()
        print("❌ Failed pages:")
        for r in failed:
            print(f"  - {r['page_name']}: {r.get('error')}")

    print()
    print("=" * 70)

    if not dry_run and successful:
        print(f"✓ All pages created under 'Cheat Sheet Index'")
        print(f"  View at: {credentials['APPFLOWY_API_URL']}/view/{CHEAT_SHEET_INDEX_PAGE_ID}")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
