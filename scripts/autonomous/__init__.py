"""
Autonomous Runner for AI_agents (Two-Agent Pattern)

Implements Anthropic's recommended two-agent pattern for optimal context
window management:

1. **Initializer Agent** - Analyzes requirements and creates tasks
2. **Coding Agent** - Executes tasks with fresh context per task

This module integrates with:
- State providers (Linear, GitHub, File) for task management
- Execution control (checkpoints, turns) for safety
- Progress tracking for visibility

Usage:
    # CLI interface (Two-Agent Pattern)

    # Phase 1: Initialize project from spec
    python -m scripts.autonomous init --spec requirements.md

    # Phase 2: Run coding agent
    python -m scripts.autonomous start

    # Other commands
    python -m scripts.autonomous status
    python -m scripts.autonomous resume
    python -m scripts.autonomous tasks
    python -m scripts.autonomous stop

    # Programmatic usage
    from scripts.autonomous import ProjectInitializer, AutonomousRunner

    # Phase 1: Initialize
    initializer = ProjectInitializer(config)
    result = initializer.initialize("requirements.md")

    # Phase 2: Execute
    runner = AutonomousRunner(config)
    runner.start()
"""

from .runner import AutonomousRunner, RunnerConfig, RunnerState, TaskResult
from .initializer import ProjectInitializer, InitializerConfig, InitializerResult
from .cli import main as cli_main

__all__ = [
    # Coding Agent
    "AutonomousRunner",
    "RunnerConfig",
    "RunnerState",
    "TaskResult",
    # Initializer Agent
    "ProjectInitializer",
    "InitializerConfig",
    "InitializerResult",
    # CLI
    "cli_main"
]

__version__ = "1.5.0"
