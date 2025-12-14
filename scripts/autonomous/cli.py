#!/usr/bin/env python3
"""
CLI interface for Autonomous Runner

Provides command-line interface for starting, stopping, and monitoring
the autonomous runner.

Usage:
    python -m scripts.autonomous start [--config CONFIG] [--resume]
    python -m scripts.autonomous status
    python -m scripts.autonomous stop
    python -m scripts.autonomous logs [--tail N]
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


def cmd_start(args):
    """Start the autonomous runner."""
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
  model: "claude-sonnet-4-20250514"
  max_tokens: 8192
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt_path: "prompts/roles/software-developer.md"
  max_turns_per_task: 50
  max_tasks_per_session: 10
  rate_limit_rpm: 50
  cost_limit_per_session: 10.0

execution:
  mode: "autonomous"
  checkpoints:
    turn_interval: 25
""")
        sys.exit(1)

    # Check for API key
    api_key_env = "ANTHROPIC_API_KEY"
    if not os.environ.get(api_key_env):
        print(f"Error: {api_key_env} environment variable not set")
        print(f"\nSet it with: export {api_key_env}='your-api-key'")
        sys.exit(1)

    print(f"Starting autonomous runner with config: {config_path}")
    print(f"Resume mode: {args.resume}")
    print("-" * 50)

    try:
        config = RunnerConfig.from_yaml(config_path)
        runner = AutonomousRunner(config)

        print(f"Model: {config.model}")
        print(f"Execution mode: {config.execution_mode}")
        print(f"Max tasks per session: {config.max_tasks_per_session}")
        print(f"Cost limit: ${config.cost_limit_per_session}")
        print("-" * 50)

        runner.start(resume=args.resume)

    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_status(args):
    """Show runner status."""
    state_file = Path(".ai-agents/state/runner-state.json")
    progress_file = Path(".ai-agents/state/progress.json")

    print("=" * 50)
    print("AUTONOMOUS RUNNER STATUS")
    print("=" * 50)

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
        print("\n" + "-" * 50)
        print("PROGRESS")
        print("-" * 50)

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
            print("\n" + "-" * 50)
            print("RECENT EVENTS")
            print("-" * 50)
            for event in events[-5:]:
                ts = event.get("timestamp", "")[:19]
                etype = event.get("type", "")
                data = event.get("data", {})
                task_id = data.get("task_id", "")
                print(f"  {ts} [{etype}] {task_id}")

    print("\n" + "=" * 50)


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
        from scripts.state_providers import get_provider
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
            from scripts.state_providers import TaskStatus
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
        config = RunnerConfig.from_yaml(config_path)

        print("=" * 50)
        print("RUNNER CONFIGURATION")
        print("=" * 50)
        print(f"\nConfig file: {config_path}")
        print(f"\nModel: {config.model}")
        print(f"Max tokens: {config.max_tokens}")
        print(f"API key env: {config.api_key_env}")
        print(f"System prompt: {config.system_prompt_path}")
        print(f"\nExecution mode: {config.execution_mode}")
        print(f"Max turns per task: {config.max_turns_per_task}")
        print(f"Max tasks per session: {config.max_tasks_per_session}")
        print(f"Pause between tasks: {config.pause_between_tasks}s")
        print(f"\nRate limit: {config.rate_limit_rpm} RPM")
        print(f"Cost limit: ${config.cost_limit_per_session}")

        # Validate
        print("\n" + "-" * 50)
        print("VALIDATION")
        print("-" * 50)

        issues = []

        # Check API key
        if not os.environ.get(config.api_key_env):
            issues.append(f"API key not set: {config.api_key_env}")

        # Check system prompt
        if not os.path.exists(config.system_prompt_path):
            issues.append(f"System prompt not found: {config.system_prompt_path}")

        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\nConfiguration valid!")

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Runner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Start runner:
    python -m scripts.autonomous start

  Start with custom config:
    python -m scripts.autonomous start --config my-config.yml

  Resume from previous session:
    python -m scripts.autonomous start --resume

  Check status:
    python -m scripts.autonomous status

  Stop runner:
    python -m scripts.autonomous stop

  View logs:
    python -m scripts.autonomous logs --tail 100

  View tasks:
    python -m scripts.autonomous tasks

  Validate config:
    python -m scripts.autonomous config
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # start command
    start_parser = subparsers.add_parser("start", help="Start the autonomous runner")
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
