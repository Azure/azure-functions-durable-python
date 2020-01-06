import logging

from ..models.history import HistoryEventType


def should_suspend(partial_result) -> bool:
    logging.warning("!!!shouldSuspend")
    return bool(partial_result is not None
                and hasattr(partial_result, "isCompleted")
                and not partial_result.isCompleted)


def _parse_history_event(directive_result):
    event_type = directive_result.get("EventType")
    if event_type is None:
        raise ValueError("EventType is not found in task object")

    if event_type == HistoryEventType.EventRaised:
        return directive_result["Input"]
    if event_type == HistoryEventType.SubOrchestrationInstanceCreated:
        return directive_result["Result"]
    if event_type == HistoryEventType.TaskCompleted:
        return directive_result["Result"]
    return None


def _find_task_scheduled(state, name):
    if not name:
        raise ValueError("Name cannot be empty")

    tasks = list(
        filter(lambda e: not (
                (not (e["EventType"] == HistoryEventType.TaskScheduled) or not (e["Name"] == name)) or e.get(
            "IsProcessed")), state))

    logging.warning(f"!!! findTaskScheduled {tasks}")
    if len(tasks) == 0:
        return None

    return tasks[0]


def _find_task_completed(state, scheduled_task):
    if scheduled_task is None:
        return None

    tasks = list(
        filter(lambda e: not (not (e["EventType"] == HistoryEventType.TaskCompleted) or not (
                e.get("TaskScheduledId") == scheduled_task["EventId"])),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def _find_task_failed(state, scheduled_task):
    if scheduled_task is None:
        return None

    tasks = list(
        filter(lambda e: not (not (e["EventType"] == HistoryEventType.TaskFailed) or not (
                e.get("TaskScheduledId") == scheduled_task["EventId"])),
               state))

    if len(tasks) == 0:
        return None

    return tasks[0]


def _set_processed(tasks):
    for task in tasks:
        if task is not None:
            logging.warning(f"!!!task {task.get('IsProcessed')}"
                            f"{task.get('Name')}")
            task["IsProcessed"] = True
            logging.warning(f"!!!after_task {task.get('IsProcessed')}"
                            f"{task.get('Name')}")
