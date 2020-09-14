from typing import List, Any, Optional

from ..models.Task import (
    Task)
from ..models.actions.CallSubOrchestratorWithRetryAction import CallSubOrchestratorWithRetryAction
from ..models.RetryOptions import RetryOptions
from ..models.history import HistoryEvent, HistoryEventType
from .task_utilities import get_retried_task


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
    return get_retried_task(
        state=state,
        max_number_of_attempts=retry_options.max_number_of_attempts,
        scheduled_type=HistoryEventType.SUB_ORCHESTRATION_INSTANCE_CREATED,
        completed_type=HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED,
        failed_type=HistoryEventType.SUB_ORCHESTRATION_INSTANCE_FAILED,
        action=new_action
    )
