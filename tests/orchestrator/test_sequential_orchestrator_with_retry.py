from typing import List, Union
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import get_orchestration_state_result, assert_orchestration_state_equals, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.actions.CallActivityWithRetryAction \
    import CallActivityWithRetryAction


RETRY_OPTIONS = RetryOptions(5000, 3)


def generator_function(context):
    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = yield context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    task2 = yield context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")
    task3 = yield context.call_activity_with_retry(
        "Hello",  retry_options, "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def generator_function_try_catch(context):
    outputs = []

    retry_options = RETRY_OPTIONS
    result = None
    try:
        result = yield context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    except:
        result = yield context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")
    return result

def generator_function_concurrent_retries(context):
    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    task2 = context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")
    task3 = context.call_activity_with_retry(
        "Hello",  retry_options, "London")

    outputs = yield context.task_all([task1, task2, task3])

    return outputs

def generator_function_two_concurrent_retries_when_all(context):
    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    task2 = context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")

    outputs = yield context.task_all([task1, task2])

    return outputs

def generator_function_two_concurrent_retries_when_any(context):
    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    task2 = context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")

    outputs = yield context.task_any([task1, task2])

    return outputs.result


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)


def add_hello_action(state: OrchestratorState, input_: Union[List[str], str]):
    retry_options = RETRY_OPTIONS
    actions = []
    inputs = input_
    if not isinstance(input_, list):
        inputs = [input_]
    for input_ in inputs:
        action = CallActivityWithRetryAction(
            function_name='Hello', retry_options=retry_options, input_=input_)
        actions.append(action)
    state._actions.append(actions)


def add_hello_failed_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def add_hello_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_retry_timer_events(context_builder: ContextBuilder, id_: int):
    fire_at = context_builder.add_timer_created_event(id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at)

def add_two_retriable_events_completing_out_of_order(context_builder: ContextBuilder,
        failed_reason, failed_details):
    ## Schedule tasks
    context_builder.add_task_scheduled_event(name='Hello', id_=0) # Tokyo task
    context_builder.add_task_scheduled_event(name='Hello', id_=1) # Seattle task

    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()

    ## Task failures and timer-scheduling

    # tasks fail "out of order"
    context_builder.add_task_failed_event(
        id_=1, reason=failed_reason, details=failed_details) # Seattle task
    fire_at_1 = context_builder.add_timer_created_event(2) # Seattle timer

    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()

    context_builder.add_task_failed_event(
        id_=0, reason=failed_reason, details=failed_details) # Tokyo task
    fire_at_2 = context_builder.add_timer_created_event(3) # Tokyo timer

    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()

    ## fire timers
    context_builder.add_timer_fired_event(id_=2, fire_at=fire_at_1) # Seattle timer
    context_builder.add_timer_fired_event(id_=3, fire_at=fire_at_2) # Tokyo timer

    ## Complete events
    context_builder.add_task_scheduled_event(name='Hello', id_=4) # Seattle task
    context_builder.add_task_scheduled_event(name='Hello', id_=5) # Tokyo task

    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=4, result="\"Hello Seattle!\"")
    context_builder.add_task_completed_event(id_=5, result="\"Hello Tokyo!\"")


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


def test_failed_tokyo_with_retry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_timer_entry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_failed_retry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_failed_retry_timer_added():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_successful_tokyo_with_failed_retry_timer_added():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_completed_events(context_builder, 2, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_hit_max_attempts():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_hello_failed_events(context_builder, 4, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 5)

    try:
        result = get_orchestration_state_result(
            context_builder, generator_function)
        # expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        expected_state = base_expected_state()
        add_hello_action(expected_state, 'Tokyo')

        error_msg = f'{failed_reason} \n {failed_details}'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str

def test_failed_tokyo_hit_max_attempts_in_try_catch():
    # This test ensures that APIs can still be invoked after a failed CallActivityWithRetry invocation
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    
    # events for first task: "Hello Tokyo"
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_hello_failed_events(context_builder, 4, failed_reason, failed_details)
    # we have an "extra" timer to wait for, due to legacy behavior in DTFx.
    add_retry_timer_events(context_builder, 5)

    # events to task in except block
    add_hello_completed_events(context_builder, 6, "\"Hello Seattle!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_try_catch)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    expected_state._output = "Hello Seattle!"
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_concurrent_retriable_results():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_concurrent_retriable')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_hello_failed_events(context_builder, 1, failed_reason, failed_details)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_retry_timer_events(context_builder, 4)
    add_retry_timer_events(context_builder, 5)
    add_hello_completed_events(context_builder, 6, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 7, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 8, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_concurrent_retries)

    expected_state = base_expected_state()
    add_hello_action(expected_state, ['Tokyo', 'Seattle', 'London'])
    expected_state._output = ["Hello Tokyo!", "Hello Seattle!", "Hello London!"]
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_concurrent_retriable_results_unordered_arrival():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_concurrent_retriable_unordered_results')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_hello_failed_events(context_builder, 1, failed_reason, failed_details)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_retry_timer_events(context_builder, 4)
    add_retry_timer_events(context_builder, 5)
    # events arrive in non-sequential different order
    add_hello_completed_events(context_builder, 8, "\"Hello London!\"")
    add_hello_completed_events(context_builder, 6, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 7, "\"Hello Seattle!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_concurrent_retries)

    expected_state = base_expected_state()
    add_hello_action(expected_state, ['Tokyo', 'Seattle', 'London'])
    expected_state._output = ["Hello Tokyo!", "Hello Seattle!", "Hello London!"]
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_concurrent_retriable_results_mixed_arrival():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_concurrent_retriable_unordered_results')
    # one task succeeds, the other two fail at first, and succeed on retry
    add_hello_failed_events(context_builder, 1, failed_reason, failed_details)
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_retry_timer_events(context_builder, 4)
    add_hello_completed_events(context_builder, 6, "\"Hello London!\"")
    add_hello_completed_events(context_builder, 5, "\"Hello Seattle!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_concurrent_retries)

    expected_state = base_expected_state()
    add_hello_action(expected_state, ['Tokyo', 'Seattle', 'London'])
    expected_state._output = ["Hello Tokyo!", "Hello Seattle!", "Hello London!"]
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_concurrent_retriable_results_alternating_taskIDs_when_all():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_concurrent_retriable_unordered_results')

    add_two_retriable_events_completing_out_of_order(context_builder, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function_two_concurrent_retries_when_all)

    expected_state = base_expected_state()
    add_hello_action(expected_state, ['Tokyo', 'Seattle'])
    expected_state._output = ["Hello Tokyo!", "Hello Seattle!"]
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_concurrent_retriable_results_alternating_taskIDs_when_any():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_concurrent_retriable_unordered_results')

    add_two_retriable_events_completing_out_of_order(context_builder, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function_two_concurrent_retries_when_any)

    expected_state = base_expected_state()
    add_hello_action(expected_state, ['Tokyo', 'Seattle'])
    expected_state._output = "Hello Seattle!"
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)