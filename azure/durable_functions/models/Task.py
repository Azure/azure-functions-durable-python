from datetime import datetime
from ..interfaces import IAction


class Task:
    action: IAction

    def __init__(self, isCompleted, isFaulted, action,
                 result=None, timestamp=None, id=None, exc=None):
        self.isCompleted: bool = isCompleted
        self.isFaulted: bool = isFaulted
        self.action: IAction = action
        self.result = result
        self.timestamp: datetime = timestamp
        self.id = id
        self.exception = exc
