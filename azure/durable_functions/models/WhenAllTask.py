from typing import Any
from azure.durable_functions.models.NewTask import CompoundTask


class WhenAllTask(CompoundTask):

    def process_result(self, _):
        if len(self.pending_tasks) == 0:
            results = list(map(lambda x: x.result, self.completed_tasks))
            self.set_result(results)

    def process_error(self, error: Exception):
        if self._first_error is None:
            self._first_error = error

        if len(self.pending_tasks) == 0:
            self.set_error(self._first_error)
