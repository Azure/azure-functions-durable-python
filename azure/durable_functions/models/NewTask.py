from azure.durable_functions.models.Task import Task
import enum
from typing import Any, List, Optional, Set

class TaskState(enum.Enum):
    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2

class NewTask:
    def __init__(self, id_: int, actions: List[Any]):
        self.id: int = id_
        self.state = TaskState.RUNNING
        self.was_yielded: bool = False
        self.parent: CompoundTask = None

        self.result: Any = None
        self.error: Optional[Exception] = None
        self.actions: List[Any] = actions
    
    def change_state(self, state: TaskState):
        if self.state is TaskState.RUNNING:
            if state is TaskState.RUNNING:
                raise Exception("TBD")
            #raise Exception("TBD") TODO: learn why this fails
        self.state = state

    def handle_result(self, result: Any):
        self.process_result(result)
        self.propagate()

    def handle_error(self, error: Exception):
        self.process_error(error)
        self.propagate()

    def set_error(self, error: Exception):
        self.change_state(TaskState.FAILED)
        self.error = error

    def set_result(self, result: Any):
        self.change_state(TaskState.SUCCEEDED)
        self.result = result      

    def propagate(self):
        has_completed = not (self.state is TaskState.RUNNING)
        has_parent = not (self.parent is None)
        if has_completed and has_parent:
            self.parent.handle_completion(self)
    
    def process_result(self, result: Any):
        pass
    
    def process_error(self, error: Exception):
        pass

class CompoundTask(NewTask):
    def __init__(self, tasks: List[Task]):
        super().__init__(-1, [])
        for task in tasks:
            task.parent = self
            self.actions.extend(task.actions)
        self._first_error: Optional[Exception] = None
        self.pending_tasks: Set[NewTask] = set(tasks)
        self.completed_tasks: List[NewTask] = []

    def handle_completion(self, child: Task):
        try:
            self.pending_tasks.remove(child)
        except KeyError:
            raise Exception("TBD")

        self.completed_tasks.append(child)

        if child.state is TaskState.FAILED:
            self.handle_error(child.error)
        else:
            self.handle_result(child)
