from ..models.TaskSet import TaskSet


def task_all(state, tasks):
    """Determine the state of scheduling the activities for execution with retry options.

    :param state: The list of history events to search to determine the current
    state of the activity.
    :param tasks: The tasks to evaluate their current state.
    :return: A Durable Task Set that reports the state of running all of the tasks within it.
    """
    all_actions = []
    results = []
    is_completed = True
    for task in tasks:
        all_actions.append(task.action)
        results.append(task.result)
        if not task.is_completed:
            is_completed = False

    if is_completed:
        return TaskSet(is_completed, all_actions, results)
    else:
        return TaskSet(is_completed, all_actions, None)
