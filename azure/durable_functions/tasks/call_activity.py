import logging
from typing import List, Any

from ..models.Task import (
    Task)
from ..models.actions.CallActivityAction import CallActivityAction
from ..models.history import HistoryEvent
from .task_utilities import _find_task_completed, _find_task_failed, _find_task_scheduled, _set_processed, \
    _parse_history_event


def call_activity_async(
        state: List[HistoryEvent],
        name: str,
        input_: Any = None) -> Task:
    logging.warning(f"!!!callActivity name={name} input={input_}")
    new_action = CallActivityAction(name, input_)

    task_scheduled = _find_task_scheduled(state, name)
    task_completed = _find_task_completed(state, task_scheduled)
    task_failed = _find_task_failed(state, task_scheduled)
    _set_processed([task_scheduled, task_completed, task_failed])

    if task_completed is not None:
        logging.warning("!!!Task Completed")
        return Task(
            isCompleted=True,
            isFaulted=False,
            action=new_action,
            result=_parse_history_event(task_completed),
            timestamp=task_completed["Timestamp"],
            id=task_completed["TaskScheduledId"])

    if task_failed is not None:
        logging.warning("!!!Task Failed")
        return Task(
            isCompleted=True,
            isFaulted=True,
            action=new_action,
            result=task_failed["Reason"],
            timestamp=task_failed["Timestamp"],
            id=task_failed["TaskScheduledId"],
            exc=Exception(f"TaskFailed {task_failed['TaskScheduledId']}")
        )

    return Task(isCompleted=False, isFaulted=False, action=new_action)


def call_activity(
        state: List[HistoryEvent],
        name: str,
        input_: Any = None) -> Task:
    result = yield call_activity_async(state, name, input_)
    return result
