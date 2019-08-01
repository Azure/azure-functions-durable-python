from datetime import datetime
from ..interfaces import ITaskMethods
from . import (Task, RetryOptions)


class DurableOrchestrationContext:

    def __init__(self,
                 instanceId,
                 isReplaying,
                 parentInstanceId,
                 callActivity,
                 task_all,
                 currentUtcDateTime):
        self.instanceId: str = instanceId
        self.isReplaying: bool = isReplaying
        self.parentInstanceId: str = parentInstanceId
        self.callActivity = callActivity
        self.task_all = task_all
        self.currentUtcDateTime = currentUtcDateTime

        # self.currentUtcDateTime: Date
        self.currentUtcDateTime: datetime
        self.Task: ITaskMethods

        def callActivity(name: str, input=None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        def callActivityWithRetry(
                name: str, retryOptions: RetryOptions, input=None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        def callSubOrchestrator(
                name: str, input=None, instanceId: str = None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        # TODO: more to port over
