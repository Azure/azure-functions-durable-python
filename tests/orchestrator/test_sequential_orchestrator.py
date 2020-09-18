from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallActivityAction \
    import CallActivityAction
from tests.test_utils.testClasses import SerializableClass


def generator_function(context):
    outputs = []

    task1 = yield context.call_activity("Hello", "Tokyo")
    task2 = yield context.call_activity("Hello", "Seattle")
    task3 = yield context.call_activity("Hello", "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


def generator_function_with_serialization(context):
    """Ochestrator to test sequential activity calls with a serializable input arguments."""
    outputs = []

    task1 = yield context.call_activity("Hello", SerializableClass("Tokyo"))
    task2 = yield context.call_activity("Hello", SerializableClass("Seattle"))
    task3 = yield context.call_activity("Hello", SerializableClass("London"))

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


def base_expected_state(output=None) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output)


def add_hello_action(state: OrchestratorState, input_: str):
    action = CallActivityAction(function_name='Hello', input_=input_)
    state.actions.append([action])


def add_hello_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_hello_failed_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def test_initial_orchestration_state():
    context_builder = ContextBuilder('test_simple_function')

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_state():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(
        context_builder, 0, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected_state._error = f'{failed_reason} \n {failed_details}'
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_and_seattle_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_and_seattle_and_london_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_and_seattle_and_london_with_serialization_state():
    """Tests the sequential function pattern with custom object serialization.
    
    This simple test validates that a sequential function pattern returns
    the expected state when the input to activities is a user-provided
    serializable class.
    """
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_with_serialization)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, SerializableClass("Tokyo"))
    add_hello_action(expected_state, SerializableClass("Seattle"))
    add_hello_action(expected_state, SerializableClass("London"))
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
