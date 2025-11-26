#!/usr/bin/env python3
"""
Tool Selector Setup Script

Generates minimal wrapper commands in a target project's .claude/commands/
that redirect to the full implementations in the AI_agents repo.

Usage:
    python setup-commands.py                    # Install to current project
    python setup-commands.py /path/to/project   # Install to specific project
    python setup-commands.py --global           # Install to ~/.claude/commands/
    python setup-commands.py --list             # List available tools without installing
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Get the AI_agents repo root (where this script lives)
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent

# Source locations
TACHES_COMMANDS = REPO_ROOT / "taches-cc-resources" / "commands"
TACHES_SKILLS = REPO_ROOT / "taches-cc-resources" / "skills"
LOCAL_COMMANDS = REPO_ROOT / ".claude" / "commands"
LOCAL_SKILLS = REPO_ROOT / "skills"

# Categories for the /ai-tools router
TOOL_CATEGORIES = {
    "Prompt Engineering": [
        "create-prompt",
        "create-meta-prompt",
        "run-prompt",
    ],
    "Agent Development": [
        "create-subagent",
        "create-agent-skill",
        "create-hook",
    ],
    "Slash Commands": [
        "create-slash-command",
        "audit-slash-command",
        "audit-skill",
        "audit-subagent",
        "heal-skill",
    ],
    "Planning & Execution": [
        "create-plan",
        "run-plan",
    ],
    "Debugging": [
        "debug",
    ],
    "Task Management": [
        "add-to-todos",
        "check-todos",
        "whats-next",
    ],
    "Thinking Models": [
        "consider:first-principles",
        "consider:5-whys",
        "consider:swot",
        "consider:devil-advocate",
        "consider:premortem",
        "consider:inversion",
        "consider:socratic",
        "consider:red-team",
        "consider:steel-man",
        "consider:opportunity-cost",
        "consider:second-order",
        "consider:pareto",
    ],
}


def parse_frontmatter(file_path: Path) -> Dict:
    """Extract YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return {"description": f"Command from {file_path.stem}"}

        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {"description": f"Command from {file_path.stem}"}

        frontmatter = content[3:end_idx].strip()
        return yaml.safe_load(frontmatter) or {}
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return {"description": f"Command from {file_path.stem}"}


def discover_tools() -> Dict[str, Dict]:
    """Discover all available tools from taches-cc-resources and local commands."""
    tools = {}

    # Discover commands from taches-cc-resources
    if TACHES_COMMANDS.exists():
        for cmd_file in TACHES_COMMANDS.glob("*.md"):
            name = cmd_file.stem
            meta = parse_frontmatter(cmd_file)
            tools[name] = {
                "name": name,
                "type": "command",
                "source": str(cmd_file),
                "description": meta.get("description", f"Command: {name}"),
                "argument_hint": meta.get("argument-hint", ""),
            }

        # Discover consider/* subcommands
        consider_dir = TACHES_COMMANDS / "consider"
        if consider_dir.exists():
            for cmd_file in consider_dir.glob("*.md"):
                name = f"consider:{cmd_file.stem}"
                meta = parse_frontmatter(cmd_file)
                tools[name] = {
                    "name": name,
                    "type": "command",
                    "source": str(cmd_file),
                    "description": meta.get("description", f"Thinking model: {cmd_file.stem}"),
                    "argument_hint": meta.get("argument-hint", ""),
                }

    # Discover skills from taches-cc-resources
    if TACHES_SKILLS.exists():
        for skill_dir in TACHES_SKILLS.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    name = skill_dir.name
                    meta = parse_frontmatter(skill_file)
                    tools[f"skill:{name}"] = {
                        "name": name,
                        "type": "skill",
                        "source": str(skill_file),
                        "description": meta.get("description", f"Skill: {name}"),
                    }

    return tools


def generate_wrapper(tool: Dict, repo_path: Path) -> str:
    """Generate a minimal wrapper command that redirects to the source."""
    name = tool["name"]
    desc = tool["description"]
    source = tool["source"]
    arg_hint = tool.get("argument_hint", "")

    # For skills, create a Skill() invocation wrapper
    if tool["type"] == "skill":
        return f"""---
description: {desc}
allowed-tools: Skill({name})
argument-hint: {arg_hint if arg_hint else "[arguments]"}
---

Invoke the {name} skill for: $ARGUMENTS
"""

    # For commands, read and execute the source
    # Use relative path from wrapper location to source
    rel_path = os.path.relpath(source, repo_path / ".claude" / "commands")

    return f"""---
description: {desc}
argument-hint: {arg_hint if arg_hint else ""}
---

Read and execute the command at: {source}

Pass these arguments: $ARGUMENTS
"""


def generate_router_command(tools: Dict[str, Dict], repo_path: Path) -> str:
    """Generate the /ai-tools discovery router command."""

    # Build category listings
    category_text = ""
    for category, tool_names in TOOL_CATEGORIES.items():
        available_tools = []
        for name in tool_names:
            if name in tools:
                t = tools[name]
                available_tools.append(f"  - `/{name}` - {t['description']}")

        if available_tools:
            category_text += f"\n### {category}\n" + "\n".join(available_tools) + "\n"

    # Add skills section
    skill_tools = [t for name, t in tools.items() if t["type"] == "skill"]
    if skill_tools:
        category_text += "\n### Skills (invoke with Skill() tool)\n"
        for t in skill_tools:
            category_text += f"  - `{t['name']}` - {t['description']}\n"

    return f"""---
description: Discover and explore available AI agent tools from AI_agents repo
---

<objective>
Help users discover and understand the AI agent tools available from the AI_agents repository.
</objective>

<available_tools>
{category_text}
</available_tools>

<usage>
**Run a command:**
```
/create-prompt [your task description]
/debug [error or symptom]
/consider:first-principles [problem to analyze]
```

**Invoke a skill:**
```
Use the Skill() tool: Skill(create-plans)
```

**Get help:**
```
/ai-tools - Show this list
```
</usage>

<source>
These tools come from: {repo_path}

To update or customize, edit the source files directly.
</source>
"""


def install_skills(target_dir: Path, tools: Dict[str, Dict], repo_path: Path) -> List[str]:
    """Install skills by creating symlinks to .claude/skills/."""
    installed = []

    # Skills directory is sibling to commands
    skills_dir = target_dir.parent / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for name, tool in tools.items():
        if not name.startswith("skill:"):
            continue

        skill_name = tool["name"]
        source_path = Path(tool["source"]).parent  # Get directory containing SKILL.md
        target_path = skills_dir / skill_name

        # Remove existing symlink or directory if it exists
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.exists():
            print(f"  Warning: {target_path} exists and is not a symlink, skipping")
            continue

        # Create symlink
        try:
            target_path.symlink_to(source_path)
            installed.append(str(target_path))
        except OSError as e:
            print(f"  Warning: Could not create symlink for {skill_name}: {e}")

    return installed


def install_wrappers(target_dir: Path, tools: Dict[str, Dict], repo_path: Path) -> List[str]:
    """Install wrapper commands to the target directory."""
    installed = []

    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    # Create consider subdirectory
    consider_dir = target_dir / "consider"
    consider_dir.mkdir(exist_ok=True)

    for name, tool in tools.items():
        # Determine output path
        if name.startswith("consider:"):
            subname = name.split(":", 1)[1]
            output_path = consider_dir / f"{subname}.md"
        elif name.startswith("skill:"):
            # Skills are installed separately via install_skills()
            continue
        else:
            output_path = target_dir / f"{name}.md"

        # Generate and write wrapper
        wrapper_content = generate_wrapper(tool, repo_path)
        output_path.write_text(wrapper_content)
        installed.append(str(output_path))

    # Generate and write router command
    router_path = target_dir / "ai-tools.md"
    router_content = generate_router_command(tools, repo_path)
    router_path.write_text(router_content)
    installed.append(str(router_path))

    return installed


def list_tools(tools: Dict[str, Dict]) -> None:
    """Print available tools without installing."""
    print("\nAvailable AI Agent Tools")
    print("=" * 50)

    for category, tool_names in TOOL_CATEGORIES.items():
        available = [n for n in tool_names if n in tools]
        if available:
            print(f"\n{category}:")
            for name in available:
                t = tools[name]
                print(f"  /{name:<25} {t['description'][:50]}")

    # List skills
    skills = [t for n, t in tools.items() if t["type"] == "skill"]
    if skills:
        print(f"\nSkills (use Skill() tool):")
        for t in skills:
            print(f"  {t['name']:<27} {t['description'][:50]}")

    print(f"\nTotal: {len(tools)} tools available")


def main():
    args = sys.argv[1:]

    # Handle --list flag
    if "--list" in args:
        tools = discover_tools()
        list_tools(tools)
        return

    # Determine target directory
    if "--global" in args:
        target_dir = Path.home() / ".claude" / "commands"
        print(f"Installing to global commands: {target_dir}")
    elif args and not args[0].startswith("-"):
        project_path = Path(args[0]).resolve()
        target_dir = project_path / ".claude" / "commands"
        print(f"Installing to project: {project_path}")
    else:
        # Current working directory
        target_dir = Path.cwd() / ".claude" / "commands"
        print(f"Installing to current project: {Path.cwd()}")

    # Discover tools
    print("\nDiscovering tools...")
    tools = discover_tools()
    print(f"Found {len(tools)} tools")

    # Install wrappers
    print(f"\nInstalling command wrappers to {target_dir}...")
    installed_commands = install_wrappers(target_dir, tools, REPO_ROOT)

    # Install skills
    print(f"\nInstalling skill symlinks to {target_dir.parent / 'skills'}...")
    installed_skills = install_skills(target_dir, tools, REPO_ROOT)

    print(f"\nInstalled {len(installed_commands)} command wrappers:")
    for path in installed_commands[:10]:
        print(f"  - {path}")
    if len(installed_commands) > 10:
        print(f"  ... and {len(installed_commands) - 10} more")

    if installed_skills:
        print(f"\nInstalled {len(installed_skills)} skill symlinks:")
        for path in installed_skills:
            print(f"  - {path}")

    print(f"\nDone! Use /ai-tools to discover available commands.")


if __name__ == "__main__":
    main()
