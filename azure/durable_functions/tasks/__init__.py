"""Contains the definitions for the functions that enable scheduling of activities."""
from .call_activity import call_activity_task
from .call_activity_with_retry import call_activity_with_retry_task
from .task_all import task_all
from .task_any import task_any
from .task_utilities import should_suspend
from .wait_for_external_event import wait_for_external_event_task
from .continue_as_new import continue_as_new
from .new_uuid import new_uuid
from .call_http import call_http

__all__ = [
    'call_activity_task',
    'call_activity_with_retry_task',
    'call_http',
    'continue_as_new',
    'new_uuid',
    'task_all',
    'task_any',
    'should_suspend',
    'wait_for_external_event_task'
]
