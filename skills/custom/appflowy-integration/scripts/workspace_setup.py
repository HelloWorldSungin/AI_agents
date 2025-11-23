#!/usr/bin/env python3
"""
AppFlowy Workspace Setup

Helper script for setting up new project workspaces in AppFlowy.
Automates the process of configuring a workspace for a new project.

Usage:
    # Interactive setup
    python workspace_setup.py

    # Command-line setup
    python workspace_setup.py --project "New AI Project" --auto
"""

import sys
import argparse
from datetime import datetime

try:
    from appflowy_client import AppFlowyClient, AppFlowyError
except ImportError:
    print("Error: appflowy_client.py not found. Ensure it's in the same directory.")
    sys.exit(1)


class WorkspaceSetup:
    """Helper for setting up project workspaces."""

    def __init__(self):
        """Initialize workspace setup helper."""
        self.client = AppFlowyClient()

    def create_project_workspace(self, project_name, team_members=None, auto=False):
        """
        Create or configure a workspace for a new project.

        Args:
            project_name: Name of the project/workspace
            team_members: List of team member emails (optional)
            auto: If True, skip confirmations

        Returns:
            Dictionary with workspace configuration
        """
        print(f"\n{'='*70}")
        print(f"Setting up workspace for: {project_name}")
        print(f"{'='*70}\n")

        # 1. Find or prompt for workspace
        workspaces = self.client.list_workspaces()

        if not workspaces:
            print("❌ No workspaces found. Please create a workspace in AppFlowy first.")
            print("\nSteps to create a workspace:")
            print("1. Open AppFlowy in your browser")
            print("2. Click '+' to create a new workspace")
            print(f"3. Name it: {project_name}")
            print("4. Run this script again")
            return None

        print(f"Found {len(workspaces)} workspace(s):")
        for i, ws in enumerate(workspaces, 1):
            print(f"  {i}. {ws.get('name', 'Unnamed')} (ID: {ws.get('id')})")

        # Find workspace by name or let user choose
        workspace = next(
            (w for w in workspaces if w.get('name') == project_name),
            None
        )

        if not workspace:
            if not auto:
                print(f"\n⚠️  Workspace '{project_name}' not found.")
                choice = input("Choose workspace number (or 'n' to create new): ").strip()

                if choice.lower() == 'n':
                    print("\nPlease create the workspace in AppFlowy UI first:")
                    print(f"1. Open AppFlowy → Create new workspace")
                    print(f"2. Name: {project_name}")
                    print("3. Run this script again")
                    return None

                try:
                    workspace = workspaces[int(choice) - 1]
                except (ValueError, IndexError):
                    print("❌ Invalid choice")
                    return None
            else:
                print(f"❌ Workspace '{project_name}' not found and auto mode is enabled")
                return None

        workspace_id = workspace['id']
        workspace_name = workspace.get('name', 'Unnamed')
        print(f"\n✅ Using workspace: {workspace_name} (ID: {workspace_id})")

        # 2. Check for Tasks database
        databases = self.client.list_databases(workspace_id)
        print(f"\nFound {len(databases)} database(s) in workspace:")
        for db in databases:
            print(f"  - {db.get('name', 'Unnamed')} (ID: {db.get('id')})")

        tasks_db = next((db for db in databases if db.get('name') == 'Tasks'), None)

        if not tasks_db:
            print("\n⚠️  'Tasks' database not found.")
            print("\nPlease create a 'Tasks' database with these fields:")
            print("  - title (text) - required")
            print("  - status (select) - Todo, In Progress, Completed, Blocked")
            print("  - priority (select) - High, Medium, Low")
            print("  - assignee (text)")
            print("  - due_date (date)")
            print("  - description (text)")
            print("  - tags (multi-select)")

            if not auto:
                input("\nPress Enter after creating the database...")
                # Refresh database list
                databases = self.client.list_databases(workspace_id)
                tasks_db = next((db for db in databases if db.get('name') == 'Tasks'), None)

                if not tasks_db:
                    print("❌ Tasks database still not found")
                    return None
            else:
                return None

        print(f"✅ Tasks database found (ID: {tasks_db['id']})")

        # 3. Verify database fields
        try:
            fields = self.client.get_database_fields(tasks_db['id'], workspace_id)
            field_names = [f.get('name') for f in fields]
            print(f"\nDatabase fields: {', '.join(field_names)}")

            required_fields = ['title', 'status', 'priority']
            missing = [f for f in required_fields if f not in field_names]
            if missing:
                print(f"⚠️  Warning: Missing recommended fields: {', '.join(missing)}")
        except Exception as e:
            print(f"⚠️  Could not verify fields: {e}")

        # 4. Create initial setup task
        print("\n📝 Creating initial project setup task...")

        setup_task = {
            'title': f'🚀 Project Setup: {project_name}',
            'description': (
                f'Project workspace initialized on {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}\n\n'
                f'Next steps:\n'
                f'- Review project requirements\n'
                f'- Set up development environment\n'
                f'- Configure CI/CD pipeline\n'
                f'- Create initial documentation'
            ),
            'status': 'In Progress',
            'priority': 'High',
        }

        if 'assignee' in field_names and not auto:
            assignee = input("Assignee for setup task (default: Project Lead): ").strip()
            setup_task['assignee'] = assignee or 'Project Lead'
        elif 'assignee' in field_names:
            setup_task['assignee'] = 'Project Lead'

        try:
            # Validate task data against schema
            validated_task = self.client.validate_task_data(
                tasks_db['id'],
                setup_task,
                workspace_id
            )

            task = self.client.create_row(tasks_db['id'], validated_task, workspace_id)
            print(f"✅ Created setup task (ID: {task.get('id')})")
        except Exception as e:
            print(f"⚠️  Could not create setup task: {e}")

        # 5. Generate configuration
        config = {
            'workspace_id': workspace_id,
            'workspace_name': workspace_name,
            'tasks_database_id': tasks_db['id'],
            'project_name': project_name,
            'setup_date': datetime.utcnow().isoformat() + 'Z',
            'team_members': team_members or [],
        }

        # 6. Display summary
        print(f"\n{'='*70}")
        print("✅ Workspace Setup Complete!")
        print(f"{'='*70}\n")
        print(f"Project: {project_name}")
        print(f"Workspace ID: {workspace_id}")
        print(f"Tasks Database ID: {tasks_db['id']}")

        if team_members:
            print(f"Team Members: {', '.join(team_members)}")

        print("\n📋 Environment Variables:")
        print(f"export APPFLOWY_WORKSPACE_ID='{workspace_id}'")
        print(f"export APPFLOWY_TASKS_DB_ID='{tasks_db['id']}'")

        print("\n💡 Next Steps:")
        print("1. Add the environment variables to your .env file")
        print("2. Configure agent configs to use this workspace")
        print("3. Start creating tasks for your project")
        print("4. Invite team members in AppFlowy UI")

        # Save config to file
        try:
            import json
            config_file = f".appflowy_{project_name.lower().replace(' ', '_')}.json"
            with open(config_file, 'w') as f:
                json.dump(config, indent=2, fp=f)
            print(f"\n💾 Configuration saved to: {config_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save config file: {e}")

        return config


def main():
    """CLI for workspace setup."""
    parser = argparse.ArgumentParser(
        description='Set up AppFlowy workspace for a new project'
    )

    parser.add_argument(
        '--project', '-p',
        help='Project name'
    )
    parser.add_argument(
        '--team', '-t',
        nargs='+',
        help='Team member emails'
    )
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='Automatic mode (skip confirmations)'
    )

    args = parser.parse_args()

    try:
        setup = WorkspaceSetup()

        # Get project name
        if args.project:
            project_name = args.project
        else:
            project_name = input("\nEnter project name: ").strip()
            if not project_name:
                print("❌ Project name is required")
                sys.exit(1)

        # Get team members
        team_members = args.team
        if not team_members and not args.auto:
            members_input = input("Team member emails (comma-separated, optional): ").strip()
            if members_input:
                team_members = [m.strip() for m in members_input.split(',')]

        # Run setup
        config = setup.create_project_workspace(
            project_name,
            team_members,
            auto=args.auto
        )

        if not config:
            print("\n❌ Setup failed or incomplete")
            sys.exit(1)

    except AppFlowyError as e:
        print(f"\n❌ AppFlowy error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
