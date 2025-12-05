#!/usr/bin/env python3
"""
Team Communication Cleanup Utility

Reduces team-communication.json file size by archiving old data
while preserving essential context.

Usage:
    python scripts/cleanup-team-communication.py [--dry-run]
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

COMM_FILE = Path(".ai-agents/state/team-communication.json")
ARCHIVE_DIR = Path(".ai-agents/state/archive")
MAX_AGENT_UPDATES = 10  # Keep only last 10 updates
MAX_COMPLETED_TASKS = 5  # Keep only last 5 completed tasks

def estimate_tokens(data: Dict) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    json_str = json.dumps(data, indent=2)
    return len(json_str) // 4

def archive_old_data(comm_data: Dict) -> Path:
    """Archive old agent updates and completed tasks"""

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_file = ARCHIVE_DIR / f"team-communication-{timestamp}.json"

    # Create archive directory
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Archive full history
    with open(archive_file, 'w') as f:
        json.dump(comm_data, f, indent=2)

    print(f"✓ Archived to: {archive_file}")

    return archive_file

def cleanup_agent_updates(comm_data: Dict) -> Dict:
    """Keep only the most recent agent updates"""

    agent_updates = comm_data.get("agent_updates", [])
    original_count = len(agent_updates)

    if original_count > MAX_AGENT_UPDATES:
        # Sort by timestamp (most recent first)
        sorted_updates = sorted(
            agent_updates,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        # Keep only recent updates
        comm_data["agent_updates"] = sorted_updates[:MAX_AGENT_UPDATES]

        removed = original_count - MAX_AGENT_UPDATES
        print(f"✓ Removed {removed} old agent updates (kept {MAX_AGENT_UPDATES})")

    return comm_data

def cleanup_completed_tasks(comm_data: Dict) -> Dict:
    """Move old completed tasks to archive, keep recent ones"""

    if "manager_instructions" not in comm_data:
        return comm_data

    completed = comm_data["manager_instructions"].get("completed_tasks", [])
    original_count = len(completed)

    if original_count > MAX_COMPLETED_TASKS:
        # Sort by completion timestamp (most recent first)
        sorted_completed = sorted(
            completed,
            key=lambda x: x.get("completed_at", ""),
            reverse=True
        )

        # Keep only recent completions
        comm_data["manager_instructions"]["completed_tasks"] = sorted_completed[:MAX_COMPLETED_TASKS]

        removed = original_count - MAX_COMPLETED_TASKS
        print(f"✓ Removed {removed} old completed tasks (kept {MAX_COMPLETED_TASKS})")

    return comm_data

def cleanup_communication_file(dry_run: bool = False) -> None:
    """Main cleanup function"""

    if not COMM_FILE.exists():
        print(f"Error: Communication file not found: {COMM_FILE}")
        sys.exit(1)

    # Read current file
    with open(COMM_FILE, 'r') as f:
        comm_data = json.load(f)

    # Calculate initial size
    initial_tokens = estimate_tokens(comm_data)
    print(f"\nInitial size: ~{initial_tokens:,} tokens")

    if initial_tokens < 20000:
        print("✓ File size is acceptable. No cleanup needed.")
        return

    print(f"\n⚠️  File size exceeds 20,000 tokens. Starting cleanup...")

    # Archive full history
    archive_file = archive_old_data(comm_data)

    # Cleanup operations
    comm_data = cleanup_agent_updates(comm_data)
    comm_data = cleanup_completed_tasks(comm_data)

    # Update timestamp
    comm_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    comm_data["last_cleanup"] = datetime.utcnow().isoformat() + "Z"
    comm_data["cleanup_archive"] = str(archive_file)

    # Calculate final size
    final_tokens = estimate_tokens(comm_data)
    reduction = initial_tokens - final_tokens
    reduction_pct = (reduction / initial_tokens) * 100

    print(f"\nFinal size: ~{final_tokens:,} tokens")
    print(f"Reduction: ~{reduction:,} tokens ({reduction_pct:.1f}%)")

    if dry_run:
        print("\n[DRY RUN] Would write cleaned file to:", COMM_FILE)
    else:
        # Write cleaned file
        with open(COMM_FILE, 'w') as f:
            json.dump(comm_data, f, indent=2)
        print(f"\n✅ Cleanup complete! File written to: {COMM_FILE}")
        print(f"📦 Full history preserved in: {archive_file}")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    cleanup_communication_file(dry_run)
