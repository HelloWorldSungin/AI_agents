#!/usr/bin/env python3
"""
CLI interface for Autonomous Runner (Two-Agent Pattern)

Implements Anthropic's recommended two-agent pattern:
1. `init` - Initializer agent: Analyzes specs and creates tasks
2. `start` - Coding agent: Executes tasks from state provider

Usage:
    # Phase 1: Initialize project from spec
    python -m scripts.autonomous init --spec requirements.md

    # Phase 2: Run coding agents
    python -m scripts.autonomous start [--config CONFIG] [--resume]

    # Other commands
    python -m scripts.autonomous status
    python -m scripts.autonomous stop
    python -m scripts.autonomous logs [--tail N]
    python -m scripts.autonomous tasks
    python -m scripts.autonomous resume
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def cmd_init(args):
    """
    Initialize project from spec/requirements file.

    This is the INITIALIZER AGENT - Phase 1 of the two-agent pattern.
    It analyzes requirements and creates tasks in the state provider.
    """
    from scripts.autonomous.initializer import ProjectInitializer, InitializerConfig

    config_path = args.config or ".ai-agents/config.yml"
    spec_path = args.spec

    # Check spec file
    if not os.path.exists(spec_path):
        print(f"Error: Spec file not found: {spec_path}")
        sys.exit(1)

    print("=" * 60)
    print("INITIALIZER AGENT - Phase 1 of Two-Agent Pattern")
    print("=" * 60)
    print(f"\nSpec file: {spec_path}")
    print(f"Config: {config_path}")
    if args.project_name:
        print(f"Project name: {args.project_name}")
    print("-" * 60)

    try:
        # Load config if exists, otherwise use defaults
        if os.path.exists(config_path):
            config = InitializerConfig.from_yaml(config_path)
        else:
            print(f"Note: Config file not found, using defaults")
            config = InitializerConfig()

        print(f"\nBackend: {config.backend}")
        print(f"Model: {config.model}")
        print("-" * 60)

        # Check if already initialized
        initializer = ProjectInitializer(config)

        if initializer.check_initialized() and not args.force:
            print("\nProject already initialized!")
            print("Use --force to re-initialize (will create new tasks)")

            state = initializer.get_project_state()
            if state:
                print(f"\nExisting project: {state.get('project_name')}")
                print(f"Tasks: {state.get('total_tasks')}")
                print(f"Initialized: {state.get('initialized_at')}")

            sys.exit(0)

        print("\nAnalyzing requirements...")
        result = initializer.initialize(
            spec_path=spec_path,
            project_name=args.project_name
        )

        print("\n" + "=" * 60)
        if result.success:
            print("INITIALIZATION COMPLETE")
            print("=" * 60)
            print(f"\nProject ID: {result.project_id}")
            print(f"Tasks Created: {result.tasks_created}")
            if result.meta_task_id:
                print(f"META Task ID: {result.meta_task_id}")

            if result.task_breakdown:
                print("\nTask Breakdown by Category:")
                for cat, count in result.task_breakdown.items():
                    print(f"  {cat}: {count}")

            if result.priority_distribution:
                print("\nPriority Distribution:")
                for pri, count in result.priority_distribution.items():
                    print(f"  {pri}: {count}")

            print("\n" + "-" * 60)
            print("NEXT STEPS")
            print("-" * 60)
            print("\n1. Review created tasks:")
            print("   python -m scripts.autonomous tasks")
            print("\n2. Start coding agent (Phase 2):")
            print("   python -m scripts.autonomous start")
            print("\n" + "=" * 60)
        else:
            print("INITIALIZATION FAILED")
            print("=" * 60)
            print(f"\nError: {result.error}")
            if result.raw_analysis:
                print("\nRaw analysis (for debugging):")
                print(result.raw_analysis[:500])
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nInitialization cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


def cmd_start(args):
    """
    Start the coding agent.

    This is the CODING AGENT - Phase 2 of the two-agent pattern.
    It executes tasks created by the initializer agent.
    """
    from scripts.autonomous.runner import AutonomousRunner, RunnerConfig

    config_path = args.config or ".ai-agents/config.yml"

    # Check if config exists
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        print("\nCreate a config file or use --config to specify one.")
        print("\nExample minimal config:")
        print("""
state_provider:
  type: "file"

autonomous:
  backend: "claude-code"  # Uses your subscription!
  model: "opus"
  max_tasks_per_session: 10

execution:
  mode: "autonomous"
  checkpoints:
    turn_interval: 25
""")
        sys.exit(1)

    print("=" * 60)
    print("CODING AGENT - Phase 2 of Two-Agent Pattern")
    print("=" * 60)
    print(f"\nConfig: {config_path}")
    print(f"Resume mode: {args.resume}")
    print("-" * 60)

    try:
        config = RunnerConfig.from_yaml(config_path)

        # Only check API key for anthropic-sdk backend
        if config.backend == "anthropic-sdk":
            if not os.environ.get(config.api_key_env):
                print(f"Error: {config.api_key_env} environment variable not set")
                print(f"\nSet it with: export {config.api_key_env}='your-api-key'")
                print("\nOr switch to Claude Code backend (uses subscription):")
                print("  autonomous:")
                print("    backend: \"claude-code\"")
                sys.exit(1)

        runner = AutonomousRunner(config)

        print(f"\nBackend: {config.backend}")
        print(f"Model: {config.model}")
        print(f"Execution mode: {config.execution_mode}")
        print(f"Max tasks per session: {config.max_tasks_per_session}")
        if config.backend == "anthropic-sdk":
            print(f"Cost limit: ${config.cost_limit_per_session}")
        print("-" * 60)

        # Check for initialized project
        project_state_file = Path(".project_state.json")
        if project_state_file.exists():
            with open(project_state_file) as f:
                state = json.load(f)
            print(f"\nProject: {state.get('project_name', 'Unknown')}")
            print(f"Total tasks: {state.get('total_tasks', 0)}")
        else:
            print("\nNote: No .project_state.json found")
            print("Consider running 'init' first to create tasks from a spec.")

        print("\n" + "-" * 60)
        print("Starting execution...")
        print("-" * 60 + "\n")

        runner.start(resume=args.resume)

    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_resume(args):
    """
    Resume from previous session with context recovery.

    Uses the initializer agent to recover context from external provider.
    """
    from scripts.autonomous.initializer import ProjectInitializer, InitializerConfig

    config_path = args.config or ".ai-agents/config.yml"

    print("=" * 60)
    print("SESSION RECOVERY")
    print("=" * 60)

    # Check for project state
    project_state_file = Path(".project_state.json")
    if not project_state_file.exists():
        print("\nNo .project_state.json found")
        print("Run 'init' first to initialize a project.")
        sys.exit(1)

    with open(project_state_file) as f:
        state = json.load(f)

    print(f"\nProject: {state.get('project_name')}")
    print(f"Project ID: {state.get('project_id')}")
    print(f"Provider: {state.get('provider_type')}")
    print(f"Total tasks: {state.get('total_tasks')}")
    print(f"Last session: {len(state.get('sessions', []))}")

    # Get current task status
    try:
        from scripts.state_providers import get_provider, TaskStatus

        provider = get_provider()

        todo = len(provider.get_tasks(status=TaskStatus.TODO))
        in_progress = len(provider.get_tasks(status=TaskStatus.IN_PROGRESS))
        done = len(provider.get_tasks(status=TaskStatus.DONE))
        blocked = len(provider.get_tasks(status=TaskStatus.BLOCKED))

        total = todo + in_progress + done + blocked
        completion = (done / total * 100) if total > 0 else 0

        print("\n" + "-" * 60)
        print("CURRENT STATE")
        print("-" * 60)
        print(f"\nTodo: {todo}")
        print(f"In Progress: {in_progress}")
        print(f"Done: {done}")
        print(f"Blocked: {blocked}")
        print(f"Completion: {completion:.1f}%")

        # Show in-progress tasks
        if in_progress > 0:
            print("\n" + "-" * 60)
            print("IN PROGRESS TASKS")
            print("-" * 60)
            tasks = provider.get_tasks(status=TaskStatus.IN_PROGRESS)
            for task in tasks[:5]:
                print(f"\n  [{task.id}] {task.title}")
                if task.description:
                    desc_preview = task.description[:100] + "..." if len(task.description) > 100 else task.description
                    print(f"    {desc_preview}")

        # Show blocked tasks
        if blocked > 0:
            print("\n" + "-" * 60)
            print("BLOCKED TASKS")
            print("-" * 60)
            tasks = provider.get_tasks(status=TaskStatus.BLOCKED)
            for task in tasks[:5]:
                print(f"\n  [{task.id}] {task.title}")

        print("\n" + "-" * 60)
        print("NEXT STEPS")
        print("-" * 60)
        print("\n1. Continue coding with:")
        print("   python -m scripts.autonomous start --resume")
        print("\n2. Or view all tasks:")
        print("   python -m scripts.autonomous tasks")

    except Exception as e:
        print(f"\nCould not query state provider: {e}")

    print("\n" + "=" * 60)


def cmd_status(args):
    """Show runner status."""
    state_file = Path(".ai-agents/state/runner-state.json")
    progress_file = Path(".ai-agents/state/progress.json")
    project_state_file = Path(".project_state.json")

    print("=" * 60)
    print("AUTONOMOUS RUNNER STATUS")
    print("=" * 60)

    # Project state
    if project_state_file.exists():
        with open(project_state_file) as f:
            project = json.load(f)
        print(f"\nProject: {project.get('project_name', 'Unknown')}")
        print(f"Sessions: {len(project.get('sessions', []))}")

    # Runner state
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)

        print(f"\nRunner State: {state.get('state', 'unknown').upper()}")
        print(f"Session ID: {state.get('session_id', 'N/A')}")
        print(f"Tasks Completed: {state.get('tasks_completed', 0)}")
        print(f"Total Cost: ${state.get('total_cost', 0):.2f}")
        print(f"Current Turn: {state.get('checkpoint_manager_turn', 0)}")
        print(f"Last Update: {state.get('updated_at', 'N/A')}")
    else:
        print("\nNo runner state found. Runner has not been started.")

    # Progress
    if progress_file.exists():
        print("\n" + "-" * 60)
        print("PROGRESS")
        print("-" * 60)

        with open(progress_file) as f:
            progress = json.load(f)

        metrics = progress.get("metrics", {})
        print(f"\nTotal Tasks: {metrics.get('total_tasks', 0)}")
        print(f"Completed: {metrics.get('completed_tasks', 0)}")
        print(f"In Progress: {metrics.get('in_progress_tasks', 0)}")
        print(f"Blocked: {metrics.get('blocked_tasks', 0)}")
        print(f"Completion Rate: {metrics.get('completion_rate', 0) * 100:.1f}%")
        print(f"Session Tasks: {metrics.get('session_tasks_completed', 0)}")
        print(f"Tasks/Hour: {metrics.get('tasks_per_hour', 0):.1f}")
        print(f"Regression: {metrics.get('regression_status', 'unknown')}")

        # Recent events
        events = progress.get("recent_events", [])
        if events:
            print("\n" + "-" * 60)
            print("RECENT EVENTS")
            print("-" * 60)
            for event in events[-5:]:
                ts = event.get("timestamp", "")[:19]
                etype = event.get("type", "")
                data = event.get("data", {})
                task_id = data.get("task_id", "")
                print(f"  {ts} [{etype}] {task_id}")

    print("\n" + "=" * 60)


def cmd_stop(args):
    """Stop the runner."""
    state_file = Path(".ai-agents/state/runner-state.json")

    if not state_file.exists():
        print("No runner state found. Nothing to stop.")
        return

    # Update state to stopped
    with open(state_file) as f:
        state = json.load(f)

    if state.get("state") == "stopped":
        print("Runner is already stopped.")
        return

    state["state"] = "stopped"
    state["updated_at"] = datetime.now().isoformat()

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    print("Runner state set to STOPPED")
    print("Note: If runner is actively running, it will stop at the next checkpoint.")


def cmd_logs(args):
    """Show runner logs."""
    log_file = Path(".ai-agents/logs/autonomous.log")

    if not log_file.exists():
        print("No log file found.")
        print(f"Looking for: {log_file}")
        return

    with open(log_file) as f:
        lines = f.readlines()

    tail = args.tail or 50
    for line in lines[-tail:]:
        print(line.rstrip())


def cmd_tasks(args):
    """Show tasks from state provider."""
    try:
        from scripts.state_providers import get_provider, TaskStatus
    except ImportError:
        print("Could not import state_providers")
        sys.exit(1)

    try:
        provider = get_provider()
    except Exception as e:
        print(f"Could not initialize provider: {e}")
        sys.exit(1)

    print("=" * 60)
    print("TASKS FROM STATE PROVIDER")
    print("=" * 60)

    # Get tasks by status
    for status_name in ["todo", "in_progress", "blocked", "done"]:
        try:
            status = TaskStatus(status_name)
            tasks = provider.get_tasks(status=status)

            if tasks:
                print(f"\n{status_name.upper()} ({len(tasks)})")
                print("-" * 40)
                for task in tasks[:10]:  # Limit to 10 per status
                    print(f"  [{task.id}] {task.title}")
                    if task.priority:
                        print(f"    Priority: {task.priority.name}")
                if len(tasks) > 10:
                    print(f"  ... and {len(tasks) - 10} more")
        except Exception as e:
            print(f"Error getting {status_name} tasks: {e}")

    print("\n" + "=" * 60)


def cmd_config(args):
    """Show or validate configuration."""
    config_path = args.config or ".ai-agents/config.yml"

    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    try:
        from scripts.autonomous.runner import RunnerConfig
        from scripts.autonomous.initializer import InitializerConfig

        runner_config = RunnerConfig.from_yaml(config_path)
        init_config = InitializerConfig.from_yaml(config_path)

        print("=" * 60)
        print("AUTONOMOUS RUNNER CONFIGURATION")
        print("=" * 60)
        print(f"\nConfig file: {config_path}")

        print("\n" + "-" * 60)
        print("BACKEND")
        print("-" * 60)
        print(f"Backend: {runner_config.backend}")
        print(f"Model: {runner_config.model}")
        print(f"Max tokens: {runner_config.max_tokens}")
        if runner_config.backend == "anthropic-sdk":
            print(f"API key env: {runner_config.api_key_env}")

        print("\n" + "-" * 60)
        print("CODING AGENT")
        print("-" * 60)
        print(f"System prompt: {runner_config.system_prompt_path}")
        print(f"Execution mode: {runner_config.execution_mode}")
        print(f"Max turns per task: {runner_config.max_turns_per_task}")
        print(f"Max tasks per session: {runner_config.max_tasks_per_session}")
        print(f"Pause between tasks: {runner_config.pause_between_tasks}s")
        print(f"Rate limit: {runner_config.rate_limit_rpm} RPM")
        if runner_config.backend == "anthropic-sdk":
            print(f"Cost limit: ${runner_config.cost_limit_per_session}")

        print("\n" + "-" * 60)
        print("INITIALIZER AGENT")
        print("-" * 60)
        print(f"System prompt: {init_config.system_prompt_path}")
        print(f"Project state file: {init_config.project_state_file}")

        # Validate
        print("\n" + "-" * 60)
        print("VALIDATION")
        print("-" * 60)

        issues = []

        # Check API key for anthropic-sdk
        if runner_config.backend == "anthropic-sdk":
            if not os.environ.get(runner_config.api_key_env):
                issues.append(f"API key not set: {runner_config.api_key_env}")

        # Check Claude Code CLI for claude-code backend
        if runner_config.backend == "claude-code":
            import shutil
            if not shutil.which("claude"):
                issues.append("Claude Code CLI not found in PATH")

        # Check system prompts
        if not os.path.exists(runner_config.system_prompt_path):
            issues.append(f"Coding agent prompt not found: {runner_config.system_prompt_path}")
        if not os.path.exists(init_config.system_prompt_path):
            issues.append(f"Initializer prompt not found: {init_config.system_prompt_path}")

        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\nConfiguration valid!")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Runner CLI - Two-Agent Pattern",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Two-Agent Pattern (Recommended by Anthropic):
  1. init   - Initializer Agent: Analyzes spec and creates tasks
  2. start  - Coding Agent: Executes tasks with fresh context

Examples:
  Initialize project from spec:
    python -m scripts.autonomous init --spec requirements.md

  Initialize with custom project name:
    python -m scripts.autonomous init --spec spec.md --project-name "My App"

  Start coding agent:
    python -m scripts.autonomous start

  Resume previous session:
    python -m scripts.autonomous resume
    python -m scripts.autonomous start --resume

  Check status:
    python -m scripts.autonomous status

  View tasks:
    python -m scripts.autonomous tasks

  Stop runner:
    python -m scripts.autonomous stop

  View logs:
    python -m scripts.autonomous logs --tail 100

  Validate config:
    python -m scripts.autonomous config
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command (NEW - Initializer Agent)
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize project from spec (Initializer Agent - Phase 1)"
    )
    init_parser.add_argument(
        "--spec", "-s",
        required=True,
        help="Path to spec/requirements file"
    )
    init_parser.add_argument(
        "--project-name", "-n",
        help="Project name (derived from spec filename if not provided)"
    )
    init_parser.add_argument(
        "--config", "-c",
        help="Path to config file (default: .ai-agents/config.yml)"
    )
    init_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-initialization even if already initialized"
    )
    init_parser.set_defaults(func=cmd_init)

    # start command (Coding Agent)
    start_parser = subparsers.add_parser(
        "start",
        help="Start coding agent (Coding Agent - Phase 2)"
    )
    start_parser.add_argument(
        "--config", "-c",
        help="Path to config file (default: .ai-agents/config.yml)"
    )
    start_parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume from previous session"
    )
    start_parser.set_defaults(func=cmd_start)

    # resume command (Session Recovery)
    resume_parser = subparsers.add_parser(
        "resume",
        help="Show session recovery context"
    )
    resume_parser.add_argument(
        "--config", "-c",
        help="Path to config file (default: .ai-agents/config.yml)"
    )
    resume_parser.set_defaults(func=cmd_resume)

    # status command
    status_parser = subparsers.add_parser("status", help="Show runner status")
    status_parser.set_defaults(func=cmd_status)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the runner")
    stop_parser.set_defaults(func=cmd_stop)

    # logs command
    logs_parser = subparsers.add_parser("logs", help="Show runner logs")
    logs_parser.add_argument(
        "--tail", "-n",
        type=int,
        default=50,
        help="Number of lines to show (default: 50)"
    )
    logs_parser.set_defaults(func=cmd_logs)

    # tasks command
    tasks_parser = subparsers.add_parser("tasks", help="Show tasks from state provider")
    tasks_parser.set_defaults(func=cmd_tasks)

    # config command
    config_parser = subparsers.add_parser("config", help="Show/validate configuration")
    config_parser.add_argument(
        "--config", "-c",
        help="Path to config file (default: .ai-agents/config.yml)"
    )
    config_parser.set_defaults(func=cmd_config)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
