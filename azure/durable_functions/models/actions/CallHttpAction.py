from typing import Any, Dict

from .Action import Action
from .ActionType import ActionType
from .. import DurableHttpRequest
from ..utils.json_utils import add_attrib, add_json_attrib


class CallHttpAction(Action):
    """Defines the structure of the Call Http object.

    Provides the information needed by the durable extension to be able to schedule the activity.
    """

    def __init__(self, http_request: DurableHttpRequest):
        self.action_type: ActionType = ActionType.CALL_HTTP
        self.http_request = http_request

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_json_attrib(json_dict, self, 'http_request', 'httpRequest')
        return json_dict
