from typing import Any, Dict

from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class WaitForExternalEventAction:
    """Defines the structure of Wait for External Event object.
    """
    def __init__(self, external_event_name: str):
        self.action_type: ActionType = ActionType.WaitForExternalEvent
        self.external_event_name: str = external_event_name
        self.reason = "ExternalEvent"

        if not self.external_event_name:
            raise ValueError("external_event_name cannot be empty")

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'external_event_name', 'externalEventName')
        add_attrib(json_dict, self, 'reason', 'reason')
        return json_dict
