from ..models.actions import ActionType


class IAction:
    """Defines the base interface for Actions that need to be executed."""

    def __init__(self):
        actionType: ActionType
