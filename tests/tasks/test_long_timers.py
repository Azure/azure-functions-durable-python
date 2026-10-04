import datetime
import json

import pytest
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.Task import LongTimerTask, TaskState, TimerTask
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.orchestrator import Orchestrator
from tests.test_utils.ContextBuilder import ContextBuilder


@pytest.fixture
def starting_context_v3():
    context = DurableOrchestrationContext.from_json(
        '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,'
        '"Timestamp":"'
        f'{datetime.datetime.now(datetime.timezone.utc).isoformat()}'
        '"}, {"OrchestrationInstance":{'
        '"InstanceId":"48d0f95957504c2fa579e810a390b938", '
        '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,'
        '"ParentInstance":null, '
        '"Name":"DurableOrchestratorTrigger","Version":"","Input":"null",'
        '"Tags":null,"EventId":-1,"IsPlayed":false, '
        '"Timestamp":"'
        f'{datetime.datetime.now(datetime.timezone.utc).isoformat()}'
        '"}],"input":null,'
        '"instanceId":"48d0f95957504c2fa579e810a390b938", '
        '"upperSchemaVersion": 2, '
        '"upperSchemaVersionNew": 3, '
        '"isReplaying":false,"parentInstanceId":null, '
        '"maximumShortTimerDuration":"0.16:00:00", '
        '"longRunningTimerIntervalDuration":"0.08:00:00" } ')
    return context


def test_durable_context_creates_correct_timer(starting_context_v3):
    timer = starting_context_v3.create_timer(datetime.datetime.now(datetime.timezone.utc) +
                                             datetime.timedelta(minutes=30))
    assert isinstance(timer, TimerTask)

    timer2 = starting_context_v3.create_timer(datetime.datetime.now(datetime.timezone.utc) +
                                              datetime.timedelta(days=1))
    assert isinstance(timer2, LongTimerTask)

def test_long_timer_fires_appropriately(starting_context_v3):
    starting_time = starting_context_v3.current_utc_datetime
    final_fire_time = starting_time + datetime.timedelta(hours=20)
    long_timer_action = CreateTimerAction(final_fire_time)
    long_timer = LongTimerTask(None, long_timer_action, starting_context_v3)
    assert long_timer.action.fire_at == final_fire_time
    assert long_timer.action == long_timer_action

    # Check the first "inner" timer and simulate firing it
    short_timer = long_timer.pending_tasks.pop()
    assert short_timer.action_repr.fire_at == starting_time + datetime.timedelta(hours=8)
    # This happens when the task is reconstructed during replay, doing it manually for the test
    long_timer._orchestration_context.current_utc_datetime = short_timer.action_repr.fire_at
    short_timer.state = TaskState.SUCCEEDED 
    long_timer.try_set_value(short_timer)

    assert long_timer.state == TaskState.RUNNING

    # Check the scond "inner" timer and simulate firing it. This one should be set to the final
    # fire time, the remaining time (12 hours) is less than the max long timer duration (16 hours)
    short_timer = long_timer.pending_tasks.pop()
    assert short_timer.action_repr.fire_at == final_fire_time
    long_timer._orchestration_context.current_utc_datetime = short_timer.action_repr.fire_at
    short_timer.state = TaskState.SUCCEEDED 
    long_timer.try_set_value(short_timer)

    # Ensure the LongTimerTask finished
    assert len(long_timer.pending_tasks) == 0
    assert long_timer.state == TaskState.SUCCEEDED


@pytest.mark.parametrize("completed_chunk", [False, True])
def test_cancel_long_timer_cancels_pending_chunk(starting_context_v3, completed_chunk):
    context = starting_context_v3
    timer = context.create_timer(context.current_utc_datetime + datetime.timedelta(days=2))
    first_chunk = next(iter(timer.pending_tasks))
    if completed_chunk:
        context.current_utc_datetime = first_chunk.action_repr.fire_at
        first_chunk.set_value(False, None)

    pending_chunk = next(iter(timer.pending_tasks))
    timer.cancel()
    timer.cancel()  # Like short timers, cancellation is idempotent before completion.

    assert timer.is_canceled()
    assert pending_chunk.is_cancelled
    if completed_chunk:
        assert not first_chunk.is_cancelled


@pytest.mark.parametrize("completed_chunk", [False, True])
def test_approval_cancels_serialized_long_timer(completed_chunk):
    def approval(context):
        event = context.wait_for_external_event("approved")
        timer = context.create_timer(context.current_utc_datetime + datetime.timedelta(days=2))
        winner = yield context.task_any([event, timer])
        if winner == event:
            timer.cancel()
            return True
        return False

    builder = ContextBuilder("approval", increase_time=False, replay_schema=ReplaySchema.V3)
    first_fire = builder.current_datetime + datetime.timedelta(hours=8)
    builder.add_timer_created_event(0, first_fire.isoformat())
    builder.add_orchestrator_completed_event()
    if completed_chunk:
        builder.current_datetime = first_fire
        builder.add_orchestrator_started_event()
        builder.add_timer_fired_event(0, first_fire.isoformat())
        second_fire = first_fire + datetime.timedelta(hours=8)
        builder.add_timer_created_event(1, second_fire.isoformat())
        builder.add_orchestrator_completed_event()
    builder.add_orchestrator_started_event()
    builder.add_event_raised_event("approved", -1, "true")
    context = DurableOrchestrationContext.from_json(builder.to_json_string(
        maximumShortTimerDuration="0.16:00:00",
        longRunningTimerIntervalDuration="0.08:00:00"))

    result = json.loads(Orchestrator(approval).handle(context))
    assert result["isDone"]
    assert result["output"] is True

    def timer_actions(actions):
        for action in actions:
            if "isCanceled" in action:
                yield action
            yield from timer_actions(action.get("compoundActions", []))

    timers = list(timer_actions([action for group in result["actions"] for action in group]))
    assert len(timers) == (2 if completed_chunk else 1)
    assert timers[-1]["isCanceled"]
    if completed_chunk:
        assert not timers[0]["isCanceled"]


def test_cancelled_long_timer_does_not_schedule_another_chunk(starting_context_v3):
    context = starting_context_v3
    timer = context.create_timer(context.current_utc_datetime + datetime.timedelta(days=2))
    chunk = next(iter(timer.pending_tasks))
    timer.cancel()

    # A firing already in history must not restart the cancelled timer.
    context.current_utc_datetime = chunk.action_repr.fire_at
    chunk.set_value(False, None)

    assert not timer.pending_tasks
    assert not any(context._actions)
