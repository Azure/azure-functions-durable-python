from azure.durable_functions.models.actions import WhenAnyAction
from azure.durable_functions.models.Task import Task
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from typing import Any, List
from azure.durable_functions.models.NewTask import CompoundTask, TaskBase, TaskState


class WhenAnyTask(CompoundTask):
    """A Task representing `when_any` scenarios.
    """

    def __init__(self, task: List[Task], replay_schema: ReplaySchema):
        """Initialize a WhenAnyTask.

        Parameters
        ----------
        task : List[Task]
            The list of child tasks
        replay_schema : ReplaySchema
            The ReplaySchema, which determines the inner action payload representation
        """
        action_wrapper = None
        if replay_schema is ReplaySchema.V2:
            action_wrapper = WhenAnyAction
        super().__init__(task, action_wrapper)

    def try_set_value(self, child: TaskBase):
        """Tries to transition a WhenAny Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            if self.state is TaskState.RUNNING:
                # the first completing sub-task sets the value
                self.set_value(is_error=False, value=self.value)
        else: #child.state is TaskState.FAILED:
            if self._first_error is None:
                # the first failed task sets the value
                self._first_error = child.value

            # do not error out until all pending tasks have completed
            if len(self.pending_tasks) == 0:
                self.set_value(is_error=True, value=self._first_error)