from typing import Any, Dict

from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class WaitForExternalEventAction:
    def __init__(self, external_event_name: str):
        self.action_type: ActionType = ActionType.WaitForExternalEvent
        self.external_event_name: str = external_event_name
        self.reason= "ExternalEvent"
        # reason = classes_1.ExternalEventType.ExternalEvent

        if not self.external_event_name:
            raise ValueError("external_event_name cannot be empty")

