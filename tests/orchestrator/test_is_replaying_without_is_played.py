"""Tests that the is_replaying flag is correctly determined from event history structure
alone, without relying on the is_played field. This covers Durable backends that never
set IsPlayed on history events.
"""

from azure.durable_functions.models.ReplaySchema import ReplaySchema
from tests.test_utils.ContextBuilder import ContextBuilder
from .orchestrator_test_utils import get_orchestration_property
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from datetime import datetime, timedelta, timezone


def generator_function(context):
    """Orchestrator that creates 3 sequential timers."""
    timestamp = "2020-07-23T21:56:54.936700Z"
    deadline = datetime.strptime(timestamp, DATETIME_STRING_FORMAT)
    deadline = deadline.replace(tzinfo=timezone.utc)

    for _ in range(0, 3):
        deadline = deadline + timedelta(seconds=30)
        yield context.create_timer(deadline)


def add_timer_fired_events_without_is_played(context_builder: ContextBuilder, id_: int, timestamp: str):
    """Add a complete timer episode without setting is_played (always False).

    Adds: TimerCreated, OrchestratorCompleted, OrchestratorStarted, TimerFired.
    This simulates a backend that never sets IsPlayed.
    """
    fire_at: str = context_builder.add_timer_created_event(id_, timestamp)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at, is_played=False)


def add_activity_completed_events_without_is_played(
        context_builder: ContextBuilder, name: str, id_: int, result: str):
    """Add a complete activity episode without setting is_played (always False).

    Adds: TaskScheduled, OrchestratorCompleted, OrchestratorStarted, TaskCompleted.
    This simulates a backend that never sets IsPlayed.
    """
    context_builder.add_task_scheduled_event(name, id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result, is_played=False)

# ---------- Tests verifying replaying=True for mid-replay tasks ----------

class IsReplayingTracker:
    """Tracks is_replaying values observed at each yield point during orchestration."""

    def __init__(self):
        self.values_at_yield = []


def generator_function_tracking_replay(context):
    """Orchestrator that records is_replaying at each yield point."""
    tracker = context._tracker

    result1 = yield context.call_activity("Hello", "Tokyo")
    tracker.values_at_yield.append(context.is_replaying)

    result2 = yield context.call_activity("Hello", "Seattle")
    tracker.values_at_yield.append(context.is_replaying)

    result3 = yield context.call_activity("Hello", "London")
    tracker.values_at_yield.append(context.is_replaying)

    return [result1, result2, result3]


def test_hello_cities_is_replaying_mid_execution_without_is_played():
    """Verify that is_replaying is True for old events and False for new events,
    even when is_played is never set.
    """
    tracker = IsReplayingTracker()

    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_without_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_without_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')

    context_as_string = context_builder.to_json_string()

    from azure.durable_functions.models import DurableOrchestrationContext
    from azure.durable_functions.orchestrator import Orchestrator

    context = DurableOrchestrationContext.from_json(context_as_string)
    context._tracker = tracker  # type: ignore

    orchestrator = Orchestrator(generator_function_tracking_replay)
    orchestrator.handle(context)

    # After first activity (old episode): replaying
    assert tracker.values_at_yield[0] == True
    # After second activity (new episode): not replaying
    assert tracker.values_at_yield[1] == False


def test_hello_cities_is_replaying_completed_without_is_played():
    """Verify intermediate is_replaying states when all three activities are completed.
    """
    tracker = IsReplayingTracker()

    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_without_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_without_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')
    add_activity_completed_events_without_is_played(context_builder, "Hello", 2, '"Hello London!"')

    context_as_string = context_builder.to_json_string()

    from azure.durable_functions.models import DurableOrchestrationContext
    from azure.durable_functions.orchestrator import Orchestrator

    context = DurableOrchestrationContext.from_json(context_as_string)
    context._tracker = tracker  # type: ignore

    orchestrator = Orchestrator(generator_function_tracking_replay)
    orchestrator.handle(context)

    # After first activity (old episode): replaying
    assert tracker.values_at_yield[0] == True
    # After second activity (old episode): replaying
    assert tracker.values_at_yield[1] == True
    # After third activity (new episode): not replaying
    assert tracker.values_at_yield[2] == False


def test_is_played_does_not_affect_is_replaying_behavior():
    """Verify that history-based detection produces the same is_replaying result
    as the is_played-based detection for one replayed timer event.
    """
    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at_1 = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str_1 = fire_at_1.strftime(DATETIME_STRING_FORMAT)
    fire_at_2 = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=60)
    fire_at_str_2 = fire_at_2.strftime(DATETIME_STRING_FORMAT)

    # Traditional backend: sets is_played=True on old events, False on new events
    traditional_backend_ctx = ContextBuilder("")
    scheduled_fire_at_1: str = traditional_backend_ctx.add_timer_created_event(0, fire_at_str_1)
    traditional_backend_ctx.add_orchestrator_completed_event()
    traditional_backend_ctx.add_orchestrator_started_event()
    traditional_backend_ctx.add_timer_fired_event(id_=0, fire_at=scheduled_fire_at_1, is_played=True)
    scheduled_fire_at_2: str = traditional_backend_ctx.add_timer_created_event(1, fire_at_str_2)
    traditional_backend_ctx.add_orchestrator_completed_event()
    traditional_backend_ctx.add_orchestrator_started_event()
    traditional_backend_ctx.add_timer_fired_event(id_=1, fire_at=scheduled_fire_at_2, is_played=False)

    result_traditional = get_orchestration_property(
        traditional_backend_ctx, generator_function, "durable_context")

    # Backend that never sets is_played (always False), relies on history structure
    history_based_ctx = ContextBuilder("", is_replaying=False)
    add_timer_fired_events_without_is_played(history_based_ctx, 0, fire_at_str_1)
    add_timer_fired_events_without_is_played(history_based_ctx, 1, fire_at_str_2)

    result_history_based = get_orchestration_property(
        history_based_ctx, generator_function, "durable_context")

    # Both approaches should agree on the final is_replaying state
    assert result_traditional.is_replaying == result_history_based.is_replaying == False
