"""Defines the base interface for Actions that need to be executed."""
from ..models.actions import ActionType


class IAction:
    """Defines the base interface for Actions that need to be executed."""

    def __init__(self):
        """Create a new Action object."""
        actionType: ActionType
