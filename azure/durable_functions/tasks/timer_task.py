from ..models.Task import Task
import datetime

class TimerTask(Task):
    """
    Returned from DurableOrchestrationContext.createTimer if the call
    is not 'yield-ed". Represents a pending timer.
    All pending timers must be completed or canceled for an orchestration 
    to complete.

    Example: Cancel a timer
    ```
    timeout_task = context.df.create_timer(expiration_date)
    if not timeout_task.is_completed():
        timeout_task.cancel()
    ```
    #TODO Write an example for create_timeout
    """

    def __init__(self, action ,is_completed, timestamp, id_):
        self._action = action,
        self._is_completed = is_completed,
        self._timestamp = timestamp,
        self._id = id_

            # Task(
            # is_completed=self._is_completed,
            # is_faulted=False,
            # action=self._action,
            # result=None,
            # timestamp=self._timestamp,
            # id_=self._id)

        super().__init__(self._is_completed,False,self._action,None,self._timestamp,self._id,None)
    
    def is_cancelled() -> bool:
        """
        Returns
        -------
        bool: Whether or not the timer has been cancelled

        """
        return self._action.is_cancelled
    
    def cancel():
        """
        Indicates the timer should be cancelled. This request will execute on
        the next `yield` or `return` statement
        
        Raises
        ------
        ValueError
            Raises an error if the task is already completed and an attempt is made to cancel it
        """
        if not self._is_completed:
            self._action.is_cancelled = True
        else:
            raise ValueError("Cannot cancel a completed task.")