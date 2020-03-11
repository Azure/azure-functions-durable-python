from typing import List

from ..models.Task import (
    Task)
from ..models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from ..models.history import HistoryEvent
from .task_utilities import set_processed, parse_history_event, find_event_raised


def wait_for_external_event_task(
        state: List[HistoryEvent],
        name: str) -> Task:
    """Determine the state of a task that is waiting for an event to occur.

    Parameters
    ----------
    state : List[HistoryEvent]
        The list of history events to search to determine the current
    state of the task.
    name : str
        The event name of the event that the task is waiting for.

    Returns
    -------
    Task
        Returns a completed task if the expected event was raised.
        Returns a not completed task if the expected event has not occurred yet.
    """
    new_action = WaitForExternalEventAction(name)
    event_raised = find_event_raised(state, name)
    set_processed([event_raised])
    if event_raised:
        return Task(
            is_completed=True,
            is_faulted=False,
            action=new_action,
            result=parse_history_event(event_raised),
            timestamp=event_raised.timestamp,
            id_=event_raised.event_id)

    else:
        return Task(is_completed=False, is_faulted=False, action=new_action)
