from typing import Any

from ..models.Task import (
    Task)
from ..models.actions.ContinueAsNewAction import ContinueAsNewAction


def continue_as_new(
        context,
        input_: Any = None):
    """Create a new continue as new action.

    Parameters
    ----------
    input_: Any
        The JSON-serializable input to pass to the activity function.
    """
    new_action = ContinueAsNewAction(input_)
    task = Task(is_completed=True, is_faulted=False, action=new_action)

    context._continue_as_new_task = task
