import json
import aiohttp
from typing import List
from urllib.parse import urlparse
from ..models import DurableOrchestrationBindings
from .DurableOrchestrationStatus import DurableOrchestrationStatus
import azure.functions as func


class DurableOrchestrationClient:
    """Durable Orchestration Client.

    Client for starting, querying, terminating and raising events to
    orchestration instances.
    """

    def __init__(self, context: str):
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
            DurableOrchestrationBindings.from_json(context)

    async def start_new(self,
                        orchestration_function_name: str,
                        instance_id: str,
                        client_input: object):
        """Start a new instance of the specified orchestrator function.

        If an orchestration instance with the specified ID already exists, the
        existing instance will be silently replaced by this new instance.

        Parameters
        ----------
        orchestration_function_name : str
            The name of the orchestrator function to start.
        instance_id : str
            The ID to use for the new orchestration instance. If no instance id is specified,
            the Durable Functions extension will generate a random GUID (recommended).
        client_input : object
            JSON-serializable input value for the orchestrator function.

        Returns
        -------
        str
            The ID of the new orchestration instance if successful, None if not.
        """
        request_url = self._get_start_new_url(
            instance_id=instance_id, orchestration_function_name=orchestration_function_name)

        async with aiohttp.ClientSession() as session:
            async with session.post(request_url,
                                    json=self._get_json_input(client_input)) as response:
                data = await response.json()
                if response.status <= 202 and data:
                    return data["id"]
                else:
                    return None

    def create_check_status_response(self, request, instance_id):
        """Create a HttpResponse that contains useful information for \
        checking the status of the specified instance.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request that triggered the current orchestration instance.
        instance_id : str
            The ID of the orchestration instance to check.

        Returns
        -------
        HttpResponse
           An HTTP 202 response with a Location header
           and a payload containing instance management URLs
        """
        http_management_payload = self.get_client_response_links(request, instance_id)
        response_args = {
            "status_code": 202,
            "body": json.dumps(http_management_payload),
            "headers": {
                "Content-Type": "application/json",
                "Location": http_management_payload["statusQueryGetUri"],
                "Retry-After": "10",
            },
        }
        return func.HttpResponse(**response_args)

    def get_client_response_links(self, request, instance_id):
        """Create a dictionary of orchestrator management urls.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request that triggered the current orchestration instance.
        instance_id : str
            The ID of the orchestration instance to check.

        Returns
        -------
        dict
            a dictionary object of orchestrator instance management urls
        """
        payload = self._orchestration_bindings.management_urls.copy()

        for key, _ in payload.items():
            if request.url:
                payload[key] = self._replace_url_origin(request.url, payload[key])
            payload[key] = payload[key].replace(
                self._orchestration_bindings.management_urls["id"], instance_id)

        return payload

    async def raise_event(self, instance_id, event_name, event_data=None,
                          task_hub_name=None, connection_name=None):
        """Send an event notification message to a waiting orchestration instance.

        In order to handle the event, the target orchestration instance must be
        waiting for an event named `eventName` using waitForExternalEvent API.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance that will handle the event.
        event_name : str
            The name of the event.
        event_data : any, optional
            The JSON-serializable data associated with the event.
        task_hub_name : str, optional
            The TaskHubName of the orchestration that will handle the event.
        connection_name : str, optional
            The name of the connection string associated with `taskHubName.`

        Raises
        ------
        ValueError
            event name must be a valid string.
        Exception
            Raises an exception if the status code is 404 or 400 when raising the event.
        """
        if not event_name:
            raise ValueError("event_name must be a valid string.")

        request_url = self._get_raise_event_url(
            instance_id, event_name, task_hub_name, connection_name)

        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, json=json.dumps(event_data)) as response:
                switch_statement = {
                    202: lambda: None,
                    410: lambda: None,
                    404: lambda: f"No instance with ID {instance_id} found.",
                    400: lambda: "Only application/json request content is supported"
                }
                has_error_message = switch_statement.get(
                    response.status, lambda: "Webhook returned unrecognized status code"
                                             + f" {response.status}")
                error_message = has_error_message()
                if error_message:
                    raise Exception(error_message)

    def get_status(self, instance_id: str, show_history: bool = None,
                   show_history_output: bool = None,
                   show_input: bool = None) -> DurableOrchestrationStatus:
        """Get the status of the specified orchestration instance.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance to query.
        show_history: bool
            Boolean marker for including execution history in the response.
        show_history_output: bool
            Boolean marker for including output in the execution history response.
        show_input: bool
            Boolean marker for including the input in the response.

        Returns
        -------
        DurableOrchestrationStatus
            The status of the requested orchestration instance
        """
        raise NotImplementedError("This is a placeholder.")

    @staticmethod
    def _get_json_input(client_input: object) -> object:
        return json.dumps(client_input) if client_input is not None else None

    @staticmethod
    def _replace_url_origin(request_url, value_url):
        request_parsed_url = urlparse(request_url)
        value_parsed_url = urlparse(value_url)
        request_url_origin = '{url.scheme}://{url.netloc}/'.format(url=request_parsed_url)
        value_url_origin = '{url.scheme}://{url.netloc}/'.format(url=value_parsed_url)
        value_url = value_url.replace(value_url_origin, request_url_origin)
        return value_url

    def _get_start_new_url(self, instance_id, orchestration_function_name):
        instance_path = f'/{instance_id}' if instance_id is not None else ''
        request_url = f'{self._orchestration_bindings.rpc_base_url}orchestrators/' \
                      f'{orchestration_function_name}{instance_path}'
        return request_url

    def _get_raise_event_url(self, instance_id, event_name, task_hub_name, connection_name):
        request_url = f'{self._orchestration_bindings.rpc_base_url}' \
                      f'instances/{instance_id}/raiseEvent/{event_name}'

        query = []
        if task_hub_name:
            query.append(f'taskHub={task_hub_name}')

        if connection_name:
            query.append(f'connection={connection_name}')

        if len(query) > 0:
            request_url += "?" + "&".join(query)

        return request_url
