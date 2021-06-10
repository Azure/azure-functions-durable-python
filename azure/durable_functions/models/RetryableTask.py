from typing import Any
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.WhenAllTask import WhenAllTask
from azure.durable_functions.models.NewTask import TaskState
from azure.durable_functions.models.Task import Task

class RetryAbleTask(WhenAllTask):
    def __init__(self, child: Task, retry_options: RetryOptions, context):
        id_ = child.id
        tasks = [child]
        super().__init__(tasks)

        self.retry_options = retry_options
        self.num_attempts = 1
        self.context = context
        self.actions = child.actions

    def process_error(self, error: Exception):

        if self.num_attempts >= self.retry_options.max_number_of_attempts:
            self.set_error(error)
        else:
            timer_task = self.context._schedule_implicit_child_task(self)
            self.pending_tasks.add(timer_task)
            rescheduled_task = self.context._schedule_implicit_child_task(self)
            self.pending_tasks.add(rescheduled_task)
        self.num_attempts += 1

    def process_result(self, result: Any):
        if len(self.pending_tasks) == 0:
            if self.state is self.state.RUNNING:
                if self._first_error is None: 
                    self.set_result(result.result)
            elif self.state is TaskState.SUCCEEDED:
                raise Exception("TBD")