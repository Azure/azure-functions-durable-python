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
    error_message = []
    for task in tasks:
        if isinstance(task, TaskSet):
            for action in task.actions:
                all_actions.append(action)
        else:
            all_actions.append(task.action)

        if task.is_faulted:
            faulted_tasks.append(task)
            error_message.append(task.exception)
        elif task.is_completed:
            completed_tasks.append(task)

    completed_tasks.sort(key=lambda t: t.timestamp)

    if len(faulted_tasks) == len(tasks):
        return TaskSet(True, all_actions, None, is_faulted=True, exception=Exception(
            f"All tasks have failed, errors messages in all tasks:{error_message}"))
    elif len(completed_tasks) != 0:
        return TaskSet(True, all_actions, completed_tasks[0], False, completed_tasks[0].timestamp)
    else:
        return TaskSet(False, all_actions, None)
