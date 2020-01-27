import json, datetime
from ..models.history import HistoryEventType, HistoryEvent
from ..models.Task import Task
from typing import List

def should_suspend(partial_result) -> bool:
    """Check the state of the result to determine if the orchestration should suspend."""
    return bool(partial_result is not None
                and hasattr(partial_result, "is_completed")
                and not partial_result.is_completed)


def parse_history_event(directive_result):
    """Based on the type of event, parse the JSON.serializable portion of the event."""
    event_type = directive_result.get("EventType")
    if event_type is None:
        raise ValueError("EventType is not found in task object")

    if event_type == HistoryEventType.EVENT_RAISED:
        return json.loads(directive_result["Input"])
    if event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_CREATED:
        return json.loads(directive_result["Result"])
    if event_type == HistoryEventType.TASK_COMPLETED:
        return json.loads(directive_result["Result"])
    return None


def find_event_raised(state, name):
    """Find if the event with the given event name is raised.

    Parameters
    ----------
    state : List[HistoryEvent]
        List of histories to search from
    name : str
        Name of the event to search for

    Returns
    -------
    HistoryEvent
        The raised event with the given event name that has not yet been processed.
        Returns None if no event with the given conditions was found.

    Raises
    ------
    ValueError
        Raises an error if no name was given when calling this function.
    """
    if not name:
        raise ValueError("Name cannot be empty")

    tasks = list(
        filter(lambda e: not (
                (not (e["EventType"] == HistoryEventType.EVENT_RAISED)
                    or not (e["Name"] == name))
            or e.get("IsProcessed")), state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_scheduled(state, name):
    """Locate the Scheduled Task.

    Within the state passed, search for an event that has hasn't been processed
    and has the the name provided.
    """
    if not name:
        raise ValueError("Name cannot be empty")

    tasks = list(
        filter(lambda e:
               not ((not ((e["EventType"] == HistoryEventType.TASK_SCHEDULED) and (
                    e["Name"] == name))) or e.get("IsProcessed")),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_completed(state, scheduled_task):
    """Locate the Completed Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a completed task type,
    and has the a scheduled id that equals the EventId of the provided scheduled task.
    """
    if scheduled_task is None:
        return None

    tasks = list(
        filter(lambda e:
               not (not (e["EventType"] == HistoryEventType.TASK_COMPLETED) or not (
                    e.get("TaskScheduledId") == scheduled_task["EventId"])),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_failed(state, scheduled_task):
    """Locate the Failed Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a failed task type,
    and has the a scheduled id that equals the EventId of the provided scheduled task.
    """
    if scheduled_task is None:
        return None

    tasks = list(
        filter(lambda e:
               not (not (e["EventType"] == HistoryEventType.TASK_FAILED) or not (
                    e.get("TaskScheduledId") == scheduled_task["EventId"])), state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_retry_timer_created(state, failed_task):
    """Locate the Timer Created Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer created task type,
    and has the an event id that is one higher then Scheduled Id of the provided
    failed task provided.
    """
    if failed_task is None:
        return None

    tasks = list(
        filter(lambda e:
               not (not (e["EventType"] == HistoryEventType.TIMER_CREATED) or not (
                    e.get("EventId") == failed_task["TaskScheduledId"] + 1)),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_retry_timer_fired(state, retry_timer_created):
    """Locate the Timer Fired Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer fired task type,
    and has the an timer id that is equal to the EventId of the provided
    timer created task provided.
    """
    if retry_timer_created is None:
        return None

    tasks = list(
        filter(lambda e: not (
               not (e["EventType"] == HistoryEventType.TIMER_FIRED)
               or not (e.get("TimerId") == retry_timer_created["EventId"])),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def set_processed(tasks):
    """Set the isProcessed attribute of all of the tasks to true.

    This provides the ability to not look at events that have already been processed within
    searching the history of events.
    """
    for task in tasks:
        if task is not None:
            task["IsProcessed"] = True

def find_timer_created(state, fire_at):

    if fire_at is None:
        return None

    tasks = list(
        filter(lambda e:
               not(not (e["EventType"] == HistoryEventType.TIMER_CREATED) 
                   or not (e["FireAt"] == fire_at)),
               state))
    if tasks:
        return tasks[0]
    else:
        return None

# TODO remove this duplicate? and reuse 
def find_timer_fired(state ,created_timer):
    """Locate the Timer Fired Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer fired task type,
    and has the an timer id that is equal to the EventId of the provided
    timer created task provided.
    """
    if created_timer is None:
        return None

    tasks = list(
        filter(lambda e: not (
               not (e["EventType"] == HistoryEventType.TIMER_FIRED)
               or not (e.get("TimerId") == created_timer["EventId"])),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]