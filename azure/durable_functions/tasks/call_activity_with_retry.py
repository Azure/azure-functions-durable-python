from typing import List, Any

from .task_utilities import get_retried_task
from ..models.RetryOptions import RetryOptions
from ..models.Task import (
    Task)
from ..models.actions.CallActivityWithRetryAction import \
    CallActivityWithRetryAction
from ..models.history import HistoryEvent, HistoryEventType


def call_activity_with_retry_task(
        state: List[HistoryEvent],
        retry_options: RetryOptions,
        name: str,
        input_: Any = None) -> Task:
    """Determine the state of scheduling an activity for execution with retry options.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of history events to search to determine the current state of the activity.
    retry_options: RetryOptions
        The retry options for the activity function.
    name: str
        The name of the activity function to call.
    input_: Any
        The JSON-serializable input to pass to the activity function.

    Returns
    -------
    Task
        A Durable Task that completes when the called activity function completes or fails
        completely.
    """
    new_action = CallActivityWithRetryAction(
        function_name=name, retry_options=retry_options, input_=input_)

    return get_retried_task(
        state=state,
        max_number_of_attempts=retry_options.max_number_of_attempts,
        scheduled_type=HistoryEventType.TASK_SCHEDULED,
        completed_type=HistoryEventType.TASK_COMPLETED,
        failed_type=HistoryEventType.TASK_FAILED,
        action=new_action
    )
