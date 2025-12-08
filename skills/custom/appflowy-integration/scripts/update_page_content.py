#!/usr/bin/env python3
"""
AppFlowy Page Content Updater

Converts markdown content to AppFlowy Delta block format and updates pages.
Uses the /api/workspace/{workspace_id}/page-view/{page_id}/append-block endpoint.
"""

import os
import sys
import json
import re
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_credentials() -> Dict[str, str]:
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

    required = ["APPFLOWY_API_URL", "APPFLOWY_WORKSPACE_ID", "APPFLOWY_API_TOKEN"]
    missing = [k for k in required if k not in credentials]
    if missing:
        raise ValueError(f"Missing required credentials: {missing}")

    return credentials


def load_sync_status() -> Dict[str, Any]:
    """Load sync status to get page IDs."""
    status_path = Path("/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/.sync-status.json")

    if not status_path.exists():
        raise FileNotFoundError(f"Sync status file not found: {status_path}")

    with open(status_path) as f:
        return json.load(f)


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


def parse_table(lines: List[str], start_idx: int) -> tuple:
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


def append_blocks_to_page(
    api_url: str,
    workspace_id: str,
    page_id: str,
    blocks: List[Dict[str, Any]],
    token: str
) -> Dict[str, Any]:
    """
    Append blocks to an AppFlowy page using the append-block endpoint.

    Args:
        api_url: Base AppFlowy API URL
        workspace_id: Workspace ID
        page_id: Target page ID
        blocks: List of block objects to append
        token: JWT authentication token

    Returns:
        API response as dictionary
    """
    endpoint = f"{api_url}/api/workspace/{workspace_id}/page-view/{page_id}/append-block"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {"blocks": blocks}

    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    return response.json()


def update_page_from_markdown(
    markdown_path: str,
    page_id: str,
    credentials: Dict[str, str],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Read markdown file, convert to blocks, and update AppFlowy page.

    Args:
        markdown_path: Path to markdown file
        page_id: Target page ID in AppFlowy
        credentials: API credentials dictionary
        dry_run: If True, only show what would be sent without making API call

    Returns:
        Result dictionary with status and metadata
    """
    # Read markdown file
    md_path = Path(markdown_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    with open(md_path) as f:
        markdown_content = f.read()

    # Convert to blocks
    blocks = markdown_to_blocks(markdown_content)

    result = {
        "markdown_path": str(md_path),
        "page_id": page_id,
        "blocks_count": len(blocks),
        "dry_run": dry_run
    }

    if dry_run:
        result["blocks_preview"] = blocks[:3]  # Show first 3 blocks
        result["message"] = "DRY RUN - No API call made"
        return result

    # Make API call
    try:
        api_response = append_blocks_to_page(
            api_url=credentials["APPFLOWY_API_URL"],
            workspace_id=credentials["APPFLOWY_WORKSPACE_ID"],
            page_id=page_id,
            blocks=blocks,
            token=credentials["APPFLOWY_API_TOKEN"]
        )

        result["status"] = "success"
        result["api_response"] = api_response

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python update_page_content.py <file_key> [--dry-run]")
        print("\nExamples:")
        print("  python update_page_content.py README.md --dry-run")
        print("  python update_page_content.py README.md")
        print("  python update_page_content.py docs/guides/ARCHITECTURE.md")
        sys.exit(1)

    file_key = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # Load credentials and sync status
    try:
        credentials = load_credentials()
        sync_status = load_sync_status()
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        sys.exit(1)

    # Find page info
    synced_files = sync_status.get("synced_files", {})
    if file_key not in synced_files:
        print(f"ERROR: File '{file_key}' not found in sync status")
        print(f"Available files: {', '.join(synced_files.keys())}")
        sys.exit(1)

    page_info = synced_files[file_key]
    page_id = page_info["page_id"]
    page_name = page_info["page_name"]

    # Construct markdown path
    repo_root = Path("/Users/sunginkim/GIT/AI_agents")
    markdown_path = repo_root / file_key

    print(f"{'[DRY RUN] ' if dry_run else ''}Updating AppFlowy page...")
    print(f"  File: {file_key}")
    print(f"  Page: {page_name}")
    print(f"  Page ID: {page_id}")
    print()

    # Update page
    try:
        result = update_page_from_markdown(
            markdown_path=str(markdown_path),
            page_id=page_id,
            credentials=credentials,
            dry_run=dry_run
        )

        print(f"Status: {result.get('status', 'completed')}")
        print(f"Blocks created: {result['blocks_count']}")

        if dry_run:
            print("\nFirst 3 blocks preview:")
            print(json.dumps(result['blocks_preview'], indent=2))
        else:
            if result.get("status") == "success":
                print("\n✅ Page updated successfully!")
                print(f"View at: {credentials['APPFLOWY_API_URL']}/view/{page_id}")
            else:
                print(f"\n❌ Update failed: {result.get('error')}")
                sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
