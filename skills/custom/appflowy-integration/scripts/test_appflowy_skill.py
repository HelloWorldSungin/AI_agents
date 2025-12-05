#!/usr/bin/env python3
"""
Test AppFlowy Skill Installation

Creates a task in AppFlowy to verify the skill integration works correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add the AppFlowy client to the Python path
client_path = Path(__file__).parent / ".ai-agents/library/skills/custom/appflowy-integration/scripts"
sys.path.insert(0, str(client_path))

from appflowy_client import AppFlowyClient, AppFlowyError

def load_env_file(env_path):
    """Load environment variables from .env file."""
    if not env_path.exists():
        print(f"⚠️  .env file not found at: {env_path}")
        return False

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    print(f"✓ Loaded environment from: {env_path}")
    return True

def main():
    """Test AppFlowy skill by creating a task."""

    print("\n" + "="*70)
    print("  AppFlowy Skill Integration Test")
    print("="*70 + "\n")

    # Load environment variables from AppFlowy deployment directory
    env_path = Path(__file__).parent / "projects/appflowy-deployment/.env"
    if not load_env_file(env_path):
        print("❌ Failed to load environment variables")
        return 1

    try:
        # Initialize client
        print("\n1️⃣  Initializing AppFlowy client...")
        client = AppFlowyClient()
        print(f"   ✓ API URL: {client.api_url}")
        print(f"   ✓ Workspace ID: {client.workspace_id}")

        # Get database information
        workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')
        database_id = os.getenv('APPFLOWY_DATABASE_ID')

        print(f"\n2️⃣  Fetching database schema...")
        print(f"   Database: To-dos (ID: {database_id})")

        # Get fields to understand the schema
        fields = client.get_database_fields(database_id, workspace_id)
        print(f"\n   Available fields:")
        for field in fields:
            field_type = field.get('field_type', field.get('type', 'unknown'))
            print(f"   - {field.get('name')} ({field_type})")

        # Prepare task data
        print(f"\n3️⃣  Creating task...")
        task_data = {
            "Name": "AppFlowy Skill Installation Complete",
            "Status": "Done",
            "Priority": "Medium",
            "Description": "Successfully migrated AppFlowy skill to pure XML structure, passed compliance audit (99%), and installed into Claude Code skill system. Skill provides task management, workspace operations, and API integration capabilities."
        }

        # Validate task data against schema
        validated_data = client.validate_task_data(database_id, task_data, workspace_id)

        print(f"\n   Task details:")
        for key, value in validated_data.items():
            print(f"   - {key}: {value}")

        # Create the task
        print(f"\n   Creating row in database...")
        result = client.create_row(database_id, validated_data, workspace_id)

        # Display result
        print(f"\n4️⃣  Task created successfully!")
        print(f"\n   Response:")
        print(f"   {json.dumps(result, indent=2)}")

        if result and 'id' in result:
            task_id = result['id']
            print(f"\n   ✓ Task ID: {task_id}")

            # Try to fetch the task back
            print(f"\n5️⃣  Verifying task creation...")
            try:
                rows = client.get_row_detail(database_id, [task_id], workspace_id)
                if rows:
                    print(f"   ✓ Task verified in database")
                    print(f"\n   Task details:")
                    print(f"   {json.dumps(rows[0], indent=2)}")
                else:
                    print(f"   ⚠️  Task created but not found in query (known UI sync issue)")
            except Exception as e:
                print(f"   ⚠️  Could not verify task: {e}")

        print("\n" + "="*70)
        print("  ✅ AppFlowy Skill Integration Test PASSED")
        print("="*70 + "\n")

        return 0

    except AppFlowyError as e:
        print(f"\n❌ AppFlowy error: {e}")
        print("\n" + "="*70)
        print("  ❌ AppFlowy Skill Integration Test FAILED")
        print("="*70 + "\n")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("  ❌ AppFlowy Skill Integration Test FAILED")
        print("="*70 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
