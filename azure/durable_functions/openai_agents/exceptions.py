#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from azure.durable_functions.models.Task import TaskBase


class YieldException(BaseException):
    """Exception raised when an orchestrator should yield control."""

    def __init__(self, task: TaskBase):
        super().__init__("Orchestrator should yield.")
        self.task = task
