from ..models.Task import Task
from ..models.actions.CreateTimerAction import CreateTimerAction


class TimerTask(Task):
    """Represents a pending timer.

    All pending timers must be completed or canceled for an orchestration to complete.

    Example: Cancel a timer
    ```
    timeout_task = context.df.create_timer(expiration_date)
    if not timeout_task.is_completed():
        timeout_task.cancel()
    ```
    """

    def __init__(self, action: CreateTimerAction, is_completed, timestamp, id_, is_played=False):
        self._action: CreateTimerAction = action
        self._is_completed = is_completed
        self._timestamp = timestamp
        self._id = id_

        super().__init__(self._is_completed, False,
                         self._action, None, self._timestamp, self._id, None)
        self._is_played = is_played

    def is_cancelled(self) -> bool:
        """Check of a timer is cancelled.

        Returns
        -------
        bool
            Returns whether a timer has been cancelled or not
        """
        return self._action.is_cancelled

    def cancel(self):
        """Cancel a timer.

        Raises
        ------
        ValueError
            Raises an error if the task is already completed and an attempt is made to cancel it
        """
        if not self._is_completed:
            self._action.is_cancelled = True
        else:
            raise ValueError("Cannot cancel a completed task.")
