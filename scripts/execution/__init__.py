"""
Execution Control Module for AI_agents

Provides configurable execution modes with checkpoints
for balancing agent autonomy with human oversight.

Components:
- CheckpointManager: Manages checkpoint triggering and approval flow
- TurnCounter: Tracks agent turns for checkpoint intervals
- ApprovalHandler: Multi-channel approval workflow

Usage:
    from scripts.execution import (
        CheckpointManager,
        TurnCounter,
        ApprovalHandler,
        CheckpointType
    )

    # Initialize
    counter = TurnCounter()
    manager = CheckpointManager(config)
    handler = ApprovalHandler(config.get("approval", {}))

    # Each turn
    counter.increment()

    # Check for checkpoint
    if manager.should_checkpoint(CheckpointType.TURN_INTERVAL):
        checkpoint = manager.create_checkpoint(
            CheckpointType.TURN_INTERVAL,
            CheckpointContext(turn_number=counter.current_turn)
        )
        result = manager.wait_for_approval(checkpoint)

        if not result.approved:
            handle_pause_or_abort(result)
"""

from .checkpoint_manager import (
    CheckpointManager,
    CheckpointType,
    CheckpointStatus,
    CheckpointContext,
    Checkpoint,
    ApprovalAction,
    ApprovalResult
)

from .turn_counter import (
    TurnCounter,
    TurnMetrics,
    TurnGuard
)

from .approval_handler import (
    ApprovalHandler,
    ApprovalChannel,
    ApprovalStatus as ApprovalRequestStatus,
    ApprovalRequest,
    ApprovalResponse
)


def create_execution_controller(config: dict):
    """
    Create a complete execution controller from config.

    Args:
        config: Execution configuration dict

    Returns:
        Tuple of (CheckpointManager, TurnCounter, ApprovalHandler)
    """
    counter = TurnCounter()
    manager = CheckpointManager(config)
    handler = ApprovalHandler(config.get("approval", {}))

    return manager, counter, handler


__all__ = [
    # Checkpoint management
    "CheckpointManager",
    "CheckpointType",
    "CheckpointStatus",
    "CheckpointContext",
    "Checkpoint",
    "ApprovalAction",
    "ApprovalResult",

    # Turn tracking
    "TurnCounter",
    "TurnMetrics",
    "TurnGuard",

    # Approval handling
    "ApprovalHandler",
    "ApprovalChannel",
    "ApprovalRequestStatus",
    "ApprovalRequest",
    "ApprovalResponse",

    # Factory
    "create_execution_controller"
]
