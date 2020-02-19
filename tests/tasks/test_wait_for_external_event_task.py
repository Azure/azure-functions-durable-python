import json
from datetime import datetime

from dateutil.tz import tzutc

from azure.durable_functions.models.Task import Task
from azure.durable_functions.models.actions.WaitForExternalEventAction import \
    WaitForExternalEventAction
from azure.durable_functions.tasks.wait_for_external_event import wait_for_external_event_task
from tests.test_utils.ContextBuilder import ContextBuilder
from .tasks_test_utils import assert_tasks_equal


def test_event_not_raised_return_incompleted_task():
    context_builder = ContextBuilder('test_simple_function')
    expected_action = WaitForExternalEventAction("A")

    returned_task = wait_for_external_event_task(context_builder.history_events, "A")
    expected_task = Task(is_completed=False, is_faulted=False, action=expected_action)

    assert_tasks_equal(expected_task, returned_task)


def test_event_raised_return_completed_task():
    timestamp = datetime.now()
    json_input = '{"test":"somecontent"}'
    expected_action = WaitForExternalEventAction("A")
    context_builder = ContextBuilder('test_simple_function')
    context_builder.add_event_raised_event(name="A", input_=json_input, timestamp=timestamp, id_=1)

    returned_task = wait_for_external_event_task(context_builder.history_events, "A")
    expected_task = Task(
        is_completed=True,
        is_faulted=False,
        action=expected_action,
        result=json.loads(json_input),
        timestamp=timestamp.replace(tzinfo=tzutc()),
        id_=1)

    assert_tasks_equal(expected_task, returned_task)
