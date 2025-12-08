#!/usr/bin/env python3
"""
Batch update all synced pages in AppFlowy from their markdown sources.

Usage:
    python batch_update_all.py [--dry-run]
"""

import sys
import json
from pathlib import Path
from update_page_content import (
    load_credentials,
    load_sync_status,
    update_page_from_markdown
)


def batch_update_all(dry_run: bool = False):
    """Update all synced pages from their markdown sources."""

    # Load configuration
    try:
        credentials = load_credentials()
        sync_status = load_sync_status()
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        sys.exit(1)

    synced_files = sync_status.get("synced_files", {})
    total_files = len(synced_files)
    repo_root = Path("/Users/sunginkim/GIT/AI_agents")

    print(f"{'[DRY RUN] ' if dry_run else ''}Batch updating {total_files} pages...")
    print()

    results = {
        "success": [],
        "failed": [],
        "total": total_files
    }

    for idx, (file_key, page_info) in enumerate(synced_files.items(), 1):
        page_id = page_info["page_id"]
        page_name = page_info["page_name"]
        folder = page_info.get("folder_name", "N/A")

        print(f"[{idx}/{total_files}] {file_key}")
        print(f"  Page: {page_name} (Folder: {folder})")

        markdown_path = repo_root / file_key

        if not markdown_path.exists():
            print(f"  ⚠️  Markdown file not found: {markdown_path}")
            results["failed"].append({
                "file": file_key,
                "error": "File not found"
            })
            print()
            continue

        try:
            result = update_page_from_markdown(
                markdown_path=str(markdown_path),
                page_id=page_id,
                credentials=credentials,
                dry_run=dry_run
            )

            if result.get("status") == "success" or dry_run:
                print(f"  ✅ {result['blocks_count']} blocks")
                results["success"].append({
                    "file": file_key,
                    "page": page_name,
                    "blocks": result["blocks_count"]
                })
            else:
                print(f"  ❌ Failed: {result.get('error')}")
                results["failed"].append({
                    "file": file_key,
                    "error": result.get("error")
                })

        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results["failed"].append({
                "file": file_key,
                "error": str(e)
            })

        print()

    # Summary
    print("=" * 60)
    print("BATCH UPDATE SUMMARY")
    print("=" * 60)
    print(f"Total files: {results['total']}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    print()

    if results["failed"]:
        print("Failed updates:")
        for item in results["failed"]:
            print(f"  - {item['file']}: {item['error']}")
        print()

    if not dry_run:
        print(f"✅ All updates completed!")
        print(f"View workspace: {credentials['APPFLOWY_API_URL']}")
    else:
        print("ℹ️  DRY RUN - No actual updates were made")

    return results


def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("Running in DRY RUN mode - no actual updates will be made")
        print()

    results = batch_update_all(dry_run=dry_run)

    # Exit with error code if any updates failed
    if results["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
