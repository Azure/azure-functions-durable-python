import json
from typing import Dict, List

from .task_utilities import find_task_scheduled, find_task_completed, find_task_failed, \
    set_processed, parse_history_event
from ..constants import HTTP_ACTION_NAME
from ..models.DurableHttpRequest import DurableHttpRequest
from ..models.TokenSource import TokenSource
from ..models.actions import CallHttpAction
from ..models.history import HistoryEvent
from ..models.Task import (
    Task)


def call_http(state: List[HistoryEvent], method: str, uri: str, content: str = None,
              headers: Dict[str, str] = None, token_source: TokenSource = None) -> Task:
    """Get task used to schedule a durable HTTP call to the specified endpoint.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of events that have been processed to determine the state of the task to be
        scheduled
    method: str
        The HTTP request method.
    uri: str
        The HTTP request uri.
    content: str
        The HTTP request content.
    headers: Dict[str, str]
        The HTTP request headers.
    token_source: TokenSource
        The source of OAuth token to add to the request.

    Returns
    -------
    Task
        The durable HTTP request to schedule.
    """
    if content and content is not isinstance(content, str):
        json_content = json.dumps(content)
    else:
        json_content = content

    request = DurableHttpRequest(method, uri, json_content, headers, token_source)

    new_action = CallHttpAction(request)

    task_scheduled = find_task_scheduled(state, HTTP_ACTION_NAME)
    task_completed = find_task_completed(state, task_scheduled)
    task_failed = find_task_failed(state, task_scheduled)
    set_processed([task_scheduled, task_completed, task_failed])

    if task_completed is not None:
        return Task(
            is_completed=True,
            is_faulted=False,
            action=new_action,
            result=parse_history_event(task_completed),
            timestamp=task_completed.timestamp,
            id_=task_completed.TaskScheduledId)

    if task_failed is not None:
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
