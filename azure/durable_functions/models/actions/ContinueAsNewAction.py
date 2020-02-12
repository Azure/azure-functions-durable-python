from typing import Any, Dict

from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class ContinueAsNewAction:
    """Defines the structure of the Continue As New object.

    Provides the information needed by the durable extension to be able to reset the orchestration
    and continue as new.
    """

    def __init__(self, input_=None):
        self.action_type: ActionType = ActionType.CONTINUE_AS_NEW
        self.input_ = input_

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        :return: The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'input_', 'input')
        return json_dict
