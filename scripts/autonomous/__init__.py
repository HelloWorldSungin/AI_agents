"""
Autonomous Runner for AI_agents

This module provides autonomous execution of development tasks using
the Anthropic Claude API. It integrates with:
- State providers (Linear, GitHub, File) for task management
- Execution control (checkpoints, turns) for safety
- Progress tracking for visibility

Usage:
    # CLI interface
    python -m scripts.autonomous start --config .ai-agents/config.yml
    python -m scripts.autonomous status
    python -m scripts.autonomous stop

    # Programmatic usage
    from scripts.autonomous.runner import AutonomousRunner

    runner = AutonomousRunner(config)
    runner.start()
"""

from .runner import AutonomousRunner
from .cli import main as cli_main

__all__ = [
    "AutonomousRunner",
    "cli_main"
]

__version__ = "1.0.0"
