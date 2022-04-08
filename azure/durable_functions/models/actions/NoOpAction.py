from azure.durable_functions.models.actions.Action import Action
from typing import Any, Dict, Optional


class NoOpAction(Action):
    """A no-op action, for anonymous tasks only."""

    def __init__(self, metadata: Optional[str] = None):
        """Create a NoOpAction object.

        This is an internal-only action class used to represent cases when intermediate
        tasks are used to implement some API. For example, in -WithRetry APIs, intermediate
        timers are created. We create this NoOp action to track those the backing actions
        of those tasks, which is necessary because we mimic the DF-internal replay algorithm.

        Parameters
        ----------
        metadata : Optional[str]
            Used for internal debugging: metadata about the action being represented.
        """
        self.metadata = metadata

    def action_type(self) -> int:
        """Get the type of action this class represents."""
        raise Exception("Attempted to get action type of an anonymous Action")

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        raise Exception("Attempted to convert an anonymous Action to JSON")
