from datetime import datetime
from azure.durable_functions.models.actions.NoOpAction import NoOpAction
from azure.durable_functions.models.actions.CompoundAction import CompoundAction
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.models.actions.Action import Action
from azure.durable_functions.models.actions.WhenAnyAction import WhenAnyAction
from azure.durable_functions.models.actions.WhenAllAction import WhenAllAction
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction

import enum
from typing import Any, List, Optional, Set, Type, Union


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

    def __init__(self, id_: Union[int, str], actions: Union[List[Action], Action]):
        """Initialize the TaskBase.

        Parameters
        ----------
        id_ : int
            An ID for the task
        actions : List[Any]
            The list of DF actions representing this Task.
            Needed for reconstruction in the extension.
        """
        self.id: Union[int, str] = id_
        self.state = TaskState.RUNNING
        self.parent: Optional[CompoundTask] = None
        self._api_name: str

        api_action: Union[Action, Type[CompoundAction]]
        if isinstance(actions, list):
            if len(actions) == 1:
                api_action = actions[0]
            else:
                api_action = CompoundAction
        else:
            api_action = actions

        self._api_name = api_action.__class__.__name__

        self.result: Any = None
        self.action_repr: Union[List[Action], Action] = actions
        self.is_played = False
        self._is_scheduled_flag = False

    @property
    def _is_scheduled(self) -> bool:
        return self._is_scheduled_flag

    def _set_is_scheduled(self, is_scheduled: bool):
        self._is_scheduled_flag = is_scheduled

    @property
    def is_completed(self) -> bool:
        """Get indicator of whether the task completed.

        Note that completion is not equivalent to success.
        """
        return not (self.state is TaskState.RUNNING)

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
                if not (isinstance(value, TaskBase) and isinstance(value.result, Exception)):
                    err_message = f"Task ID {self.id} failed but it's value was not an Exception"
                    raise Exception(err_message)
            new_state = TaskState.FAILED
        else:
            new_state = TaskState.SUCCEEDED
        self.change_state(new_state)
        self.result = value
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

    def __init__(self, tasks: List[TaskBase], compound_action_constructor=None):
        """Instantiate CompoundTask attributes.

        Parameters
        ----------
        tasks : List[Task]
            The children/sub-tasks of this Task
        compound_action_constructor : Union[WhenAllAction, WhenAnyAction, None]
            Either None or, a WhenAllAction or WhenAnyAction constructor.
            It is None when using the V1 replay protocol, where no Compound Action
            objects size and compound actions are represented as arrays of actions.
            It is not None when using the V2 replay protocol.
        """
        super().__init__(-1, [])
        child_actions = []
        for task in tasks:
            task.parent = self
            action_repr = task.action_repr
            if isinstance(action_repr, list):
                child_actions.extend(action_repr)
            else:
                if not task._is_scheduled:
                    child_actions.append(action_repr)
        if compound_action_constructor is None:
            self.action_repr = child_actions
        else:  # replay_schema >= ReplaySchema.V2
            self.action_repr = compound_action_constructor(child_actions)
        self._first_error: Optional[Exception] = None
        self.pending_tasks: Set[TaskBase] = set(tasks)
        self.completed_tasks: List[TaskBase] = []
        self.children = tasks

        if len(self.children) == 0:
            self.state = TaskState.SUCCEEDED

        # Sub-tasks may have already completed, so we process them
        for child in self.children:
            if not (child.state is TaskState.RUNNING):
                self.handle_completion(child)

    @property
    def _is_scheduled(self) -> bool:
        return all([child._is_scheduled for child in self.children])

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
        self.set_is_played(child.is_played)
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

    def _get_action(self) -> Action:
        action: Action
        if isinstance(self.action_repr, list):
            action = self.action_repr[0]
        else:
            action = self.action_repr
        return action


class TimerTask(AtomicTask):
    """A Timer Task."""

    def __init__(self, id_: Union[int, str], action: CreateTimerAction):
        super().__init__(id_, action)
        self.action_repr: Union[List[CreateTimerAction], CreateTimerAction]

    @property
    def is_cancelled(self) -> bool:
        """Check if the Timer is cancelled.

        Returns
        -------
        bool
            Returns whether a timer has been cancelled or not
        """
        action: CreateTimerAction = self._get_action()
        return action.is_cancelled

    def cancel(self):
        """Cancel a timer.

        Raises
        ------
        ValueError
            Raises an error if the task is already completed and an attempt is made to cancel it
        """
        if not self.is_completed:
            action: CreateTimerAction = self._get_action()
            action.is_cancelled = True
        else:
            raise ValueError("Cannot cancel a completed task.")


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
        compound_action_constructor = None
        if replay_schema.value >= ReplaySchema.V2.value:
            compound_action_constructor = WhenAllAction
        super().__init__(task, compound_action_constructor)

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
                results = list(map(lambda x: x.result, self.children))
                self.set_value(is_error=False, value=results)
        else:  # child.state is TaskState.FAILED:
            # a single error is sufficient to fail this task
            if self._first_error is None:
                self._first_error = child.result
                self.set_value(is_error=True, value=self._first_error)


class LongTimerTask(WhenAllTask):
    """A Timer Task for intervals longer than supported by the storage backend."""

    def __init__(self, id_, action: CreateTimerAction, orchestration_context):
        """Initialize a LongTimerTask.

        Parameters
        ----------
        id_ : int
            An ID for the task
        action : CreateTimerAction
            The action this task represents
        orchestration_context: DurableOrchestrationContext
            The orchestration context this task was created in
        """
        current_time = orchestration_context.current_utc_datetime
        final_fire_time = action.fire_at
        duration_until_fire = final_fire_time - current_time

        if duration_until_fire > orchestration_context._maximum_short_timer_duration:
            next_fire_time = current_time + orchestration_context._long_timer_interval_duration
        else:
            next_fire_time = final_fire_time

        next_timer_action = CreateTimerAction(next_fire_time)
        next_timer_task = TimerTask(None, next_timer_action)
        super().__init__([next_timer_task], orchestration_context._replay_schema)

        self.id = id_
        self.action = action
        self._orchestration_context = orchestration_context
        self._max_short_timer_duration = self._orchestration_context._maximum_short_timer_duration
        self._long_timer_interval = self._orchestration_context._long_timer_interval_duration

    def is_canceled(self) -> bool:
        """Check if the LongTimer is cancelled.

        Returns
        -------
        bool
            Returns whether the timer has been cancelled or not
        """
        return self.action.is_cancelled

    def cancel(self):
        """Cancel a timer.

        Raises
        ------
        ValueError
            Raises an error if the task is already completed and an attempt is made to cancel it
        """
        if (self.result):
            raise Exception("Cannot cancel a completed task.")
        self.action.is_cancelled = True

    def try_set_value(self, child: TimerTask):
        """Transition this LongTimer Task to a terminal state and set its value.

        If the LongTimer has not yet reached the designated completion time, starts a new
        TimerTask for the next interval and does not close.

        Parameters
        ----------
        child : TimerTask
            A timer sub-task that just completed
        """
        current_time = self._orchestration_context.current_utc_datetime
        final_fire_time = self.action.fire_at
        if final_fire_time > current_time:
            next_timer = self.get_next_timer_task(final_fire_time, current_time)
            self.add_new_child(next_timer)
        return super().try_set_value(child)

    def get_next_timer_task(self, final_fire_time: datetime, current_time: datetime) -> TimerTask:
        """Create a TimerTask to represent the next interval of the LongTimer.

        Parameters
        ----------
        final_fire_time : datetime.datetime
            The final firing time of the LongTimer
        current_time : datetime.datetime
            The current time

        Returns
        -------
        TimerTask
            A TimerTask representing the next interval of the LongTimer
        """
        duration_until_fire = final_fire_time - current_time
        if duration_until_fire > self._max_short_timer_duration:
            next_fire_time = current_time + self._long_timer_interval
        else:
            next_fire_time = final_fire_time
        return TimerTask(None, CreateTimerAction(next_fire_time))

    def add_new_child(self, child_timer: TimerTask):
        """Add the TimerTask to this task's children.

        Also register the TimerTask with the orchestration context.

        Parameters
        ----------
        child_timer : TimerTask
            The newly created TimerTask to add
        """
        child_timer.parent = self
        self.pending_tasks.add(child_timer)
        self._orchestration_context._add_to_open_tasks(child_timer)
        self._orchestration_context._add_to_actions(child_timer.action_repr)
        child_timer._set_is_scheduled(True)


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
        compound_action_constructor = None
        if replay_schema.value >= ReplaySchema.V2.value:
            compound_action_constructor = WhenAnyAction
        super().__init__(task, compound_action_constructor)

    def try_set_value(self, child: TaskBase):
        """Transition a WhenAny Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if self.state is TaskState.RUNNING:
            self.set_value(is_error=False, value=child)


class RetryAbleTask(WhenAllTask):
    """A Task representing `with_retry` scenarios.

    It inherits from WhenAllTask because retryable scenarios are Tasks
    with equivalent to WhenAll Tasks with dynamically increasing lists
    of children. At every failure, we add a Timer child and a Task child
    to the list of pending tasks.
    """

    def __init__(self, child: TaskBase, retry_options: RetryOptions, context):
        tasks = [child]
        super().__init__(tasks, context._replay_schema)

        self.retry_options = retry_options
        self.num_attempts = 1
        self.context = context
        self.actions = child.action_repr
        self.is_waiting_on_timer = False
        self.error = None

    @property
    def id_(self):
        """Obtain the task's ID.

        Since this is an internal-only abstraction, the task ID is represented
        by the ID of its inner/wrapped task _plus_ a suffix: "_retryable_proxy"

        Returns
        -------
        [type]
            [description]
        """
        return str(list(map(lambda x: x.id, self.children))) + "_retryable_proxy"

    def try_set_value(self, child: TaskBase):
        """Transition a Retryable Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if self.is_waiting_on_timer:
            # timer fired, re-scheduling original task
            self.is_waiting_on_timer = False
            # As per DTFx semantics: we need to check the number of retires only after the final
            # timer has fired. This means we essentially have to wait for one "extra" timer after
            # the maximum number of attempts has been reached. Removing this extra timer will cause
            # stuck orchestrators as we need to be "in sync" with the replay logic of DTFx.
            if self.num_attempts >= self.retry_options.max_number_of_attempts:
                self.is_waiting_on_timer = True
                # we have reached the maximum number of attempts, set error
                self.set_value(is_error=True, value=self.error)
            else:
                rescheduled_task = self.context._generate_task(
                    action=NoOpAction("rescheduled task"), parent=self)
                self.pending_tasks.add(rescheduled_task)
                self.context._add_to_open_tasks(rescheduled_task)
                self.num_attempts += 1

            return
        if child.state is TaskState.SUCCEEDED:
            if len(self.pending_tasks) == 0:
                # if all pending tasks have completed,
                # and we have a successful child, then
                # we can set the Task's event
                self.set_value(is_error=False, value=child.result)

        else:  # child.state is TaskState.FAILED:
            # increase size of pending tasks by adding a timer task
            # when it completes, we'll retry the original task
            timer_task = self.context._generate_task(
                action=NoOpAction("-WithRetry timer"), parent=self)
            self.pending_tasks.add(timer_task)
            self.context._add_to_open_tasks(timer_task)
            self.is_waiting_on_timer = True
            self.error = child.result
