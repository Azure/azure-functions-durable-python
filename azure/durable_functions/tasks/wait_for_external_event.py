import logging
from typing import List, Any

from ..models.Task import (
    Task)
from ..models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from ..models.history import HistoryEvent
from .task_utilities import find_task_completed, find_task_failed, find_task_scheduled, \
    set_processed, parse_history_event, find_event_raised


def wait_for_external_event_task(
        state: List[HistoryEvent],
        name: str) -> Task:
    logging.warning(f"!!!wait_for_external_event_task name={name}")
    new_action = WaitForExternalEventAction(name)
    eventRaised = find_event_raised(state, name)
    set_processed([eventRaised])
    if (eventRaised):
            return Task(
            isCompleted=True,
            isFaulted=False,
            action=new_action,
            result=parse_history_event(eventRaised),
            timestamp=eventRaised["Timestamp"],
            id=eventRaised["EventId"])
    
    else:
        return Task(isCompleted=False, isFaulted=False, action=new_action)
    