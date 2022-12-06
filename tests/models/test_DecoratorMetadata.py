from azure.durable_functions.decorators.metadata import OrchestrationTrigger,\
    EntityTrigger, ActivityTrigger, DurableClient
from azure.durable_functions.constants import ORCHESTRATION_TRIGGER, \
    ACTIVITY_TRIGGER, ENTITY_TRIGGER, DURABLE_CLIENT
from azure.functions.decorators.core import BindingDirection


def test_OrchestrationTrigger_with_full_params():
    trigger = OrchestrationTrigger(
        name="myContext",
        orchestration="myOrchestratorFunction"
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ORCHESTRATION_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "orchestrationTrigger",
        "name": "myContext",
        "orchestration": "myOrchestratorFunction"
    }

def test_OrchestrationTrigger_with_default_params():
    trigger = OrchestrationTrigger(
        name="myContext",
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ORCHESTRATION_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "orchestrationTrigger",
        "name": "myContext"
    }

def test_EntityTrigger_with_full_params():
    trigger = EntityTrigger(
        name="myContext",
        entity_name="myEntityFunction"
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ENTITY_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "entityTrigger",
        "name": "myContext",
        "entityName": "myEntityFunction"
    }

def test_EntityTrigger_with_default_params():
    trigger = EntityTrigger(
        name="myContext",
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ENTITY_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "entityTrigger",
        "name": "myContext"
    }

def test_ActivityTrigger_with_full_params():
    trigger = ActivityTrigger(
        name="myInput",
        activity="myActivityFunction"
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ACTIVITY_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "activityTrigger",
        "name": "myInput",
        "activity": "myActivityFunction"
    }

def test_ActivityTrigger_with_default_params():
    trigger = ActivityTrigger(
        name="myInput"
    )

    binding_name = trigger.get_binding_name()
    assert binding_name == ACTIVITY_TRIGGER

    dict_repr = trigger.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "activityTrigger",
        "name": "myInput"
    }

def test_DurableClient_with_full_params():
    input_binding = DurableClient(
        name="myClient",
        task_hub="myTaskHub",
        connection_name="myConnection"
    )

    binding_name = input_binding.get_binding_name()
    assert binding_name == DURABLE_CLIENT

    dict_repr = input_binding.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "durableClient",
        "name": "myClient",
        "taskHub": "myTaskHub",
        "connectionName": "myConnection"
    }

def test_DurableClient_with_default_params():
    input_binding = DurableClient(
        name="myClient",
    )

    binding_name = input_binding.get_binding_name()
    assert binding_name == DURABLE_CLIENT

    dict_repr = input_binding.get_dict_repr()
    assert dict_repr == {
        "direction": BindingDirection.IN,
        "type": "durableClient",
        "name": "myClient"
    }