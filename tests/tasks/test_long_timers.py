import datetime

import pytest
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.Task import LongTimerTask, TaskState, TimerTask
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction


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
