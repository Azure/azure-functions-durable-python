import json
from typing import Dict


class DurableOrchestrationBindings:
    """Binding information.

    Provides information relevant to the creation and management of
    durable functions.
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    # noinspection PyPep8Naming
    def __init__(self, taskHubName: str, creationUrls: Dict[str, str],
                 managementUrls: Dict[str, str], **kwargs):
        self.task_hub_name: str = taskHubName
        self.creation_urls: Dict[str, str] = creationUrls
        self.management_urls: Dict[str, str] = managementUrls
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)
