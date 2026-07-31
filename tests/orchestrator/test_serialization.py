import json
from dataclasses import dataclass

import pytest

import azure.functions._durable_functions as _sdk
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from tests.test_utils.ContextBuilder import ContextBuilder
from .orchestrator_test_utils import (
    assert_orchestration_state_equals,
    assert_valid_schema,
    get_orchestration_state_result,
)
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.utils.df_serialization import df_loads


def base_expected_state(
        output=None,
        replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(
        is_done=False,
        actions=[],
        output=output,
        replay_schema=replay_schema.value)


def generator_function(context):
    return False


def test_serialization_of_False():
    """Test that an orchestrator can return False."""

    context_builder = ContextBuilder("serialize False")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(output=False)

    expected_state._is_done = True
    expected = expected_state.to_json()

    # Since we're essentially testing the `to_json` functionality,
    # we explicitely ensure that the output is set
    expected["output"] = False

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


@dataclass
class CustomResult:
    message: str

    def to_json(self):
        return {"message": self.message}

    @classmethod
    def from_json(cls, data):
        return cls(message=data["message"])


def orchestrator_with_custom_output(context):
    return CustomResult(message="Custom serialization test")


@pytest.mark.parametrize("strict", [False, True])
def test_serialization_of_custom_output(monkeypatch, strict):
    if strict:
        monkeypatch.setenv("AZURE_FUNCTIONS_DURABLE_STRICT_TYPING", "true")
    else:
        monkeypatch.delenv("AZURE_FUNCTIONS_DURABLE_STRICT_TYPING", raising=False)

    result = get_orchestration_state_result(
        ContextBuilder("serialize custom class"),
        orchestrator_with_custom_output)

    assert_valid_schema(result)
    assert result["isDone"] is True
    assert result["output"] == {
        "__class__": "CustomResult",
        "__module__": CustomResult.__module__,
        "__data__": {"message": "Custom serialization test"},
    }


def orchestrator_calling_typed_sub_orchestrator(context):
    result = yield context.call_sub_orchestrator(
        "CustomOutputOrchestrator", expected_type=CustomResult)
    return result.message


def orchestrator_calling_untyped_sub_orchestrator(context):
    yield context.call_sub_orchestrator("CustomOutputOrchestrator")


def test_strict_custom_output_can_be_decoded_by_sub_orchestrator(monkeypatch):
    monkeypatch.setenv("AZURE_FUNCTIONS_DURABLE_STRICT_TYPING", "true")
    child_state = get_orchestration_state_result(
        ContextBuilder("serialize custom class"),
        orchestrator_with_custom_output)
    child_output = json.dumps(child_state["output"])

    context_builder = ContextBuilder("consume custom class")
    context_builder.add_sub_orchestrator_started_event(
        name="CustomOutputOrchestrator", id_=0, input_="")
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_sub_orchestrator_completed_event(
        result=child_output, id_=0)

    result = get_orchestration_state_result(
        context_builder, orchestrator_calling_typed_sub_orchestrator)

    assert result["isDone"] is True
    assert result["output"] == "Custom serialization test"
    assert df_loads(child_output, expected_type=CustomResult) == CustomResult(
        message="Custom serialization test")


@pytest.mark.skipif(
    not hasattr(_sdk, "df_loads"),
    reason="strict typing is unavailable with the legacy SDK serializer")
def test_strict_custom_output_requires_sub_orchestrator_type(monkeypatch):
    monkeypatch.setenv("AZURE_FUNCTIONS_DURABLE_STRICT_TYPING", "true")
    child_state = get_orchestration_state_result(
        ContextBuilder("serialize custom class"),
        orchestrator_with_custom_output)

    context_builder = ContextBuilder("consume custom class")
    context_builder.add_sub_orchestrator_started_event(
        name="CustomOutputOrchestrator", id_=0, input_="")
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_sub_orchestrator_completed_event(
        result=json.dumps(child_state["output"]), id_=0)

    with pytest.raises(TypeError, match="strict mode requires expected_type"):
        get_orchestration_state_result(
            context_builder, orchestrator_calling_untyped_sub_orchestrator)
