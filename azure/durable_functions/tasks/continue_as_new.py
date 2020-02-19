from typing import Any

from ..models.Task import (
    Task)
from ..models.actions.ContinueAsNewAction import ContinueAsNewAction


def continue_as_new(
        input_: Any = None) -> Task:
    """Create a new continue as new action.

    Parameters
    ----------
    input_: Any
        The JSON-serializable input to pass to the activity function.

    Returns
    -------
    Task
        A Durable Task that causes the orchestrator reset and start as a new orchestration.
    """
    new_action = ContinueAsNewAction(input_)

    return Task(is_completed=False, is_faulted=False, action=new_action)
