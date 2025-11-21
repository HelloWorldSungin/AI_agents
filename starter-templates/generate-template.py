#!/usr/bin/env python3
"""
AI Agents Library - Project Template Generator

This script generates a complete AI agents setup for your existing project.
It creates all necessary configuration files, context documents, and directory structure.

Usage:
    python generate-template.py --type web-app --name "MyProject" --output /path/to/project
    python generate-template.py --type mobile-app --name "MobileApp" --output ~/Projects/app
    python generate-template.py --interactive
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Template types and their descriptions
TEMPLATE_TYPES = {
    "web-app": "Full-stack web application (React/Vue + Node.js/Python)",
    "mobile-app": "Mobile application (React Native, Flutter, or native)",
    "full-stack": "Complete full-stack application with multiple services",
    "api-service": "Backend API service or microservice",
    "data-pipeline": "Data processing pipeline or analytics project",
}


class TemplateGenerator:
    """Generates AI agents setup for existing projects."""

    def __init__(self, template_type: str, project_name: str, output_path: Path):
        self.template_type = template_type
        self.project_name = project_name
        self.output_path = output_path
        self.template_path = Path(__file__).parent / template_type

    def generate(self):
        """Generate the complete template."""
        print(f"🎯 Generating {self.template_type} template for: {self.project_name}")
        print(f"📂 Output directory: {self.output_path}")
        print()

        # Create .ai-agents directory structure
        self._create_directory_structure()

        # Copy and customize template files
        self._copy_context_files()
        self._create_config_file()
        self._create_readme()
        self._create_gitignore()

        print()
        print("✅ Template generated successfully!")
        print()
        print("📋 Next steps:")
        print("1. Review and customize files in .ai-agents/context/")
        print("2. Update .ai-agents/config.yml with your specific needs")
        print("3. Run: python .ai-agents/library/scripts/compose-agent.py --config .ai-agents/config.yml --all")
        print("4. Use the composed agents in .ai-agents/composed/")
        print()
        print(f"📖 See .ai-agents/README.md for detailed instructions")

    def _create_directory_structure(self):
        """Create the .ai-agents directory structure."""
        print("📁 Creating directory structure...")

        ai_dir = self.output_path / ".ai-agents"
        directories = [
            "context",
            "composed",
            "state",
            "checkpoints",
            "memory",
            "workflows",
        ]

        for dir_name in directories:
            dir_path = ai_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ Created: .ai-agents/{dir_name}/")

    def _copy_context_files(self):
        """Copy and customize context template files."""
        print()
        print("📄 Creating context files...")

        context_dir = self.output_path / ".ai-agents" / "context"
        template_context = self.template_path / "context"

        if template_context.exists():
            for template_file in template_context.glob("*.md"):
                content = template_file.read_text()
                # Replace placeholders
                content = content.replace("{{PROJECT_NAME}}", self.project_name)

                output_file = context_dir / template_file.name
                output_file.write_text(content)
                print(f"   ✓ Created: context/{template_file.name}")

    def _create_config_file(self):
        """Create the agent configuration file."""
        print()
        print("⚙️  Creating configuration...")

        config_template = self.template_path / "config.yml"
        if config_template.exists():
            content = config_template.read_text()
            content = content.replace("{{PROJECT_NAME}}", self.project_name)

            config_file = self.output_path / ".ai-agents" / "config.yml"
            config_file.write_text(content)
            print(f"   ✓ Created: .ai-agents/config.yml")

    def _create_readme(self):
        """Create README for the AI agents setup."""
        print()
        print("📖 Creating documentation...")

        readme_content = f"""# AI Agents Setup for {self.project_name}

This directory contains the AI agents configuration for your project.

## Quick Start

### 1. Add AI Agents Library (if not already added)

```bash
git submodule add https://github.com/your-org/AI_agents.git .ai-agents/library
git submodule update --init --recursive
```

### 2. Customize Your Configuration

Edit these files to match your project:

- `context/architecture.md` - Your system architecture and tech stack
- `context/api-contracts.md` - Your API specifications
- `context/coding-standards.md` - Your team's coding conventions
- `context/current-features.md` - What's built and what's planned
- `config.yml` - Agent configuration and skills

### 3. Compose Your Agents

```bash
cd .ai-agents/library
python3 scripts/compose-agent.py --config ../../config.yml --all
```

This generates complete agent prompts in `.ai-agents/composed/`

### 4. Use Your Agents

Copy the composed prompts and paste them into Claude or your LLM API:

```bash
# Example: Use the frontend developer agent
cat .ai-agents/composed/frontend_developer.md | pbcopy
```

Then paste into Claude and give it a task!

## Directory Structure

```
.ai-agents/
├── library/           # AI Agents Library (submodule)
├── context/          # Your project-specific context
│   ├── architecture.md
│   ├── api-contracts.md
│   ├── coding-standards.md
│   └── current-features.md
├── config.yml        # Agent configuration
├── composed/         # Generated agent prompts (DO NOT EDIT)
├── state/           # Agent state tracking
├── checkpoints/     # Conversation checkpoints
├── memory/          # Project memory/RAG
└── workflows/       # Custom workflows
```

## Available Agents

Check `config.yml` to see which agents are configured for your project.

Common agents:
- **frontend_developer** - UI/component development
- **backend_developer** - API and database work
- **qa_tester** - Automated testing
- **team_manager** - Coordination and planning

## Updating Agents

When your project evolves, update the context files and recompose:

```bash
# Edit context files
vi .ai-agents/context/current-features.md

# Recompose agents
cd .ai-agents/library
python3 scripts/compose-agent.py --config ../../config.yml --all
```

## Documentation

- [AI Agents Library README](.ai-agents/library/README.md)
- [Skills Guide](.ai-agents/library/SKILLS_GUIDE.md)
- [Migration Guide](.ai-agents/library/MIGRATION_GUIDE.md)

## Support

Need help? Check the documentation in `.ai-agents/library/` or open an issue.

---

Generated for **{self.project_name}** ({self.template_type} template)
"""

        readme_file = self.output_path / ".ai-agents" / "README.md"
        readme_file.write_text(readme_content)
        print(f"   ✓ Created: .ai-agents/README.md")

    def _create_gitignore(self):
        """Create .gitignore for AI agents directory."""
        gitignore_content = """# AI Agents - Generated files
composed/
state/
checkpoints/

# Keep these in version control
!context/
!config.yml
!README.md
"""

        gitignore_file = self.output_path / ".ai-agents" / ".gitignore"
        gitignore_file.write_text(gitignore_content)
        print(f"   ✓ Created: .ai-agents/.gitignore")


def interactive_mode():
    """Run generator in interactive mode."""
    print("🤖 AI Agents Library - Interactive Template Generator")
    print("=" * 60)
    print()

    # Select template type
    print("Available template types:")
    for i, (key, desc) in enumerate(TEMPLATE_TYPES.items(), 1):
        print(f"{i}. {key:15} - {desc}")
    print()

    while True:
        choice = input("Select template type (1-5): ").strip()
        try:
            template_type = list(TEMPLATE_TYPES.keys())[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")

    # Get project name
    project_name = input("\nProject name: ").strip()
    if not project_name:
        print("Error: Project name cannot be empty")
        sys.exit(1)

    # Get output path
    default_output = Path.cwd()
    output_input = input(f"\nOutput directory [{default_output}]: ").strip()
    output_path = Path(output_input) if output_input else default_output

    print()
    print("Configuration:")
    print(f"  Template: {template_type}")
    print(f"  Project:  {project_name}")
    print(f"  Output:   {output_path}")
    print()

    confirm = input("Generate template? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    print()
    generator = TemplateGenerator(template_type, project_name, output_path)
    generator.generate()


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI agents setup for your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--type",
        choices=list(TEMPLATE_TYPES.keys()),
        help="Type of project template",
    )

    parser.add_argument(
        "--name",
        help="Project name",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: current directory)",
        default=Path.cwd(),
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive or (not args.type and not args.name):
        interactive_mode()
        return

    # Command-line mode
    if not args.type or not args.name:
        parser.error("--type and --name are required (or use --interactive)")

    generator = TemplateGenerator(args.type, args.name, args.output)
    generator.generate()


if __name__ == "__main__":
    main()
