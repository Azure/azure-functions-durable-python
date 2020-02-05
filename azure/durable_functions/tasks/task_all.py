from ..models.TaskSet import TaskSet


def task_all(tasks):
    """Determine the state of scheduling the activities for execution with retry options.

    :param tasks: The tasks to evaluate their current state.
    :return: A Durable Task Set that reports the state of running all of the tasks within it.
    """
    all_actions = []
    results = []
    is_completed = True
    faulted = []
    for task in tasks:
        all_actions.append(task.action)
        results.append(task.result)
        if task.is_faulted:
            faulted.append(task.exception)
        if not task.is_completed:
            is_completed = False

    if len(faulted) > 0:
        return TaskSet(is_completed, all_actions, results, is_faulted=True, exception=faulted[0])
    if is_completed:
        return TaskSet(is_completed, all_actions, results)
    else:
        return TaskSet(is_completed, all_actions, None)
