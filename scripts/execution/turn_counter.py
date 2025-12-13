"""
Turn Counter for AI_agents

Tracks agent turns for checkpoint triggering and session management.
Persists turn count across context resets via file storage.

Usage:
    from scripts.execution.turn_counter import TurnCounter

    counter = TurnCounter()
    counter.start_session()

    # Each agent turn
    turn = counter.increment()
    if counter.should_checkpoint(interval=50):
        trigger_checkpoint()

    counter.end_session()
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class TurnMetrics:
    """Metrics for a session's turns"""
    session_id: str
    started_at: str
    total_turns: int
    checkpoints_triggered: int
    last_checkpoint_turn: int
    avg_turn_duration_ms: float
    context_samples: list  # [(turn, context_usage), ...]


class TurnCounter:
    """
    Tracks and persists agent turn counts.

    Features:
    - Persistent turn tracking across sessions
    - Checkpoint interval detection
    - Turn metrics collection
    - Context usage sampling
    """

    def __init__(self, state_dir: str = ".ai-agents/state"):
        """
        Initialize turn counter.

        Args:
            state_dir: Directory for state persistence
        """
        self.state_dir = Path(state_dir)
        self.turn_file = self.state_dir / "turn_counter.json"

        # Current state
        self.session_id: Optional[str] = None
        self.current_turn: int = 0
        self.session_start_turn: int = 0
        self.last_checkpoint_turn: int = 0
        self.checkpoints_triggered: int = 0

        # Timing
        self.session_start_time: Optional[datetime] = None
        self.last_turn_time: Optional[datetime] = None
        self.turn_durations: list = []

        # Context tracking
        self.context_samples: list = []

        # Load existing state
        self._load_state()

    def _load_state(self):
        """Load persistent state from file."""
        if self.turn_file.exists():
            try:
                with open(self.turn_file, 'r') as f:
                    state = json.load(f)

                self.current_turn = state.get("total_turns", 0)
                self.last_checkpoint_turn = state.get("last_checkpoint_turn", 0)

                # Check if there's an active session
                if state.get("active_session"):
                    session = state["active_session"]
                    self.session_id = session.get("session_id")
                    self.session_start_turn = session.get("start_turn", 0)
                    self.checkpoints_triggered = session.get("checkpoints", 0)

            except (json.JSONDecodeError, KeyError):
                # Corrupted file, start fresh
                self._reset_state()
        else:
            self._reset_state()

    def _reset_state(self):
        """Reset to clean state."""
        self.current_turn = 0
        self.session_start_turn = 0
        self.last_checkpoint_turn = 0
        self.checkpoints_triggered = 0
        self.session_id = None

    def _save_state(self):
        """Save persistent state to file."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

        state = {
            "total_turns": self.current_turn,
            "last_checkpoint_turn": self.last_checkpoint_turn,
            "updated_at": datetime.now().isoformat()
        }

        if self.session_id:
            state["active_session"] = {
                "session_id": self.session_id,
                "start_turn": self.session_start_turn,
                "current_turn": self.current_turn,
                "checkpoints": self.checkpoints_triggered,
                "started_at": self.session_start_time.isoformat() if self.session_start_time else None
            }

        with open(self.turn_file, 'w') as f:
            json.dump(state, f, indent=2)

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new session.

        Args:
            session_id: Optional session ID, auto-generated if not provided

        Returns:
            Session ID
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_start_turn = self.current_turn
        self.session_start_time = datetime.now()
        self.last_turn_time = datetime.now()
        self.turn_durations = []
        self.context_samples = []
        self.checkpoints_triggered = 0

        self._save_state()
        return self.session_id

    def end_session(self) -> TurnMetrics:
        """
        End the current session.

        Returns:
            TurnMetrics for the session
        """
        session_turns = self.current_turn - self.session_start_turn

        avg_duration = 0.0
        if self.turn_durations:
            avg_duration = sum(self.turn_durations) / len(self.turn_durations)

        metrics = TurnMetrics(
            session_id=self.session_id or "unknown",
            started_at=self.session_start_time.isoformat() if self.session_start_time else "",
            total_turns=session_turns,
            checkpoints_triggered=self.checkpoints_triggered,
            last_checkpoint_turn=self.last_checkpoint_turn,
            avg_turn_duration_ms=avg_duration,
            context_samples=self.context_samples
        )

        # Clear session state
        self.session_id = None
        self.session_start_time = None
        self._save_state()

        return metrics

    def increment(self, context_usage: Optional[float] = None) -> int:
        """
        Increment turn counter.

        Args:
            context_usage: Optional current context usage (0.0-1.0)

        Returns:
            New turn number
        """
        self.current_turn += 1

        # Track timing
        now = datetime.now()
        if self.last_turn_time:
            duration_ms = (now - self.last_turn_time).total_seconds() * 1000
            self.turn_durations.append(duration_ms)
        self.last_turn_time = now

        # Sample context usage
        if context_usage is not None:
            self.context_samples.append((self.current_turn, context_usage))
            # Keep only last 100 samples
            if len(self.context_samples) > 100:
                self.context_samples = self.context_samples[-100:]

        self._save_state()
        return self.current_turn

    def should_checkpoint(self, interval: int) -> bool:
        """
        Check if checkpoint should trigger based on interval.

        Args:
            interval: Number of turns between checkpoints

        Returns:
            True if checkpoint should trigger
        """
        if interval <= 0:
            return False

        turns_since_checkpoint = self.current_turn - self.last_checkpoint_turn
        return turns_since_checkpoint >= interval

    def mark_checkpoint(self):
        """Mark that a checkpoint was triggered."""
        self.last_checkpoint_turn = self.current_turn
        self.checkpoints_triggered += 1
        self._save_state()

    def get_session_turns(self) -> int:
        """Get number of turns in current session."""
        return self.current_turn - self.session_start_turn

    def get_turns_since_checkpoint(self) -> int:
        """Get number of turns since last checkpoint."""
        return self.current_turn - self.last_checkpoint_turn

    def get_total_turns(self) -> int:
        """Get total turns across all sessions."""
        return self.current_turn

    def get_current_context_usage(self) -> Optional[float]:
        """Get most recent context usage sample."""
        if self.context_samples:
            return self.context_samples[-1][1]
        return None

    def get_context_trend(self, window: int = 10) -> Optional[float]:
        """
        Get context usage trend (positive = increasing).

        Args:
            window: Number of samples to consider

        Returns:
            Trend value or None if insufficient data
        """
        if len(self.context_samples) < window:
            return None

        recent = self.context_samples[-window:]
        first_half = [s[1] for s in recent[:window//2]]
        second_half = [s[1] for s in recent[window//2:]]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        return avg_second - avg_first

    def get_metrics(self) -> Dict[str, Any]:
        """Get current turn metrics."""
        return {
            "session_id": self.session_id,
            "total_turns": self.current_turn,
            "session_turns": self.get_session_turns(),
            "turns_since_checkpoint": self.get_turns_since_checkpoint(),
            "checkpoints_triggered": self.checkpoints_triggered,
            "current_context_usage": self.get_current_context_usage(),
            "context_trend": self.get_context_trend(),
            "avg_turn_duration_ms": sum(self.turn_durations) / len(self.turn_durations) if self.turn_durations else 0
        }

    def estimate_remaining_turns(self, context_limit: float = 0.9) -> Optional[int]:
        """
        Estimate turns remaining before context limit.

        Args:
            context_limit: Context usage limit (0.9 = 90%)

        Returns:
            Estimated remaining turns or None if can't estimate
        """
        current_usage = self.get_current_context_usage()
        trend = self.get_context_trend()

        if current_usage is None or trend is None or trend <= 0:
            return None

        remaining_usage = context_limit - current_usage
        if remaining_usage <= 0:
            return 0

        # Estimate based on trend
        return int(remaining_usage / trend * 10)  # Rough estimate


class TurnGuard:
    """
    Context manager for tracking turns with automatic cleanup.

    Usage:
        with TurnGuard(counter) as turn:
            # Agent work here
            if turn.should_checkpoint(50):
                handle_checkpoint()
    """

    def __init__(self, counter: TurnCounter, context_usage: Optional[float] = None):
        self.counter = counter
        self.context_usage = context_usage
        self.turn_number: int = 0

    def __enter__(self):
        self.turn_number = self.counter.increment(self.context_usage)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Could add error tracking here
        pass

    def should_checkpoint(self, interval: int) -> bool:
        return self.counter.should_checkpoint(interval)
