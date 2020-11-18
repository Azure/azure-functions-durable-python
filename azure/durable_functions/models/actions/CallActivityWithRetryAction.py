from json import dumps
from typing import Dict, Union

from .Action import Action
from .ActionType import ActionType
from ..RetryOptions import RetryOptions
from ..utils.json_utils import add_attrib, add_json_attrib
from azure.functions._durable_functions import _serialize_custom_object


class CallActivityWithRetryAction(Action):
    """Defines the structure of the Call Activity With Retry object.

    Provides the information needed by the durable extension to be able to schedule the activity.
    """

    def __init__(self, function_name: str,
                 retry_options: RetryOptions, input_=None):
        self.function_name: str = function_name
        self.retry_options: RetryOptions = retry_options
        self.input_ = dumps(input_, default=_serialize_custom_object)

        if not self.function_name:
            raise ValueError("function_name cannot be empty")

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CALL_ACTIVITY_WITH_RETRY

    def to_json(self) -> Dict[str, Union[str, int]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Union[str, int]]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}

        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'function_name', 'functionName')
        add_attrib(json_dict, self, 'input_', 'input')
        add_json_attrib(json_dict, self, 'retry_options', 'retryOptions')
        return json_dict
