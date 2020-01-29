from ..models.TaskSet import TaskSet


def task_any(tasks):
    """Determine whether any of the given tasks is completed.

    Parameters
    ----------
    tasks : Task
        The tasks to evaluate their current state.

    Returns
    -------
    TaskSet
        Returns a completed Durable Task Set if any of the tasks is completed.
        Returns a not completed Durable Task Set if none of the tasks are completed.
        Returns a faulted Taskset if all tasks are faulted
    """
    all_actions = []
    completed_tasks = []
    faulted_tasks = []

    for task in tasks:
        all_actions.append(task.action)
        if task.is_completed:
            completed_tasks.append(task)
        if task.is_faulted:
            faulted_tasks.append(task)

    completed_tasks.sort(key=lambda t: t.timestamp)

    if len(faulted_tasks) == len(tasks):
        return TaskSet(False, all_actions, None, is_faulted=True)
    elif len(completed_tasks) != 0:
        return TaskSet(True, all_actions, completed_tasks[0])
    else:
        return TaskSet(False, all_actions, None)
