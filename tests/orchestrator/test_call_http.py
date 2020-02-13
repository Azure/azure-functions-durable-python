import json

from azure.durable_functions.constants import HTTP_ACTION_NAME
from azure.durable_functions.models import DurableHttpRequest
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallHttpAction import CallHttpAction

SIMPLE_GET_URI: str = \
    'https://localhost:7071/we_just_need_a_uri_to_for_testing'

SIMPLE_RESULT: str = json.dumps({'name': 'simple'})


def generator_function(context):
    url = SIMPLE_GET_URI
    yield context.call_http("GET", url)


def base_expected_state(output=None) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output)


def add_http_action(state: OrchestratorState, request):
    action = CallHttpAction(request)
    state.actions.append([action])


def add_completed_http_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name=HTTP_ACTION_NAME, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_failed_http_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name=HTTP_ACTION_NAME, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def get_request() -> DurableHttpRequest:
    return DurableHttpRequest(method='GET', uri=SIMPLE_GET_URI)


def test_initial_orchestration_state():
    context_builder = ContextBuilder('test_simple_function')

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    request = get_request()
    add_http_action(expected_state, request)
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_completed_state():
    context_builder = ContextBuilder('test_simple_function')
    add_completed_http_events(context_builder, 0, SIMPLE_RESULT)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    request = get_request()
    add_http_action(expected_state, request)
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
