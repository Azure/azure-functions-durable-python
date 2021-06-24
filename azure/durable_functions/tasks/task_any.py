from azure.durable_functions.models.actions.WhenAnyAction import WhenAnyAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from ..models.TaskSet import TaskSet


def task_any(tasks, replay_schema: ReplaySchema):
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
            if replay_schema == ReplaySchema.V1:
                all_actions.extend(task.actions)
            else:
                all_actions.append(task.actions)
        else:
            all_actions.append(task.action)

        if task.is_faulted:
            faulted_tasks.append(task)
            error_message.append(task.exception)
        elif task.is_completed:
            completed_tasks.append(task)

    completed_tasks.sort(key=lambda t: t.timestamp)

    if replay_schema == ReplaySchema.V2:
        all_actions = WhenAnyAction(all_actions)

    if len(faulted_tasks) == len(tasks):
        return TaskSet(True, all_actions, None, is_faulted=True, exception=Exception(
            f"All tasks have failed, errors messages in all tasks:{error_message}"))
    elif len(completed_tasks) != 0:
        return TaskSet(True, all_actions, completed_tasks[0], False, completed_tasks[0].timestamp)
    else:
        return TaskSet(False, all_actions, None)
