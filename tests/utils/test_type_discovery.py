"""Tests for type_discovery helpers."""

from typing import Optional
from unittest.mock import MagicMock

from azure.durable_functions.models.utils.type_discovery import (
    activity_output_type,
    sub_orchestrator_output_type,
)


class _Result:
    pass


def _make_function_builder(fn):
    """Build a minimal stand-in for FunctionBuilder._function._func."""
    fb = MagicMock()
    fb._function._func = fn
    return fb


# ---------------------------------------------------------------------------
# activity_output_type
# ---------------------------------------------------------------------------

def test_activity_output_type_returns_annotation():
    def my_activity(x) -> _Result:
        return _Result()
    fb = _make_function_builder(my_activity)
    assert activity_output_type(fb) is _Result


def test_activity_output_type_returns_none_for_string():
    assert activity_output_type("activity_name") is None


def test_activity_output_type_returns_none_when_unannotated():
    def my_activity(x):
        return None
    fb = _make_function_builder(my_activity)
    assert activity_output_type(fb) is None


def test_activity_output_type_returns_none_for_typing_construct():
    def my_activity(x) -> Optional[_Result]:
        return None
    fb = _make_function_builder(my_activity)
    # Optional[_Result] is not a concrete class, so we return None.
    assert activity_output_type(fb) is None


# ---------------------------------------------------------------------------
# sub_orchestrator_output_type (same shape as activity)
# ---------------------------------------------------------------------------

def test_sub_orchestrator_output_type_returns_annotation():
    def my_sub_orch(ctx) -> _Result:
        return _Result()
    fb = _make_function_builder(my_sub_orch)
    assert sub_orchestrator_output_type(fb) is _Result


def test_sub_orchestrator_output_type_returns_none_for_string():
    assert sub_orchestrator_output_type("orch_name") is None
