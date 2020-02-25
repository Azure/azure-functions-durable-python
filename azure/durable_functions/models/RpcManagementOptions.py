from datetime import datetime
from furl import furl
from typing import Any, List

from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from azure.durable_functions.models.OrchestrationRuntimeStatus import OrchestrationRuntimeStatus


class RpcManagementOptions:
    """Class used to collect the options for getting orchestration status."""

    def __init__(self, instance_id: str = None, task_hub_name: str = None,
                 connection_name: str = None, show_history: bool = None,
                 show_history_output: bool = None, created_time_from: datetime = None,
                 created_time_to: datetime = None,
                 runtime_status: List[OrchestrationRuntimeStatus] = None, show_input: bool = None):
        self._instance_id = instance_id
        self._task_hub_name = task_hub_name
        self._connection_name = connection_name
        self._show_history = show_history
        self._show_history_output = show_history_output
        self._created_time_from = created_time_from
        self._created_time_to = created_time_to
        self._runtime_status = runtime_status
        self._show_input = show_input

    @staticmethod
    def _add_arg(url: furl, name: str, value: Any):
        if value:
            url.args[name] = value

    @staticmethod
    def _add_date_arg(url: furl, name: str, value: datetime):
        if value:
            date_as_string = value.strftime(DATETIME_STRING_FORMAT)
            RpcManagementOptions._add_arg(url, name, date_as_string)

    def to_url(self, base_url: str) -> str:
        """Get the url based on the options selected.

        Parameters
        ----------
        base_url: str
            The base url to prepend to the url path

        Returns
        -------
        str
            The Url used to get orchestration status information
        """
        url = furl(f"{base_url}instances/{self._instance_id if self._instance_id else ''}")

        self._add_arg(url, 'taskHub', self._task_hub_name)
        self._add_arg(url, 'connectionName', self._connection_name)
        self._add_arg(url, 'showInput', self._show_input)
        self._add_arg(url, 'showHistory', self._show_history)
        self._add_arg(url, 'showHistoryOutput', self._show_history_output)
        self._add_date_arg(url, 'createdTimeFrom', self._created_time_from)
        self._add_date_arg(url, 'createdTimeTo', self._created_time_to)
        if self._runtime_status is not None and len(self._runtime_status) > 0:
            runtime_status = ",".join(r.value for r in self._runtime_status)
            self._add_arg(url, 'runtimeStatus', runtime_status)

        return url.url
