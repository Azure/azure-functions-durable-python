from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.WhenAllTask import WhenAllTask
from azure.durable_functions.models.NewTask import TaskBase, TaskState

class RetryAbleTask(WhenAllTask):
    """A Task representing `with_retry` scenarios.

    It inherits from WhenAllTask because retryable scenarios are Tasks
    with equivalent to WhenAll Tasks with dynamically increasing lists
    of children. At every failure, we add a Timer child and a Task child
    to the list of pending tasks. 
    """

    def __init__(self, child: TaskBase, retry_options: RetryOptions, context):
        self.id_ = str(child.id) + "_retryable_proxy"
        tasks = [child]
        super().__init__(tasks, context._replay_schema)

        self.retry_options = retry_options
        self.num_attempts = 1
        self.context = context
        self.actions = child.action_repr
    

    def try_set_value(self, child: TaskBase):
        """Tries to transition a Retryable Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            if len(self.pending_tasks) == 0:
                # if all pending tasks have completed,
                # and we have a successful child, then
                # we can set the Task's event
                self.set_value(is_error=False, value=child.value)


        else: # child.state is TaskState.FAILED:
            if self.num_attempts >= self.retry_options.max_number_of_attempts:
                # we have reached the maximum number of attempts, set error
                self.set_value(is_error=True, value=child.value)
            else:
                # still have some retries left.
                # increase size of pending tasks by adding a timer task
                # and then re-scheduling the current task after that
                # TODO: rename these calls below
                timer_task = self.context._schedule_implicit_child_task(self)
                self.pending_tasks.add(timer_task)
                rescheduled_task = self.context._schedule_implicit_child_task(self)
                self.pending_tasks.add(rescheduled_task)
            self.num_attempts += 1