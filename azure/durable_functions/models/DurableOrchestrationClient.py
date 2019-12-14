import requests
import json
from typing import List

from azure.durable_functions.models import DurableOrchestrationBindings


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
        self._orchestrationBindings: DurableOrchestrationBindings

    def start_new(self, context,
                  orchestration_function_name: str,
                  instance_id: str,
                  client_input):

        self._orchestrationBindings = DurableOrchestrationBindings(context)

        request_url = self._orchestrationBindings.creation_urls['createNewInstancePostUri']
        request_url = request_url.replace(self._functionNamePlaceholder, orchestration_function_name)

        request_url = request_url.replace(self._instanceIdPlaceholder,
                                          f'/{instance_id}' if instance_id is not None else '')
        result = requests.post(request_url, json=json.dumps(client_input) if client_input is not None else None)
        return result
