from typing import Any
from azure.durable_functions.models.NewTask import TaskBase

class AtomicTask(TaskBase):
    """A Task with no subtasks.
    """

    def __init__(self, id_, action):
        super().__init__(id_, [action])