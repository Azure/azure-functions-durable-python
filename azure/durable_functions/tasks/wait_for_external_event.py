import logging
from typing import List

from ..models.Task import (
    Task)
from ..models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from ..models.history import HistoryEvent
from .task_utilities import set_processed, parse_history_event, find_event_raised


def wait_for_external_event_task(
        state: List[HistoryEvent],
        name: str) -> Task:
    logging.warning(f"!!!wait_for_external_event_task name={name}")
    new_action = WaitForExternalEventAction(name)
    event_raised = find_event_raised(state, name)
    set_processed([event_raised])
    if (event_raised):
        return Task(
            isCompleted=True,
            isFaulted=False,
            action=new_action,
            result=parse_history_event(event_raised),
            timestamp=event_raised["Timestamp"],
            id=event_raised["EventId"])

    else:
        return Task(isCompleted=False, isFaulted=False, action=new_action)
