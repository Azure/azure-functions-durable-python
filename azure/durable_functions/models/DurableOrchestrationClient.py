from typing import List


class DurableOrchestrationClient:

    def __init__(self):
        self.taskHubName: str

        self.uniqueWebhookOrigins: List[str]

        # self._axiosInstance: AxiosInstance = None (http client)

        self._eventNamePlaceholder: str = "{eventName}"
        self._functionNamePlaceholder: str = "{functionName}"
        self._instanceIdPlaceholder: str = "[/{instanceId}]"
        self._reasonPlaceholder: str = "{text}"

        self._createdTimeFromQueryKey: str = "createdTimeFrom"
        self._createdTimeToQueryKey: str = "createdTimeTo"
        self._runtimeStatusQueryKey: str = "runtimeStatus"
        self._showHistoryQueryKey: str = "showHistory"
        self._showHistoryOutputQueryKey: str = "showHistoryOutput"
        self._showInputQueryKey: str = "showInput"
