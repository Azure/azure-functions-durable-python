from typing import Any
from azure.durable_functions.models.NewTask import CompoundTask


class WhenAnyTask(CompoundTask):

    def process_result(self, result: Any):
        self.set_result(result)

    def process_error(self, error: Exception):
        if self._first_error is None:
            self._first_error = error

        if len(self.pending_tasks) == 0:
            self.set_error(self._first_error)
