from ..models.TaskSet import TaskSet


def task_all(tasks):
    """Determine the state of scheduling the activities for execution with retry options.

    :param tasks: The tasks to evaluate their current state.
    :return: A Durable Task Set that reports the state of running all of the tasks within it.
    """
    all_actions = []
    results = []
    is_completed = True
<<<<<<< HEAD
    faulted = []
=======
    complete_time = None
>>>>>>> able to pass in tasksets to task_any and task_all
    for task in tasks:
        if isinstance(task, TaskSet):
            for action in task.actions:
                all_actions.append(action)
        else:
            all_actions.append(task.action)
        results.append(task.result)
<<<<<<< HEAD
<<<<<<< HEAD
        if task.is_faulted:
            faulted.append(task.exception)
=======
        
>>>>>>> able to pass in tasksets to task_any and task_all
=======

>>>>>>> fix flake8
        if not task.is_completed:
            is_completed = False
        else:
            complete_time = task.timestamp if complete_time is None \
                else max([task.timestamp, complete_time])

    if len(faulted) > 0:
        return TaskSet(is_completed, all_actions, results, is_faulted=True, exception=faulted[0])
    if is_completed:
        return TaskSet(is_completed, all_actions, results, False, complete_time)
    else:
        return TaskSet(is_completed, all_actions, None)
