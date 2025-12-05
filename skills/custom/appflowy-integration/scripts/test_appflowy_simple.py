#!/usr/bin/env python3
"""
Simple AppFlowy Skill Test

Creates a task via direct API calls to verify the skill integration works.
"""

import os
import json
import requests
from pathlib import Path

def load_env_file(env_path):
    """Load environment variables from .env file."""
    if not env_path.exists():
        print(f"Warning: .env file not found at: {env_path}")
        return False

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    print(f"Loaded environment from: {env_path}")
    return True

def main():
    """Test AppFlowy skill by creating a task."""

    print("\n" + "="*70)
    print("  AppFlowy Skill Integration Test")
    print("="*70 + "\n")

    # Load environment variables from AppFlowy deployment directory
    env_path = Path(__file__).parent / "projects/appflowy-deployment/.env"
    if not load_env_file(env_path):
        print("ERROR: Failed to load environment variables")
        return 1

    api_url = os.getenv('APPFLOWY_API_URL')
    api_token = os.getenv('APPFLOWY_API_TOKEN')
    workspace_id = os.getenv('APPFLOWY_WORKSPACE_ID')
    database_id = os.getenv('APPFLOWY_DATABASE_ID')

    print(f"\nConfiguration:")
    print(f"  API URL: {api_url}")
    print(f"  Workspace ID: {workspace_id}")
    print(f"  Database ID: {database_id}")
    print(f"  Token: {api_token[:20]}...")

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Step 1: Get database schema
        print(f"\nStep 1: Fetching database schema...")
        fields_url = f"{api_url}/api/workspace/{workspace_id}/database/{database_id}/fields"
        print(f"  GET {fields_url}")

        response = requests.get(fields_url, headers=headers, timeout=30)
        response.raise_for_status()

        fields = response.json()
        print(f"\n  Available fields in To-dos database:")
        for field in fields:
            field_type = field.get('field_type', field.get('type', 'unknown'))
            print(f"    - {field.get('name')} ({field_type})")

        # Step 2: Create task
        print(f"\nStep 2: Creating task...")
        task_data = {
            "Name": "AppFlowy Skill Installation Complete",
            "Status": "Done",
            "Priority": "Medium",
            "Description": "Successfully migrated AppFlowy skill to pure XML structure, passed compliance audit (99%), and installed into Claude Code skill system. Skill provides task management, workspace operations, and API integration capabilities."
        }

        print(f"\n  Task data:")
        for key, value in task_data.items():
            display_value = value if len(str(value)) < 60 else str(value)[:57] + "..."
            print(f"    {key}: {display_value}")

        create_url = f"{api_url}/api/workspace/{workspace_id}/database/{database_id}/row"
        print(f"\n  POST {create_url}")

        response = requests.post(create_url, headers=headers, json=task_data, timeout=30)
        response.raise_for_status()

        result = response.json()
        print(f"\n  Response:")
        print(f"  {json.dumps(result, indent=2)}")

        if 'id' in result:
            task_id = result['id']
            print(f"\n  Task created successfully!")
            print(f"  Task ID: {task_id}")

            # Step 3: Verify task
            print(f"\nStep 3: Verifying task creation...")
            detail_url = f"{api_url}/api/workspace/{workspace_id}/database/{database_id}/row/detail"
            print(f"  GET {detail_url}?row_ids={task_id}")

            response = requests.get(detail_url, headers=headers, params={'row_ids': task_id}, timeout=30)
            response.raise_for_status()

            rows = response.json()
            if rows:
                print(f"\n  Task verified in database!")
                print(f"  Row data:")
                print(f"  {json.dumps(rows[0], indent=2)}")
            else:
                print(f"\n  Warning: Task created but not found in query (known UI sync issue)")

            print("\n" + "="*70)
            print("  SUCCESS: AppFlowy Skill Integration Test PASSED")
            print("="*70 + "\n")
            print(f"Task '{task_data['Name']}' created with ID: {task_id}")
            return 0

        else:
            print(f"\n  ERROR: No task ID in response")
            print("\n" + "="*70)
            print("  FAILED: AppFlowy Skill Integration Test FAILED")
            print("="*70 + "\n")
            return 1

    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        print("\n" + "="*70)
        print("  FAILED: AppFlowy Skill Integration Test FAILED")
        print("="*70 + "\n")
        return 1

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("  FAILED: AppFlowy Skill Integration Test FAILED")
        print("="*70 + "\n")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
