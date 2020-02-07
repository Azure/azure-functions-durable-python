from datetime import datetime, date
import json
from azure.durable_functions.models import Task, TaskSet
from azure.durable_functions.tasks import task_any
from azure.durable_functions.tasks.wait_for_external_event import wait_for_external_event_task
from azure.durable_functions.models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from tests.test_utils.ContextBuilder import ContextBuilder
from .tasks_test_utils import assert_taskset_equal


from tests.orchestrator.orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from tests.orchestrator.test_sequential_orchestrator import base_expected_state,\
 add_hello_action, add_hello_failed_events

def test_has_completed_task():
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=False, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = Task(is_completed=True, is_faulted=False, action=all_actions[1],timestamp=date(2000,2,1))
    task3 = Task(is_completed=True, is_faulted=False, action=all_actions[2],timestamp=date(2000,1,1))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(tasks)
    expected_taskset = TaskSet(is_completed=True, actions=all_actions, result=task3, timestamp=date(2000,1,1))

    assert_taskset_equal(expected_taskset, returned_taskset)

def test_has_no_completed_task():
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=False, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = Task(is_completed=False, is_faulted=False, action=all_actions[1],timestamp=date(2000,2,1))
    task3 = Task(is_completed=False, is_faulted=False, action=all_actions[2],timestamp=date(2000,1,1))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(tasks)
    expected_taskset = TaskSet(is_completed=False, actions=all_actions, result=None)

    assert_taskset_equal(expected_taskset, returned_taskset)

def test_all_faulted_task_should_fail():
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=True, action=all_actions[0], timestamp=date(2000,1,1), exc=Exception("test failure"))
    task2 = Task(is_completed=False, is_faulted=True, action=all_actions[1], timestamp=date(2000,2,1), exc=Exception("test failure"))
    task3 = Task(is_completed=False, is_faulted=True, action=all_actions[2], timestamp=date(2000,1,1), exc=Exception("test failure"))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(tasks)
    error_messages = [Exception("test failure") for _ in range(3)]
    expected_exception = Exception(f"All tasks have failed, errors messages in all tasks:{error_messages}")
    expected_taskset = TaskSet(is_completed=True, actions=all_actions, result=None, is_faulted=True, exception=expected_exception)
    assert_taskset_equal(expected_taskset, returned_taskset)

def test_one_faulted_task_should_still_proceed():
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=True, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = Task(is_completed=False, is_faulted=False, action=all_actions[1],timestamp=date(2000,2,1))
    task3 = Task(is_completed=False, is_faulted=False, action=all_actions[2],timestamp=date(2000,1,1))

    tasks = [task1, task2, task3]
    returned_taskset = task_any(tasks)
    expected_taskset = TaskSet(is_completed=False, actions=all_actions, result=None)

    assert_taskset_equal(expected_taskset, returned_taskset)

def test_taskset_and_tasks_as_args():
    all_actions = [WaitForExternalEventAction("C"), WaitForExternalEventAction("A"), WaitForExternalEventAction("B")]
    task1 = Task(is_completed=False, is_faulted=True, action=all_actions[0], timestamp=date(2000,1,1))
    task2 = TaskSet(is_completed=True, is_faulted=False, actions=[all_actions[1], all_actions[2]], \
            result=[None, None], timestamp=date(2000,1,1))

    tasks = [task1, task2]
    returned_taskset = task_any(tasks)
    expected_taskset = TaskSet(is_completed=True, actions=all_actions, result=task2, timestamp=date(2000,1,1))

    assert_taskset_equal(expected_taskset, returned_taskset)
