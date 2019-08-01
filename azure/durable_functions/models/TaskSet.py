from typing import List
from ..interfaces import IAction


class TaskSet:
    def __init__(self, isCompleted, actions, result, isFaulted=False, e=None):
        self.isCompleted: bool = isCompleted
        self.actions: List[IAction] = actions
        self.result = result
        self.isFaulted: bool = isFaulted
        self.exception = e
