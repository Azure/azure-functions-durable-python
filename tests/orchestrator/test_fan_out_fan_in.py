import json

from azure.durable_functions.models import OrchestratorState
from azure.durable_functions.models.actions import CallActivityAction
from .orchestrator_test_utils import get_orchestration_state_result, \
    assert_orchestration_state_equals
from tests.test_utils.ContextBuilder import ContextBuilder


def generator_function(context):
    activity_count = yield context.df.call_activity("GetActivityCount")
    tasks = []
    for i in range(activity_count):
        current_task = context.df.call_activity("ParrotValue", str(i))
        tasks.append(current_task)
    values = yield context.df.task_all(tasks)
    results = yield context.df.call_activity("ShowMeTheSum", values)
    return results


def base_expected_state(output=None) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output)


def add_completed_event(
        context_builder: ContextBuilder, id_: int, name: str, result):
    context_builder.add_task_scheduled_event(name=name, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=json.dumps(result))


def add_single_action(state: OrchestratorState, function_name: str, input_):
    action = CallActivityAction(function_name=function_name, input_=input_)
    state.actions.append([action])


def add_multi_actions(state: OrchestratorState, function_name: str, volume: int):
    actions = []
    for i in range(volume):
        action = CallActivityAction(function_name=function_name, input_=json.dumps(i))
        actions.append(action)
    state.actions.append(actions)


def test_initial_call():
    context_builder = ContextBuilder('test_fan_out_fan_in_function')

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    expected = expected_state.to_json()

    assert_orchestration_state_equals(expected, result)


def test_get_activity_count_success():
    activity_count = 5
    context_builder = ContextBuilder('test_fan_out_fan_in_function')
    add_completed_event(context_builder, 0, 'GetActivityCount', activity_count)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    add_multi_actions(expected_state, function_name='ParrotValue', volume=activity_count)
    expected = expected_state.to_json()

    assert_orchestration_state_equals(expected, result)
