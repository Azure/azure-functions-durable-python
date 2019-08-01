from typing import Callable, List
from ..models import (Task, TaskSet)


class ITaskMethods:
    def __init__(self):
        self.all: Callable[List[Task], TaskSet]
        self.any: Callable[List[Task], TaskSet]
