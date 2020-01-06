from ..models.TaskSet import TaskSet


def task_all(state, tasks):
    all_actions = []
    results = []
    is_completed = True
    for task in tasks:
        all_actions.append(task.action)
        results.append(task.result)
        if not task.isCompleted:
            is_completed = False

    if is_completed:
        return TaskSet(is_completed, all_actions, results)
    else:
        return TaskSet(is_completed, all_actions, None)
