from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.models.actions.Action import Action
from azure.durable_functions.models.actions.WhenAnyAction import WhenAnyAction
from azure.durable_functions.models.actions.WhenAllAction import WhenAllAction

import enum
from typing import Any, List, Optional, Set, Union


class TaskState(enum.Enum):
    """The possible states that a Task can be in."""

    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2


class TaskBase:
    """The base class of all Tasks.

    Contains shared logic that drives all of its sub-classes. Should never be
    instantiated on its own.
    """

    def __init__(self, id_: int, actions: Union[List[Action], Action]):
        """Initialize the TaskBase.

        Parameters
        ----------
        id_ : int
            An ID for the task
        actions : List[Any]
            The list of DF actions representing this Task.
            Needed for reconstruction in the extension.
        """
        self.id: int = id_
        self.state = TaskState.RUNNING
        self.was_yielded: bool = False
        self.parent: Optional[CompoundTask] = None

        self.value: Any = None
        self.action_repr: Union[List[Action], Action] = actions
        self.is_played = False

    def set_is_played(self, is_played: bool):
        """Set the is_played flag for the Task.

        Needed for updating the orchestrator's is_replaying flag.

        Parameters
        ----------
        is_played : bool
            Whether the latest event for this Task has been played before.
        """
        self.is_played = is_played

    def change_state(self, state: TaskState):
        """Transition a running Task to a terminal state: success or failure.

        Parameters
        ----------
        state : TaskState
            The terminal state to assign to this Task

        Raises
        ------
        Exception
            When the input state is RUNNING
        """
        if state is TaskState.RUNNING:
            raise Exception("Cannot change Task to the RUNNING state.")
        self.state = state

    def set_value(self, is_error: bool, value: Any):
        """Set the value of this Task: either an exception of a result.

        Parameters
        ----------
        is_error : bool
            Whether the value represents an exception of a result.
        value : Any
            The value of this Task

        Raises
        ------
        Exception
            When the Task failed but its value was not an Exception
        """
        new_state = self.state
        if is_error:
            if not isinstance(value, Exception):
                raise Exception(f"Task ID {self.id} failed but it's value was not an Exception")
            new_state = TaskState.FAILED
        else:
            new_state = TaskState.SUCCEEDED
        self.change_state(new_state)
        self.value = value
        self.propagate()

    def propagate(self):
        """Notify parent Task of this Task's state change."""
        has_completed = not (self.state is TaskState.RUNNING)
        has_parent = not (self.parent is None)
        if has_completed and has_parent:
            self.parent.handle_completion(self)


class CompoundTask(TaskBase):
    """A Task of Tasks.

    Contains shared logic that drives all of its sub-classes.
    Should never be instantiated on its own.
    """

    def __init__(self, tasks: List[TaskBase], action_wrapper=None):
        """Instantiate CompoundTask attributes.

        Parameters
        ----------
        tasks : List[Task]
            The children/sub-tasks of this Task
        """
        super().__init__(-1, [])
        child_actions = []
        for task in tasks:
            task.parent = self
            action_repr = task.action_repr
            if isinstance(action_repr, list):
                child_actions.extend(action_repr)
            else:
                child_actions.append(action_repr)
        if action_wrapper is None:
            self.action_repr = child_actions
        else:  # replay_schema is ReplaySchema.V2
            self.action_repr = action_wrapper(child_actions)
        self._first_error: Optional[Exception] = None
        self.pending_tasks: Set[TaskBase] = set(tasks)
        self.completed_tasks: List[TaskBase] = []

    def handle_completion(self, child: TaskBase):
        """Manage sub-task completion events.

        Parameters
        ----------
        child : TaskBase
            The sub-task that completed

        Raises
        ------
        Exception
            When the calling sub-task was not registered
            with this Task's pending sub-tasks.
        """
        try:
            self.pending_tasks.remove(child)
        except KeyError:
            raise Exception(
                f"Parent Task {self.id} does not have pending sub-task with ID {child.id}."
                f"This most likely means that Task {child.id} completed twice.")

        self.completed_tasks.append(child)
        self.try_set_value(child)

    def try_set_value(self, child: TaskBase):
        """Transition a CompoundTask to a terminal state and set its value.

        Should be implemented by sub-classes.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each subclass.
        """
        raise NotImplementedError


class AtomicTask(TaskBase):
    """A Task with no subtasks."""

    pass


class WhenAllTask(CompoundTask):
    """A Task representing `when_all` scenarios."""

    def __init__(self, task: List[TaskBase], replay_schema: ReplaySchema):
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
        """Transition a WhenAll Task to a terminal state and set its value.

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
        else:  # child.state is TaskState.FAILED:
            # a single error is sufficient to fail this task
            if self._first_error is None:
                self._first_error = child.value
                self.set_value(is_error=True, value=self._first_error)


class WhenAnyTask(CompoundTask):
    """A Task representing `when_any` scenarios."""

    def __init__(self, task: List[TaskBase], replay_schema: ReplaySchema):
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
        """Transition a WhenAny Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            if self.state is TaskState.RUNNING:
                # the first completing sub-task sets the value
                self.set_value(is_error=False, value=self.value)
        else:  # child.state is TaskState.FAILED:
            if self._first_error is None:
                # the first failed task sets the value
                self._first_error = child.value

            # do not error out until all pending tasks have completed
            if len(self.pending_tasks) == 0:
                self.set_value(is_error=True, value=self._first_error)


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
        """Transition a Retryable Task to a terminal state and set its value.

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

        else:  # child.state is TaskState.FAILED:
            if self.num_attempts >= self.retry_options.max_number_of_attempts:
                # we have reached the maximum number of attempts, set error
                self.set_value(is_error=True, value=child.value)
            else:
                # still have some retries left.
                # increase size of pending tasks by adding a timer task
                # and then re-scheduling the current task after that
                # TODO: rename these calls below
                timer_task = self.context._produce_anonymous_task(parent=self)
                self.pending_tasks.add(timer_task)
                rescheduled_task = self.context._produce_anonymous_task(parent=self)
                self.pending_tasks.add(rescheduled_task)
            self.num_attempts += 1
