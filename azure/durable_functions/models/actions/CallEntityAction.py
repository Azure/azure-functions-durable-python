from typing import Any, Dict

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib
from json import dumps
from azure.functions._durable_functions import _serialize_custom_object


class CallEntityAction(Action):
    """Defines the structure of the Call Entity object.

    Provides the information needed by the durable extension to be able to call an activity
    """

    def __init__(self, entity_id: str, operation: str, input_=None):
        self.entity_id: str = entity_id #TODO: type?
        self.operation: str = operation
        # It appears that `.input_` needs to be JSON-serializable at this point
        self.input_ = dumps(input_, default=_serialize_custom_object)

        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CALL_ENTITY

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'entity_id', 'entityId')
        add_attrib(json_dict, self, 'operation', 'operation')
        add_attrib(json_dict, self, 'input_', 'input')
        return json_dict
