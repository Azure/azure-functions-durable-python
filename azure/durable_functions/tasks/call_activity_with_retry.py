from typing import List, Any

from .task_utilities import find_task_scheduled, \
    find_task_retry_timer_created, set_processed, parse_history_event, \
    find_task_completed, find_task_failed, find_task_retry_timer_fired
from ..models.RetryOptions import RetryOptions
from ..models.Task import (
    Task)
from ..models.actions.CallActivityWithRetryAction import \
    CallActivityWithRetryAction
from ..models.history import HistoryEvent


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
    for attempt in range(retry_options.max_number_of_attempts):
        task_scheduled = find_task_scheduled(state, name)
        task_completed = find_task_completed(state, task_scheduled)
        task_failed = find_task_failed(state, task_scheduled)
        task_retry_timer = find_task_retry_timer_created(state, task_failed)
        task_retry_timer_fired = find_task_retry_timer_fired(
            state, task_retry_timer)
        set_processed([task_scheduled, task_completed,
                       task_failed, task_retry_timer, task_retry_timer_fired])

        if not task_scheduled:
            break

        if task_completed:
            return Task(
                is_completed=True,
                is_faulted=False,
                action=new_action,
                result=parse_history_event(task_completed),
                timestamp=task_completed.timestamp,
                id_=task_completed.TaskScheduledId)

        if task_failed and task_retry_timer and attempt + 1 >= \
                retry_options.max_number_of_attempts:
            return Task(
                is_completed=True,
                is_faulted=True,
                action=new_action,
                timestamp=task_failed.timestamp,
                id_=task_failed.TaskScheduledId,
                exc=Exception(
                    f"{task_failed.Reason} \n {task_failed.Details}")
            )

    return Task(is_completed=False, is_faulted=False, action=new_action)
