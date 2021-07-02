from tests.orchestrator.test_fan_out_fan_in import add_completed_event, add_failed_event, base_expected_state, add_multi_actions
from tests.orchestrator.orchestrator_test_utils import assert_orchestration_state_equals, get_orchestration_state_result
from tests.test_utils.ContextBuilder import ContextBuilder

def generator_function(context):
    task1 = context.call_activity("Hello", "0")
    task2 = context.call_activity("Hello", "1")
    task3 = context.call_activity("Hello", "2")
    task4 = context.task_any([task1, task2, task3])
    yield task4
    return task4.result

def test_continues_on_zero_results():
    context_builder = ContextBuilder()
    result = get_orchestration_state_result(
        context_builder, generator_function)
    expected_state = base_expected_state()
    add_multi_actions(expected_state, function_name='Hello', volume=3)
    expected = expected_state.to_json()
    assert_orchestration_state_equals(expected, result)

def test_continues_on_one_failure():
    context_builder = ContextBuilder()
    add_failed_event(context_builder, 0, "Hello", reason="", details="")
    result = get_orchestration_state_result(
        context_builder, generator_function)
    add_failed_event(context_builder, 0, "Hello", reason="", details="")
    expected_state = base_expected_state()
    add_multi_actions(expected_state, function_name='Hello', volume=3)
    expected = expected_state.to_json()
    assert_orchestration_state_equals(expected, result)

def test_fails_on_all_failures():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder()
    add_failed_event(context_builder, 0, "Hello", reason=failed_reason, details=failed_details)
    add_failed_event(context_builder, 1, "Hello", reason=failed_reason, details=failed_details)
    add_failed_event(context_builder, 2, "Hello", reason=failed_reason, details=failed_details)
    try:
        result = get_orchestration_state_result(
            context_builder, generator_function)
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)
        assert True
        expected_state = base_expected_state()
        add_multi_actions(expected_state, function_name='Hello', volume=3)
        expected = expected_state.to_json()
        error_msg = f'{failed_reason} \n {failed_details}'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str

def test_succeeds_on_one_result():
    context_builder = ContextBuilder()
    add_completed_event(context_builder, 0, "Hello", result="1")
    result = get_orchestration_state_result(
        context_builder, generator_function)
    add_completed_event(context_builder, 2, "Hello", "3")
    expected_state = base_expected_state()
    add_multi_actions(expected_state, function_name='Hello', volume=3)
    expected_state._is_done = True
    expected = expected_state.to_json()
    assert_orchestration_state_equals(expected, result)