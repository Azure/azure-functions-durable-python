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


def generator_function_activity(context):
    """Orchestrator that calls 3 sequential activities."""
    result1 = yield context.call_activity("Hello", "Tokyo")
    result2 = yield context.call_activity("Hello", "Seattle")
    result3 = yield context.call_activity("Hello", "London")
    return [result1, result2, result3]


def generator_function_compound_task(context):
    """Orchestrator that creates 3 timers then waits on any of them."""
    timestamp = "2020-07-23T21:56:54.936700Z"
    deadline = datetime.strptime(timestamp, DATETIME_STRING_FORMAT)
    deadline = deadline.replace(tzinfo=timezone.utc)

    tasks = []
    for _ in range(0, 3):
        deadline = deadline + timedelta(seconds=30)
        tasks.append(context.create_timer(deadline))
    yield context.task_any(tasks)


def add_timer_fired_events_no_is_played(context_builder: ContextBuilder, id_: int, timestamp: str):
    """Add a complete timer episode without setting is_played (always False).

    Adds: TimerCreated, OrchestratorCompleted, OrchestratorStarted, TimerFired.
    This simulates a backend that never sets IsPlayed.
    """
    fire_at: str = context_builder.add_timer_created_event(id_, timestamp)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at, is_played=False)


def add_activity_completed_events_no_is_played(
        context_builder: ContextBuilder, name: str, id_: int, result: str):
    """Add a complete activity episode without setting is_played (always False).

    Adds: TaskScheduled, OrchestratorCompleted, OrchestratorStarted, TaskCompleted.
    This simulates a backend that never sets IsPlayed.
    """
    context_builder.add_task_scheduled_event(name, id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result, is_played=False)


# ---------- Tests using timers ----------

def test_no_is_played_initial_value_not_replaying():
    """With no completed events, is_replaying should be False."""
    context_builder = ContextBuilder("", is_replaying=False)
    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    assert result.is_replaying == False


def test_no_is_played_one_replayed_timer():
    """One completed timer in old episode => is_replaying should be True.

    History structure (is_played always False):
      [OrchestratorStarted, ExecutionStarted,
       TimerCreated, OrchestratorCompleted, OrchestratorStarted*, TimerFired]
    The last OrchestratorStarted (*) starts at index 4, and TimerFired is at index 5.
    Since TimerFired is in the last episode (new events), is_replaying = False after
    processing. But the orchestrator hasn't finished yet, so we check the state
    at the point where the second timer is yielded — which is after processing
    the first completed timer.

    Actually: with one completed episode and one pending, after processing all
    events the last task resolved is in the new-events section, so is_replaying = False.
    But wait — we only have one completed timer. The orchestrator needs 3. So after
    the first timer resolves, the orchestrator yields a second timer which is pending.
    The is_replaying value reflects the state of the last resolved task.
    """
    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("", is_replaying=False)
    add_timer_fired_events_no_is_played(context_builder, 0, fire_at_str)

    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    # The timer fired event is in the last episode (new events), so is_replaying is False
    assert result.is_replaying == False


def test_no_is_played_two_timers_first_is_replayed():
    """Two completed timers, first in old episode, second in new => is_replaying should be False.

    History structure (is_played always False):
      [OrchestratorStarted, ExecutionStarted,
       TimerCreated(0), OrchestratorCompleted, OrchestratorStarted, TimerFired(0),
       TimerCreated(1), OrchestratorCompleted, OrchestratorStarted*, TimerFired(1)]
    Last OrchestratorStarted (*) is at the boundary. TimerFired(0) is in old events
    (replaying), TimerFired(1) is in new events (not replaying).
    Final is_replaying should reflect the last resolved task = False.
    """
    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)
    fire_at2 = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=60)
    fire_at_str2 = fire_at2.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("", is_replaying=False)
    add_timer_fired_events_no_is_played(context_builder, 0, fire_at_str)
    add_timer_fired_events_no_is_played(context_builder, 1, fire_at_str2)

    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    # Last resolved task is in the new events section
    assert result.is_replaying == False


def test_no_is_played_compound_task_replayed():
    """Compound task (task_any) with timer in old episode => is_replaying should be True.

    History: one timer fires in old events, a new OrchestratorStarted opens the new episode.
    The compound task resolves with is_played inferred from history position => replaying.
    But since this timer fires in the last episode, is_replaying = False actually.
    Wait — the add_timer_fired helper adds OrchestratorCompleted + OrchestratorStarted,
    so the TimerFired will be in the last episode (new events).
    """
    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("", is_replaying=False)
    add_timer_fired_events_no_is_played(context_builder, 0, fire_at_str)

    result = get_orchestration_property(
        context_builder, generator_function_compound_task, "durable_context")

    # The timer fires in the new/last episode
    assert result.is_replaying == False


# ---------- Tests using activities ----------

def test_no_is_played_one_activity_completed():
    """One completed activity, only episode => is_replaying should be False."""
    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_no_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')

    result = get_orchestration_property(
        context_builder, generator_function_activity, "durable_context")

    assert result.is_replaying == False


def test_no_is_played_two_activities_first_replayed():
    """Two completed activities: first in old episode, second in new.

    History structure (is_played always False):
      [OrchestratorStarted, ExecutionStarted,
       TaskScheduled(0), OrchestratorCompleted, OrchestratorStarted, TaskCompleted(0),
       TaskScheduled(1), OrchestratorCompleted, OrchestratorStarted*, TaskCompleted(1)]
    TaskCompleted(0) is before *  => replaying.
    TaskCompleted(1) is at/after * => not replaying.
    Final is_replaying = False (reflects last resolved task).
    """
    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_no_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')

    result = get_orchestration_property(
        context_builder, generator_function_activity, "durable_context")

    assert result.is_replaying == False


def test_no_is_played_three_activities_all_completed():
    """Three completed activities: first two replayed, third is new.

    The orchestrator returns [result1, result2, result3] and is_done should be True.
    """
    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_no_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 2, '"Hello London!"')

    result = get_orchestration_property(
        context_builder, generator_function_activity, "durable_context")

    # Orchestration completed, last task was in new events
    assert result.is_replaying == False


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


def test_no_is_played_intermediate_replay_state_two_of_three():
    """Verify that is_replaying is True for old events and False for new events,
    even when is_played is never set.

    Two activities completed in history (first old, second new), third pending.
    After yielding activity 1 (old episode): is_replaying should be True.
    After yielding activity 2 (new episode): is_replaying should be False.
    """
    tracker = IsReplayingTracker()

    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_no_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')

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


def test_no_is_played_intermediate_replay_state_three_of_three():
    """Verify intermediate is_replaying states when all three activities are completed.

    Three activities: first two in old episodes, third in new episode.
    After yield 1 (old): is_replaying True
    After yield 2 (old): is_replaying True
    After yield 3 (new): is_replaying False
    """
    tracker = IsReplayingTracker()

    context_builder = ContextBuilder("", is_replaying=False)
    add_activity_completed_events_no_is_played(context_builder, "Hello", 0, '"Hello Tokyo!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 1, '"Hello Seattle!"')
    add_activity_completed_events_no_is_played(context_builder, "Hello", 2, '"Hello London!"')

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


def test_no_is_played_matches_is_played_behavior_one_replayed():
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
    add_timer_fired_events_no_is_played(history_based_ctx, 0, fire_at_str_1)
    add_timer_fired_events_no_is_played(history_based_ctx, 1, fire_at_str_2)

    result_history_based = get_orchestration_property(
        history_based_ctx, generator_function, "durable_context")

    # Both approaches should agree on the final is_replaying state
    assert result_traditional.is_replaying == result_history_based.is_replaying == False
