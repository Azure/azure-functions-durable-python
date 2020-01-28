from datetime import datetime, date
import json
from unittest.mock import MagicMock
from azure.durable_functions.models import Task, TaskSet
from azure.durable_functions.tasks import task_any
from azure.durable_functions.tasks.wait_for_external_event import wait_for_external_event_task
from azure.durable_functions.models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from tests.test_utils.constants import DATETIME_STRING_FORMAT
from tests.test_utils.ContextBuilder import ContextBuilder
from .tasks_test_utils import assert_taskset_equal


def test_has_completed_task():
    state = MagicMock()
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=False, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = Task(is_completed=True, is_faulted=False, action=all_actions[1],timestamp=date(2000,2,1))
    task3 = Task(is_completed=True, is_faulted=False, action=all_actions[2],timestamp=date(2000,1,1))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(state, tasks)
    expected_taskset = TaskSet(is_completed=True, actions=all_actions, result=task3)

    assert_taskset_equal(expected_taskset, returned_taskset)

def test_has_no_completed_task():
    state = MagicMock()
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=False, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = Task(is_completed=False, is_faulted=False, action=all_actions[1],timestamp=date(2000,2,1))
    task3 = Task(is_completed=False, is_faulted=False, action=all_actions[2],timestamp=date(2000,1,1))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(state, tasks)
    expected_taskset = TaskSet(is_completed=False, actions=all_actions, result=None)

    assert_taskset_equal(expected_taskset, returned_taskset)
