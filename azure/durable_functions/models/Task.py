from datetime import datetime
from ..interfaces import IAction


class Task:
    _action: IAction

    def __init__(self, is_completed, is_faulted, action,
                 result=None, timestamp=None, id_=None, exc=None):
        self._is_completed: bool = is_completed
        self._is_faulted: bool = is_faulted
        self._action: IAction = action
        self._result = result
        self._timestamp: datetime = timestamp
        self._id = id_
        self._exception = exc
