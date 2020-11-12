from typing import Optional, Dict, Any


class OperationResult:
    """OperationResult.

    The result of an Entity operation.
    """

    def __init__(self,
                 is_error: bool,
                 duration: int,
                 result: Optional[str] = None):
        """Instantiate an OperationResult.

        Parameters
        ----------
        is_error: bool
            Whether or not the operation resulted in an exception.
        duration: int
            How long the operation took, in milliseconds.
        result: Optional[str]
            The operation result. Defaults to None.
        """
        # TODO: perhaps this should inherit from orchestrator state
        self._is_error: bool = is_error
        self._duration: int = duration
        self._result: Optional[str] = result

    @property
    def is_error(self) -> bool:
        """Determine if the operation resulted in an error.

        Returns
        -------
        bool
            True if the operation resulted in error. Otherwise False.
        """
        return self._is_error

    @property
    def duration(self) -> int:
        """Get the duration of this operation.

        Returns
        -------
        int:
            The duration of this operation, in milliseconds
        """
        return self._duration

    @property
    def result(self) -> Optional[str]:
        """Get the operation's result.

        Returns
        -------
        Optional[str]
            The operation's result
        """
        # TODO: is this necessary str or None?
        return self._result

    def to_json(self) -> Dict[str, Any]:
        """Represent OperationResult as a JSON-serializable Dict.

        Returns
        -------
        Dict[str, Any]
            A JSON-serializable Dict of the OperationResult
        """
        to_json: Dict[str, Any] = {}
        to_json["isError"] = self.is_error
        to_json["duration"] = self.duration
        to_json["result"] = self.result
        return to_json
