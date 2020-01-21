import requests
import json
from typing import List

from azure.durable_functions.models import DurableOrchestrationBindings


class DurableOrchestrationClient:

    def __init__(self, context: str):
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
        self._orchestrationBindings: DurableOrchestrationBindings = \
            DurableOrchestrationBindings(context)

    def start_new(self,
                  orchestration_function_name: str,
                  instance_id: str,
                  client_input):
        request_url = self.get_start_new_url(instance_id, orchestration_function_name)

        result = requests.post(request_url, json=self.get_json_input(client_input))
        return result

    @staticmethod
    def get_json_input(client_input):
        return json.dumps(client_input) if client_input is not None else None

    def get_start_new_url(self, instance_id, orchestration_function_name):
        request_url = self._orchestrationBindings.creation_urls['createNewInstancePostUri']
        request_url = request_url.replace(self._functionNamePlaceholder,
                                          orchestration_function_name)
        request_url = request_url.replace(self._instanceIdPlaceholder,
                                          f'/{instance_id}' if instance_id is not None else '')
        return request_url
