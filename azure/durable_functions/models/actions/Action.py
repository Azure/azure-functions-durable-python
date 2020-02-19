from azure.durable_functions.models.actions import ActionType


class Action:
    """Defines the base interface for Actions that need to be executed."""

    def __init__(self):
        actionType: ActionType
