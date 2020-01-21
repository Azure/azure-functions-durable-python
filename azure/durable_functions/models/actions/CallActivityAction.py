from typing import Any, Dict

from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class CallActivityAction:
    def __init__(self, function_name: str, input_=None):
        self.action_type: ActionType = ActionType.CallActivity
        self.function_name: str = function_name
        self.input_ = input_

        if not self.function_name:
            raise ValueError("function_name cannot be empty")

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'function_name', 'functionName')
        add_attrib(json_dict, self, 'input_', 'input')
        return json_dict
