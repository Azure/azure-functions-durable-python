from typing import Any, Dict

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class CallActivityAction(Action):
    """Defines the structure of the Call Activity object.

    Provides the information needed by the durable extension to be able to schedule the activity.
    """

    def __init__(self, function_name: str, input_=None):
        self.function_name: str = function_name
        self.input_ = input_

        if not self.function_name:
            raise ValueError("function_name cannot be empty")

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CALL_ACTIVITY

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'function_name', 'functionName')
        add_attrib(json_dict, self, 'input_', 'input')
        return json_dict
