from typing import Any
from azure.durable_functions.models.NewTask import NewTask

class MutableTask(NewTask):

    def __init__(self, id_, action):
        super().__init__(id_, [action])

    def process_result(self, result: Any):
        self.set_result(result)
    
    def process_error(self, error: Exception):
        self.set_error(error)