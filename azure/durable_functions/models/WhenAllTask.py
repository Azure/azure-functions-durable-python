from azure.durable_functions.models.actions.WhenAllAction import WhenAllAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.models.Task import Task
from typing import Any, List
from azure.durable_functions.models.NewTask import CompoundTask, TaskBase, TaskState


class WhenAllTask(CompoundTask):
    """A Task representing `when_all` scenarios.
    """

    def __init__(self, task: List[Task], replay_schema: ReplaySchema):
        """Initialize a WhenAllTask.

        Parameters
        ----------
        task : List[Task]
            The list of child tasks
        replay_schema : ReplaySchema
            The ReplaySchema, which determines the inner action payload representation
        """
        action_wrapper = None
        if replay_schema is ReplaySchema.V2:
            action_wrapper = WhenAllAction
        super().__init__(task, action_wrapper)

    def try_set_value(self, child: TaskBase):
        """Tries to transition a WhenAll Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            # A WhenAll Task only completes when it has no pending tasks
            # i.e _when all_ of its children have completed
            if len(self.pending_tasks) == 0:
                results = list(map(lambda x: x.value, self.completed_tasks))
                self.set_value(is_error=False, value=results)
        else: # child.state is TaskState.FAILED:
            # a single error is sufficient to fail this task
            if self._first_error is None:
                self._first_error = child.value
                self.set_value(is_error= True, value=self._first_error)