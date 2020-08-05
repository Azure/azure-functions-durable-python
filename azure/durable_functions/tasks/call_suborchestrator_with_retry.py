from typing import List, Any, Optional

from ..models.Task import (
    Task)
from ..models.actions.CallSubOrchestratorWithRetryAction import CallSubOrchestratorWithRetryAction
from ..models.RetryOptions import RetryOptions
from ..models.history import HistoryEvent
from .task_utilities import set_processed, parse_history_event, \
    find_sub_orchestration_created, find_sub_orchestration_completed, \
    find_sub_orchestration_failed, find_task_retry_timer_fired, find_task_retry_timer_created


def call_sub_orchestrator_with_retry_task(
        context,
        state: List[HistoryEvent],
        retry_options: RetryOptions,
        name: str,
        input_: Optional[Any] = None,
        instance_id: Optional[str] = None) -> Task:
    """Determine the state of Scheduling a sub-orchestrator for execution, with retry options.

    Parameters
    ----------
    context: 'DurableOrchestrationContext':
        A reference to the orchestration context.
    state: List[HistoryEvent]
        The list of history events to search to determine the current state of the activity.
    retry_options: RetryOptions
        The settings for retrying this sub-orchestrator in case of a failure.
    name: str
        The name of the activity function to schedule.
    input_: Optional[Any]
        The JSON-serializable input to pass to the activity function. Defaults to None.
    instance_id: str
        The instance ID of the sub-orchestrator to call. Defaults to "".

    Returns
    -------
    Task
        A Durable Task that completes when the called sub-orchestrator completes or fails.
    """
    new_action = CallSubOrchestratorWithRetryAction(name, retry_options, input_, instance_id)
    for attempt in range(retry_options.max_number_of_attempts):
        task_scheduled = find_sub_orchestration_created(
            state, name, context=context, instance_id=instance_id)
        task_completed = find_sub_orchestration_completed(state, task_scheduled)
        task_failed = find_sub_orchestration_failed(state, task_scheduled)
        task_retry_timer = find_task_retry_timer_created(state, task_failed)
        task_retry_timer_fired = find_task_retry_timer_fired(
            state, task_retry_timer)
        set_processed([task_scheduled, task_completed,
                       task_failed, task_retry_timer, task_retry_timer_fired])

        if not task_scheduled:
            break

        if task_completed is not None:
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
                result=task_failed.Reason,
                timestamp=task_failed.timestamp,
                id_=task_failed.TaskScheduledId,
                exc=Exception(
                    f"{task_failed.Reason} \n {task_failed.Details}")
            )

    return Task(is_completed=False, is_faulted=False, action=new_action)
