from typing import Any, Dict

from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class WaitForExternalEventAction:
    """Defines the structure of Wait for External Event object.

    Returns
    -------
    WaitForExternalEventAction
        Returns a WaitForExternalEventAction Class.

    Raises
    ------
    ValueError
        Raises error if external_event_name is not defined.
    """

    def __init__(self, external_event_name: str):
        self.action_type: ActionType = ActionType.WAIT_FOR_EXTERNAL_EVENT
        self.external_event_name: str = external_event_name
        self.reason = "ExternalEvent"

        if not self.external_event_name:
            raise ValueError("external_event_name cannot be empty")

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict = {}

        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'external_event_name', 'externalEventName')
        add_attrib(json_dict, self, 'reason', 'reason')
        return json_dict
