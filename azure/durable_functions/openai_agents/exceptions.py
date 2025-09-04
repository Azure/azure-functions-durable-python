from azure.durable_functions.models.Task import TaskBase


class YieldException(BaseException):
    """Exception raised when an orchestrator should yield control."""

    def __init__(self, task: TaskBase):
        super().__init__("Orchestrator should yield.")
        self.task = task
