from azure.durable_functions.models.Task import TaskBase

class YieldException(BaseException):
    def __init__(self, task: TaskBase):
        super().__init__("Orchestrator should yield.")
        self.task = task