"""Tests for the expected_type kwarg on orchestration context APIs.

Covers call_activity, call_sub_orchestrator, and their _with_retry variants
when an explicit expected_type is provided at the call site (V1 string-name
callers with no auto-discovery).
"""
import json
from datetime import datetime

from tests.orchestrator.orchestrator_test_utils import (
    assert_orchestration_state_equals,
    get_orchestration_state_result,
)
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallActivityAction import CallActivityAction
from azure.durable_functions.models.actions.CallSubOrchestratorAction import CallSubOrchestratorAction
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.utils.df_serialization import df_dumps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Order:
    def __init__(self, item: str, qty: int = 1):
        self.item = item
        self.qty = qty

    @staticmethod
    def to_json(obj):
        return {"item": obj.item, "qty": obj.qty}

    @staticmethod
    def from_json(data):
        return _Order(data["item"], data["qty"])


def _base_state(output=None) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output)


def _add_activity_completed(ctx_builder, id_, result_str, name="DoWork"):
    ctx_builder.add_task_scheduled_event(name=name, id_=id_)
    ctx_builder.add_orchestrator_completed_event()
    ctx_builder.add_orchestrator_started_event()
    ctx_builder.add_task_completed_event(id_=id_, result=result_str)


def _add_sub_orch_completed(ctx_builder, id_, result_str, name="SubOrch"):
    ctx_builder.add_sub_orchestrator_started_event(name=name, id_=id_, input_="")
    ctx_builder.add_orchestrator_completed_event()
    ctx_builder.add_orchestrator_started_event()
    ctx_builder.add_sub_orchestrator_completed_event(result=result_str, id_=id_)


# ---------------------------------------------------------------------------
# call_activity with expected_type
# ---------------------------------------------------------------------------

def orchestrator_activity_expected_type(context):
    result = yield context.call_activity("DoWork", "x", expected_type=_Order)
    return result.item


def test_call_activity_with_expected_type():
    payload = df_dumps(_Order("widget", 5))
    ctx = ContextBuilder("test")
    _add_activity_completed(ctx, 0, payload)

    result = get_orchestration_state_result(ctx, orchestrator_activity_expected_type)

    assert result["isDone"] is True
    # The orchestrator returns result.item which is "widget"
    assert result["output"] == "widget"


# ---------------------------------------------------------------------------
# call_activity_with_retry with expected_type
# ---------------------------------------------------------------------------

def orchestrator_activity_retry_expected_type(context):
    opts = RetryOptions(5000, 3)
    result = yield context.call_activity_with_retry(
        "DoWork", opts, "x", expected_type=_Order)
    return result.item


def test_call_activity_with_retry_expected_type():
    payload = df_dumps(_Order("gadget", 2))
    ctx = ContextBuilder("test")
    _add_activity_completed(ctx, 0, payload)

    result = get_orchestration_state_result(ctx, orchestrator_activity_retry_expected_type)

    assert result["isDone"] is True
    assert result["output"] == "gadget"


# ---------------------------------------------------------------------------
# call_sub_orchestrator with expected_type
# ---------------------------------------------------------------------------

def orchestrator_sub_orch_expected_type(context):
    result = yield context.call_sub_orchestrator(
        "SubOrch", "input", expected_type=_Order)
    return result.item


def test_call_sub_orchestrator_with_expected_type():
    payload = df_dumps(_Order("part", 10))
    ctx = ContextBuilder("test")
    _add_sub_orch_completed(ctx, 0, payload)

    result = get_orchestration_state_result(ctx, orchestrator_sub_orch_expected_type)

    assert result["isDone"] is True
    assert result["output"] == "part"


# ---------------------------------------------------------------------------
# call_sub_orchestrator_with_retry with expected_type
# ---------------------------------------------------------------------------

def orchestrator_sub_orch_retry_expected_type(context):
    opts = RetryOptions(5000, 3)
    result = yield context.call_sub_orchestrator_with_retry(
        "SubOrch", opts, "input", expected_type=_Order)
    return result.item


def test_call_sub_orchestrator_with_retry_expected_type():
    payload = df_dumps(_Order("gizmo", 3))
    ctx = ContextBuilder("test")
    _add_sub_orch_completed(ctx, 0, payload)

    result = get_orchestration_state_result(ctx, orchestrator_sub_orch_retry_expected_type)

    assert result["isDone"] is True
    assert result["output"] == "gizmo"


# ---------------------------------------------------------------------------
# expected_type kwarg overrides auto-discovered type (None in V1)
# ---------------------------------------------------------------------------

def orchestrator_override(context):
    """Call with string name (V1) + expected_type; auto-discovery returns None."""
    result = yield context.call_activity("DoWork", "x", expected_type=_Order)
    return [result.item, result.qty]


def test_expected_type_kwarg_used_when_auto_discovery_returns_none():
    payload = df_dumps(_Order("bolt", 99))
    ctx = ContextBuilder("test")
    _add_activity_completed(ctx, 0, payload)

    result = get_orchestration_state_result(ctx, orchestrator_override)

    assert result["isDone"] is True
    output = result["output"]
    assert output[0] == "bolt"
    assert output[1] == 99
