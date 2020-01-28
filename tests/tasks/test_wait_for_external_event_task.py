
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.Task import Task
from azure.durable_functions.tasks.wait_for_external_event import wait_for_external_event_task
from azure.durable_functions.models.actions.WaitForExternalEventAction import WaitForExternalEventAction
from tests.test_utils.constants import DATETIME_STRING_FORMAT
from datetime import datetime
import json


def assert_actions_equal(action1, action2):
    assert action1.action_type == action2.action_type
    assert action1.external_event_name == action2.external_event_name   
    assert action1.reason == action2.reason

def assert_tasks_equal(task1, task2):
    assert task1.is_completed == task2.is_completed
    assert task1.is_faulted == task2.is_faulted
    assert task1.result == task2.result
    assert task1.timestamp == task2.timestamp
    assert task1.id == task2.id
    assert_actions_equal(task1.action, task2.action)

def test_event_not_raised_return_incompleted_task():
    context_builder = ContextBuilder('test_simple_function')
    state = context_builder.get_history_list_as_dict()
    expected_action = WaitForExternalEventAction("A")

    returned_task = wait_for_external_event_task(state, "A")
    expected_task = Task(is_completed=False, is_faulted=False, action=expected_action)

    assert_tasks_equal(expected_task, returned_task)

def test_event_raised_return_completed_task():
    timestamp = datetime.now().strftime(DATETIME_STRING_FORMAT)
    json_input = '{"test":"somecontent"}'
    expected_action = WaitForExternalEventAction("A")
    context_builder = ContextBuilder('test_simple_function')
    context_builder.add_event_raised_event(name="A", input_=json_input, timestamp=timestamp, id_=1)
    state = context_builder.get_history_list_as_dict()
    
    returned_task = wait_for_external_event_task(state, "A")
    expected_task = Task(
            is_completed=True,
            is_faulted=False,
            action=expected_action,
            result=json.loads(json_input),
            timestamp=timestamp,
            id_=1)

    assert_tasks_equal(expected_task, returned_task)
