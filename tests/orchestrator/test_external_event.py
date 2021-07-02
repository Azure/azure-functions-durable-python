from datetime import datetime
from tests.orchestrator.test_fan_out_fan_in import add_completed_event, add_failed_event, base_expected_state, add_multi_actions
from tests.orchestrator.orchestrator_test_utils import assert_orchestration_state_equals, get_orchestration_state_result
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.actions.WaitForExternalEventAction import WaitForExternalEventAction

def generator_function(context):
    yield context.wait_for_external_event("A")
    return ""

def test_continue_when_no_payload():
    context_builder = ContextBuilder()
    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    expected_state.actions.append([WaitForExternalEventAction("A")])
    expected = expected_state.to_json()
    assert_orchestration_state_equals(expected, result)

def test_succeeds_on_payload():
    timestamp = datetime.now()
    json_input = '{"test":"somecontent"}'
    context_builder = ContextBuilder()
    context_builder.add_event_raised_event(0, input_=json_input, timestamp=timestamp, id_=0)
    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    expected_state.actions.append([WaitForExternalEventAction("A")])
    expected_state._is_done = True
    expected = expected_state.to_json()
    assert_orchestration_state_equals(expected, result)