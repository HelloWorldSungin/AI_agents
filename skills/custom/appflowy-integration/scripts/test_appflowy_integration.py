#!/usr/bin/env python3
"""
Test script for AppFlowy AI Agent Integration
Phase 4: Create test task via API
"""

import os
import sys
import json
import requests
from datetime import datetime

# Configuration
API_URL = "http://192.168.68.55"
WORKSPACE_ID = "22bcbccd-9cf3-41ac-aa0b-28fe144ba71d"
DATABASE_ID = "bb7a9c66-8088-4f71-a7b7-551f4c1adc5d"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3NTExOWIwZi03MjMyLTQ4NmQtYjA0Ny1hODYxYTVlMmNkY2QiLCJhdWQiOiIiLCJleHAiOjE3NjU0MTc2MjMsImlhdCI6MTc2NDgxMjgyMywiZW1haWwiOiJhZG1pbkBhcmtub2RlLmxvY2FsIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6ImFkbWluQGFya25vZGUubG9jYWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJBZG1pbiBVc2VyIiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI3NTExOWIwZi03MjMyLTQ4NmQtYjA0Ny1hODYxYTVlMmNkY2QifSwicm9sZSI6IiIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY0ODEyODIzfV0sInNlc3Npb25faWQiOiIwOTU0ZDdiMS1jNWYxLTRjNDctODQ4MC05MjA1NzU1YjQxZGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.G_d75QUSzTi46sqv6wrFAGok910XKEZopCHWG5Ah4bA"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_connection():
    """Test API connection by fetching workspaces"""
    print("\n=== Testing API Connection ===")
    response = requests.get(f"{API_URL}/api/workspace", headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"✓ Connected to AppFlowy API")
    print(f"✓ Found {len(data['data'])} workspaces")
    return True

def get_database_fields():
    """Get field definitions for the database"""
    print("\n=== Fetching Database Fields ===")
    url = f"{API_URL}/api/workspace/{WORKSPACE_ID}/database/{DATABASE_ID}/fields"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    fields = response.json()
    print(f"✓ Database fields retrieved")
    print(f"Fields: {json.dumps(fields, indent=2)}")
    return fields

def get_existing_rows():
    """Get existing rows to understand the structure"""
    print("\n=== Fetching Existing Rows ===")
    url = f"{API_URL}/api/workspace/{WORKSPACE_ID}/database/{DATABASE_ID}/row"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    rows = response.json()
    print(f"✓ Found {len(rows.get('data', []))} existing rows")
    if rows.get('data'):
        print(f"Sample row: {json.dumps(rows['data'][0], indent=2)}")
    return rows

def create_test_task():
    """Create a test task using the API"""
    print("\n=== Creating Test Task ===")

    # Task data
    task_data = {
        "data": {
            "Name": "Test Task - AI Agent Integration",
            "Description": "This task was created by the AI agent to verify AppFlowy API integration"
        }
    }

    url = f"{API_URL}/api/workspace/{WORKSPACE_ID}/database/{DATABASE_ID}/row"
    print(f"URL: {url}")
    print(f"Data: {json.dumps(task_data, indent=2)}")

    response = requests.post(url, headers=headers, json=task_data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print(f"✓ Test task created successfully!")
        print(f"Task details: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"✗ Failed to create task: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def main():
    """Main test flow"""
    print("=" * 60)
    print("AppFlowy AI Agent Integration Test - Phase 4")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    try:
        # Test connection
        test_connection()

        # Get database fields
        fields = get_database_fields()

        # Get existing rows
        rows = get_existing_rows()

        # Create test task
        result = create_test_task()

        if result:
            print("\n" + "=" * 60)
            print("✓✓✓ PHASE 4 TEST SUCCESSFUL ✓✓✓")
            print("=" * 60)
            print("\nNext Steps:")
            print("1. Open AppFlowy UI at http://appflowy.arknode-ai.home")
            print("2. Login with admin@arknode.local")
            print("3. Navigate to 'ArkNode Infrastructure' workspace")
            print("4. Open 'To-dos' database")
            print("5. Verify 'Test Task - AI Agent Integration' appears")
            print("\nReady to proceed to Phase 5: Multi-Project Structure")
        else:
            print("\n" + "=" * 60)
            print("✗✗✗ PHASE 4 TEST FAILED ✗✗✗")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
