from typing import List
from azure.durable_functions.models.actions.Action import Action
from datetime import datetime


class TaskSet:
    """Represents a list of some pending action.

    Similar to a native JavaScript promise in
    that it acts as a placeholder for outstanding asynchronous work, but has
    a synchronous implementation and is specific to Durable Functions.

    Tasks are only returned to an orchestration function when a
    [[DurableOrchestrationContext]] operation is not called with `yield`. They
    are useful for parallelization and timeout operations in conjunction with
    Task.all and Task.any.
    """

    def __init__(self, is_completed, actions, result, is_faulted=False,
                 timestamp=None, exception=None):
        self._is_completed: bool = is_completed
        self._actions: List[Action] = actions
        self._result = result
        self._is_faulted: bool = is_faulted
        self._timestamp: datetime = timestamp
        self._exception = exception

    @property
    def is_completed(self) -> bool:
        """Get indicator whether the task has completed.

        Note that completion is not equivalent to success.
        """
        return self._is_completed

    @property
    def is_faulted(self) -> bool:
        """Get indicator whether the task faulted in some way due to error."""
        return self._is_faulted

    @property
    def actions(self) -> List[Action]:
        """Get the scheduled action represented by the task.

        _Internal use only._
        """
        return self._actions

    @property
    def result(self) -> object:
        """Get the result of the task, if completed. Otherwise `None`."""
        return self._result

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp of the task."""
        return self._timestamp

    @property
    def exception(self):
        """Get the error thrown when attempting to perform the task's action.

        If the Task has not yet completed or has completed successfully, `None`
        """
        return self._exception
