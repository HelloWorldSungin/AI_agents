#!/usr/bin/env python3
"""
Team Communication Validation Utility

Validates team-communication.json structure and size.

Usage:
    python scripts/validate-team-communication.py
"""

import json
import sys
from pathlib import Path

COMM_FILE = Path(".ai-agents/state/team-communication.json")
MAX_SAFE_TOKENS = 20000
CRITICAL_TOKENS = 25000

def validate_structure(data: dict) -> list:
    """Validate JSON structure"""
    errors = []

    # Required top-level keys
    required_keys = ["manager_instructions", "agent_updates", "shared_resources"]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    # Validate manager_instructions
    if "manager_instructions" in data:
        mgr = data["manager_instructions"]
        required_mgr = ["current_focus", "active_tasks"]
        for key in required_mgr:
            if key not in mgr:
                errors.append(f"Missing manager_instructions.{key}")

    return errors

def estimate_tokens(data: dict) -> int:
    """Estimate token count"""
    json_str = json.dumps(data, indent=2)
    return len(json_str) // 4

def validate_file() -> None:
    """Main validation"""

    if not COMM_FILE.exists():
        print(f"❌ Error: File not found: {COMM_FILE}")
        sys.exit(1)

    # Load file
    try:
        with open(COMM_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    # Validate structure
    errors = validate_structure(data)
    if errors:
        print("❌ Structure validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Check size
    tokens = estimate_tokens(data)
    print(f"\n📊 File Size: ~{tokens:,} tokens")

    if tokens < MAX_SAFE_TOKENS:
        print("✅ Size OK")
    elif tokens < CRITICAL_TOKENS:
        print("⚠️  Warning: Approaching token limit")
        print(f"   Recommend cleanup (max safe: {MAX_SAFE_TOKENS:,})")
    else:
        print("🔴 CRITICAL: File too large!")
        print(f"   Agents cannot read files > {CRITICAL_TOKENS:,} tokens")
        print("   Run cleanup immediately: python3 scripts/cleanup-team-communication.py")
        sys.exit(1)

    # Summary
    print(f"\n✅ Validation passed")
    print(f"   Agent updates: {len(data.get('agent_updates', []))}")
    print(f"   Active tasks: {len(data.get('manager_instructions', {}).get('active_tasks', []))}")
    print(f"   Completed tasks: {len(data.get('manager_instructions', {}).get('completed_tasks', []))}")

if __name__ == "__main__":
    validate_file()
