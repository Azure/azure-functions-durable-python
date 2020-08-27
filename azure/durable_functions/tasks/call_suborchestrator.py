from typing import List, Any, Optional

from ..models.Task import (
    Task)
from ..models.actions.CallSubOrchestratorAction import CallSubOrchestratorAction
from ..models.history import HistoryEvent
from .task_utilities import set_processed, parse_history_event, \
    find_sub_orchestration_created, find_sub_orchestration_completed, \
    find_sub_orchestration_failed


def call_sub_orchestrator_task(
        context,
        state: List[HistoryEvent],
        name: str,
        input_: Optional[Any] = None,
        instance_id: Optional[str] = None) -> Task:
    """Determine the state of Scheduling a sub-orchestrator for execution.

    Parameters
    ----------
    context: 'DurableOrchestrationContext':
        A reference to the orchestration context.
    state: List[HistoryEvent]
        The list of history events to search to determine the current state of the activity.
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
    new_action = CallSubOrchestratorAction(name, input_, instance_id)

    task_scheduled = find_sub_orchestration_created(
        state, name, context=context, instance_id=instance_id)
    task_completed = find_sub_orchestration_completed(state, task_scheduled)
    task_failed = find_sub_orchestration_failed(state, task_scheduled)
    set_processed([task_scheduled, task_completed, task_failed])

    if task_completed is not None:
        return Task(
            is_completed=True,
            is_faulted=False,
            action=new_action,
            is_played=task_completed._is_played,
            result=parse_history_event(task_completed),
            timestamp=task_completed.timestamp,
            id_=task_completed.TaskScheduledId)

    if task_failed is not None:
        return Task(
            is_completed=True,
            is_faulted=True,
            action=new_action,
            is_played=task_failed._is_played,
            result=task_failed.Reason,
            timestamp=task_failed.timestamp,
            id_=task_failed.TaskScheduledId,
            exc=Exception(
                f"{task_failed.Reason} \n {task_failed.Details}")
        )

    return Task(is_completed=False, is_faulted=False, action=new_action)
