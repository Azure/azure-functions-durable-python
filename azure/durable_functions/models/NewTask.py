from azure.durable_functions.models.ReplaySchema import ReplaySchema
from build.lib.azure.durable_functions.models.actions.Action import Action
from azure.durable_functions.models.Task import Task
import enum
from typing import Any, List, Optional, Set, Union

class TaskState(enum.Enum):
    """The possible states that a Task can be in.
    """
    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2

class TaskBase:
    """The base class of all Tasks. Contains shared logic
    that drives all of its sub-classes. Should never be
    instantiated on its own.
    """

    def __init__(self, id_: int, actions: List[Action]):
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
        self.parent: CompoundTask = None

        self.value: Any = None
        self.action_repr: Union[List[Action], Action] = actions
        self.is_played = False

    def set_is_played(self, is_played: bool):
        """Set the is_played flag for the Task, needed for updating
        the orchestrator's is_replaying flag.

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
        """Notify parent Task of this Task's state change.
        """
        has_completed = not (self.state is TaskState.RUNNING)
        has_parent = not (self.parent is None)
        if has_completed and has_parent:
            self.parent.handle_completion(self)
    
class CompoundTask(TaskBase):
    """A Task of Tasks. Contains shared logic
    that drives all of its sub-classes. Should never be
    instantiated on its own.
    """

    def __init__(self, tasks: List[Task], action_wrapper=None):
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
        else: # replay_schema is ReplaySchema.V2
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
            raise Exception(f"Parent Task {self.id} does not have sub-task {self.child.id} in its pending list."\
                f"This most likely means that Task {self.child.id} completed twice.")

        self.completed_tasks.append(child)
        self.try_set_value(child)
    
    def try_set_value(self, child: TaskBase):
        """Tries to transition a CompoundTask to a terminal state and set its value.

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