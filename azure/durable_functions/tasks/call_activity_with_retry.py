from typing import List, Any

from ..models.Task import (
    Task)
from ..models.actions.CallActivityWithRetryAction import CallActivityWithRetryAction
from ..models.history import HistoryEvent
from ..models.RetryOptions import RetryOptions
from .task_utilities import *


def call_activity_with_retry_task(
        state: List[HistoryEvent],
        retry_options: RetryOptions,
        name: str,
        input_: Any = None) -> Task:
    new_action = CallActivityWithRetryAction(function_name=name, retry_options=retry_options, input_=input_)
    for attempt in range(retry_options.max_number_of_attempts):
        task_scheduled = find_task_scheduled(state, name)
        task_completed = find_task_completed(state, task_scheduled)
        task_failed = find_task_failed(state, task_scheduled)
        task_retry_timer = find_task_retry_timer_created(state, task_failed)
        task_retry_timer_fired = find_task_retry_timer_fired(state, task_retry_timer)
        set_processed([task_scheduled, task_completed, task_failed, task_retry_timer, task_retry_timer_fired])

        if not task_scheduled:
            break

        if task_completed:
            logging.warning("!!!Task Completed")
            return Task(
                isCompleted=True,
                isFaulted=False,
                action=new_action,
                result=parse_history_event(task_completed),
                timestamp=task_completed["Timestamp"],
                id=task_completed["TaskScheduledId"])

        if task_failed and task_retry_timer and attempt >= retry_options.max_number_of_attempts:
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