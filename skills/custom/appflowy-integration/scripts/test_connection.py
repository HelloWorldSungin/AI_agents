#!/usr/bin/env python3
"""
Quick test script to verify AppFlowy connection and database setup.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sync_docs_database import (
    load_env_file,
    validate_environment,
    AppFlowyClient,
    AppFlowyAPIError,
    logger
)


def main():
    """Test connection and database setup."""
    print("=" * 60)
    print("AppFlowy Connection & Database Test")
    print("=" * 60)

    try:
        # Load environment
        load_env_file()

        # Validate environment
        try:
            api_url, api_token, workspace_id, database_id = validate_environment()
            print(f"✓ Environment variables loaded")
            print(f"  - API URL: {api_url}")
            print(f"  - Workspace ID: {workspace_id}")
            print(f"  - Database ID: {database_id}")
        except ValueError as e:
            print(f"✗ {e}")
            print("\nTo fix:")
            print("1. Create the Documentation database in AppFlowy")
            print("2. Add APPFLOWY_DOCS_DATABASE_ID to your .env file")
            print(f"3. Location: /Users/sunginkim/GIT2/ArkNode-AI/projects/appflowy-deployment/.env")
            return 1

        print()

        # Test connection
        print("Testing AppFlowy connection...")
        client = AppFlowyClient(api_url, api_token, workspace_id, database_id)

        try:
            workspaces = client.list_workspaces()
            print(f"✓ Connected - {len(workspaces)} workspace(s) accessible")
        except AppFlowyAPIError as e:
            print(f"✗ Connection failed: {e}")
            return 1

        print()

        # Test database access
        print("Testing database access...")
        try:
            schema = client.get_database_schema()
            print(f"✓ Database found")
        except AppFlowyAPIError as e:
            print(f"✗ Database not found: {e}")
            print("\nTo fix:")
            print("1. Verify the database ID in your .env file")
            print("2. Ensure the database exists in the AI Agents workspace")
            print("3. Check database permissions")
            return 1

        print()

        # Validate schema
        print("Validating database schema...")
        field_mapping = client.get_field_mapping()

        if not field_mapping:
            print("✗ No fields found in database")
            print("\nTo fix:")
            print("1. Open the Documentation database in AppFlowy")
            print("2. Create the required fields (see SETUP_DOCUMENTATION_DATABASE.md)")
            return 1

        print("Fields found:")
        for field_name, field_id in field_mapping.items():
            print(f"  - {field_name}: {field_id}")

        print()

        # Check required fields
        required_fields = {'Title', 'Content', 'Category', 'FilePath', 'LastUpdated'}
        missing_fields = required_fields - set(field_mapping.keys())

        if missing_fields:
            print(f"✗ Missing required fields: {', '.join(missing_fields)}")
            print("\nTo fix:")
            print("1. Open the Documentation database in AppFlowy")
            print("2. Create these fields:")
            for field in missing_fields:
                if field == 'Content':
                    print(f"   - {field} (Long Text)")
                elif field == 'Category':
                    print(f"   - {field} (Select: Getting Started, Guides, Reference, Examples)")
                elif field == 'FilePath':
                    print(f"   - {field} (Text)")
                elif field == 'LastUpdated':
                    print(f"   - {field} (Date)")
                elif field == 'Title':
                    print(f"   - {field} (Text, Primary)")
            return 1

        print("✓ All required fields present")
        print()

        # Success
        print("=" * 60)
        print("✓ Setup Complete!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python sync_docs_database.py --dry-run   # Test sync")
        print("  python sync_docs_database.py             # Sync documentation")
        print()

        return 0

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
