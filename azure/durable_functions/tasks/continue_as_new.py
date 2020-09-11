from typing import Any

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

    context.actions.append([new_action])
    context._continue_as_new_flag = True
