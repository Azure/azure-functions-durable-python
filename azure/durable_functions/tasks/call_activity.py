from typing import List, Any

from ..models.Task import (
    Task)
from ..models.actions.CallActivityAction import CallActivityAction
from ..models.history import HistoryEvent
from .task_utilities import find_task_completed, find_task_failed, \
    find_task_scheduled, set_processed, parse_history_event


def call_activity_task(
        state: List[HistoryEvent],
        name: str,
        input_: Any = None) -> Task:
    """Determine the state of Scheduling an activity for execution.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of history events to search to determine the current state of the activity.
    name: str
        The name of the activity function to schedule.
    input_: Any
        The JSON-serializable input to pass to the activity function.

    Returns
    -------
    Task
        A Durable Task that completes when the called activity function completes or fails.
    """
    raise NotImplementedError

