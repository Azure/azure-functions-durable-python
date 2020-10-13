from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallEntityAction \
    import CallEntityAction
from azure.durable_functions.models.actions.SignalEntityAction \
    import SignalEntityAction
from tests.test_utils.testClasses import SerializableClass
import azure.durable_functions as df
from typing import Any

def generator_function_call_entity(context):
    outputs = []
    entityId = df.EntityId("Counter", "myCounter")
    x = yield context.call_entity(entityId, "add", 3)
    
    outputs.append(x)
    return outputs

def generator_function_signal_entity(context):
    outputs = []
    entityId = df.EntityId("Counter", "myCounter")
    context.signal_entity(entityId, "add", 3)
    x = yield context.call_entity(entityId, "get")
    
    outputs.append(x)
    return outputs

def base_expected_state(output=None) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output)

def add_call_entity_action(state: OrchestratorState, id_: df.EntityId, op: str, input_: Any):
    action = CallEntityAction(entity_id=id_, operation=op, input_=input_)
    state.actions.append([action])

def add_signal_entity_action(state: OrchestratorState, id_: df.EntityId, op: str, input_: Any):
    action = SignalEntityAction(entity_id=id_, operation=op, input_=input_)
    state.actions.append([action])

def add_call_entity_completed_events(
        context_builder: ContextBuilder, op: str, instance_id=str, input_=None):
    context_builder.add_event_sent_event(instance_id)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_event_raised_event(name="0000", id_=0, input_=input_, is_entity=True)

def test_call_entity_sent():
    context_builder = ContextBuilder('test_simple_function')

    entityId = df.EntityId("Counter", "myCounter")
    result = get_orchestration_state_result(
        context_builder, generator_function_call_entity)

    expected_state = base_expected_state()
    add_call_entity_action(expected_state, entityId, "add", 3)
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
    
def test_signal_entity_sent():
    context_builder = ContextBuilder('test_simple_function')

    entityId = df.EntityId("Counter", "myCounter")
    result = get_orchestration_state_result(
        context_builder, generator_function_signal_entity)

    expected_state = base_expected_state()
    add_signal_entity_action(expected_state, entityId, "add", 3)
    add_call_entity_action(expected_state, entityId, "get", None)
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_call_entity_raised():
    entityId = df.EntityId("Counter", "myCounter")
    context_builder = ContextBuilder('test_simple_function')
    add_call_entity_completed_events(context_builder, "add", df.EntityId.get_scheduler_id(entityId), 3)

    result = get_orchestration_state_result(
        context_builder, generator_function_call_entity)

    expected_state = base_expected_state(
        [3]
    )

    add_call_entity_action(expected_state, entityId, "add", 3)
    expected_state._is_done = True
    expected = expected_state.to_json()

    #assert_valid_schema(result)

    assert_orchestration_state_equals(expected, result)