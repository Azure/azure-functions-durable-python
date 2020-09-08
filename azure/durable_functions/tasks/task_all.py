from datetime import datetime
from typing import List, Optional, Any

from ..models.Task import Task
from ..models.TaskSet import TaskSet
from ..models.actions import Action


def task_all(tasks: List[Task]):
    """Determine the state of scheduling the activities for execution with retry options.

    Parameters
    ----------
    tasks: List[Task]
        The tasks to evaluate their current state.

    Returns
    -------
    TaskSet
        A Durable Task Set that reports the state of running all of the tasks within it.
    """
    # Args for constructing the output TaskSet
    is_played = True
    is_faulted = False
    is_completed = True

    actions: List[Action] = []
    results: List[Any] = []

    exception: Optional[str] = None
    end_time: Optional[datetime] = None

    for task in tasks:
        # Add actions and results
        if isinstance(task, TaskSet):
            actions.extend(task.actions)
        else:
            # We know it's an atomic Task
            actions.append(task.action)
        results.append(task.result)

        # Record first exception, if it exists
        if task.is_faulted and not is_faulted:
            is_faulted = True
            exception = task.exception

        # If any task is not played, TaskSet is not played
        if not task._is_played:
            is_played = False

        # If any task is incomplete, TaskSet is incomplete
        # If the task is complete, we can update the end_time
        if not task.is_completed:
            is_completed = False
        elif end_time is None:
            end_time = task.timestamp
        else:
            end_time = max([task.timestamp, end_time])

    # Incomplete TaskSets do not have results or end-time
    if not is_completed:
        results = None
        end_time = None

    # Construct TaskSet
    taskset = TaskSet(
        is_completed=is_completed,
        actions=actions,
        result=results,
        is_faulted=is_faulted,
        timestamp=end_time,
        exception=exception,
        is_played=is_played
    )
    return taskset
