from datetime import datetime

from .actions import Action


class Task:
    """Represents some pending action.

    Similar to a native JavaScript promise in
    that it acts as a placeholder for outstanding asynchronous work, but has
    a synchronous implementation and is specific to Durable Functions.

    Tasks are only returned to an orchestration function when a
    [[DurableOrchestrationContext]] operation is not called with `yield`. They
    are useful for parallelization and timeout operations in conjunction with
    Task.all and Task.any.
    """

    def __init__(self, is_completed, is_faulted, action,
                 result=None, timestamp=None, id_=None, exc=None):
        self._is_completed: bool = is_completed
        self._is_faulted: bool = is_faulted
        self._action: Action = action
        self._result = result
        self._timestamp: datetime = timestamp
        self._id = id_
        self._exception = exc

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
    def action(self) -> Action:
        """Get the scheduled action represented by the task.

        _Internal use only._
        """
        return self._action

    @property
    def result(self) -> object:
        """Get the result of the task, if completed. Otherwise `None`."""
        return self._result

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp of the task."""
        return self._timestamp

    @property
    def id(self):
        """Get the ID number of the task.

        _Internal use only._
        """
        return self._id

    @property
    def exception(self):
        """Get the error thrown when attempting to perform the task's action.

        If the Task has not yet completed or has completed successfully, `None`
        """
        return self._exception
