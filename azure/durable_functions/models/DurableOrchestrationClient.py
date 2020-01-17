"""Durable Orchestration Client class definition."""
import requests
import json
from typing import List

from azure.durable_functions.models import DurableOrchestrationBindings


class DurableOrchestrationClient:
    """Durable Orchestration Client.

    Client for starting, querying, terminating and raising events to
    orchestration instances.
    """

    def __init__(self, context: str):
        """Create a new Orchestration Client.

        :param context: The object representing the orchestrationClient input
        binding of the Azure function that will use this client.
        """
        self.task_hub_name: str
        self._uniqueWebHookOrigins: List[str]
        self._event_name_placeholder: str = "{eventName}"
        self._function_name_placeholder: str = "{functionName}"
        self._instance_id_placeholder: str = "[/{instanceId}]"
        self._reason_placeholder: str = "{text}"
        self._created_time_from_query_key: str = "createdTimeFrom"
        self._created_time_to_query_key: str = "createdTimeTo"
        self._runtime_status_query_key: str = "runtimeStatus"
        self._show_history_query_key: str = "showHistory"
        self._show_history_output_query_key: str = "showHistoryOutput"
        self._show_input_query_key: str = "showInput"
        self._orchestration_bindings: DurableOrchestrationBindings = \
            DurableOrchestrationBindings(context)

    def start_new(self,
                  orchestration_function_name: str,
                  instance_id: str,
                  client_input):
        """Start a new instance of the specified orchestrator function.

        If an orchestration instance with the specified ID already exists, the
        existing instance will be silently replaced by this new instance.

        :param orchestration_function_name: The name of the orchestrator
        function to start.
        :param instance_id: The ID to use for the new orchestration instance.
        If no instanceId is specified, the Durable Functions extension will
        generate a random GUID (recommended).
        :param client_input: JSON-serializable input value for the orchestrator
        function.
        :return: The ID of the new orchestration instance.
        """
        request_url = self._get_start_new_url(
            instance_id,
            orchestration_function_name)

        result = requests.post(request_url, json=self._get_json_input(
            client_input))
        return result

    @staticmethod
    def _get_json_input(client_input):
        return json.dumps(client_input) if client_input is not None else None

    def _get_start_new_url(self, instance_id, orchestration_function_name):
        request_url = self._orchestration_bindings.creation_urls[
                'createNewInstancePostUri'
        ]
        request_url = request_url.replace(self._function_name_placeholder,
                                          orchestration_function_name)
        request_url = request_url.replace(self._instance_id_placeholder,
                                          f'/{instance_id}'
                                          if instance_id is not None else '')
        return request_url
