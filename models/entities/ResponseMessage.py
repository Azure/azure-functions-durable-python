from typing import Dict, Any
import json


class ResponseMessage:
    """ResponseMessage.

    Specifies the response of an entity, as processed by the durable-extension.
    """

    def __init__(self, result: str, is_exception: bool = False):
        """Instantiate a ResponseMessage.

        Specifies the response of an entity, as processed by the durable-extension.

        Parameters
        ----------
        result: str
            The result provided by the entity
        """
        # The time-out case seems to be handled by the Functions-Host, so
        # its result is not doubly-serialized. In this branch, we compensate
        # for this by re-serializing the payload.
        if result.strip().startswith("Timeout value of"):
            is_exception = True
            result = json.dumps(result)

        self.result = result
        self.is_exception = is_exception
        # TODO: JS has an additional exceptionType field, but does not use it

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ResponseMessage':
        """Instantiate a ResponseMessage from a dict of the JSON-response by the extension.

        Parameters
        ----------
        d: Dict[str, Any]
            The dictionary parsed from the JSON-response by the durable-extension

        Returns
        -------
        ResponseMessage:
            The ResponseMessage built from the provided dictionary
        """
        is_error = "exceptionType" in d.keys()
        result = cls(d["result"], is_error)
        return result
