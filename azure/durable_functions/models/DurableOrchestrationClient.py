import json
import re
import requests
import validators
from typing import List
from urllib.parse import urlparse
from azure.durable_functions.models import DurableOrchestrationBindings

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
        if result.status_code <= 202 and result.text:
            response_text = json.loads(result.text)
            return response_text["id"]
        else:
            return None

    def createCheckStatusResponse(self, request, instanceId):
        """ Create a dictionary object that is used to create HttpResponse and 
        contains useful information for checking the status of the specified instance.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request that triggered the current orchestration instance.
        instanceId : str
            The ID of the orchestration instance to check.

        Returns
        -------
        dict
           An HTTP 202 response with a Location header and a payload containing instance management URLs
        """
        httpManagementPayload = self.getClientResponseLinks(request, instanceId)
        return {
            "status_code": 202,
            "body": json.dumps(httpManagementPayload),
            "headers": {
                "Content-Type": "application/json",
                "Location": httpManagementPayload["statusQueryGetUri"],
                "Retry-After": "10",
            },
        }

    def getClientResponseLinks(self, request, instanceId):
        """Create a dictionary of orchestrator management urls.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request that triggered the current orchestration instance.
        instanceId : str
            The ID of the orchestration instance to check.

        Returns
        -------
        dict
            a dictionary object of orchestrator instance management urls
        """
        payload = self._orchestration_bindings.management_urls.copy()
        for key, _ in payload.items():
            if request.url and validators.url(payload[key]):
                request_parsed_url = urlparse(request.url)
                value_parsed_url = urlparse(payload[key])
                request_url_origin = '{url.scheme}://{url.netloc}/'.format(url=request_parsed_url)
                value_url_origin = '{url.scheme}://{url.netloc}/'.format(url=value_parsed_url)
                payload[key] = payload[key].replace(value_url_origin, request_url_origin)
            payload[key] = payload[key].replace(
                self._orchestration_bindings.management_urls["id"], instanceId)

        return payload


    def raise_event(self, instance_id, event_name, event_data=None, task_hub_name=None, connection_name=None):
        """Sends an event notification message to a waiting orchestration instance.
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
        if (not event_name):
            raise ValueError("event_name must be a valid string.")
        
        id_placeholder = self._orchestration_bindings.management_urls["id"]
        request_url = self._orchestration_bindings.management_urls["sendEventPostUri"].replace(id_placeholder, instance_id)
        request_url = request_url.replace(self._event_name_placeholder, event_name)
        if task_hub_name:
            request_url = request_url.replace(self.task_hub_name, task_hub_name)
        
        if connection_name:
            p=re.compile(r'(?P<connection>connection=)(?P<connectionString>[\w]+)', re.IGNORECASE)
            p.sub(r'\g<connection>'+connection_name, request_url)
    
        response = requests.post(request_url, json=json.dumps(event_data))

        switch_statement = {
            202: lambda: None,
            410: lambda: None,
            404: lambda : f"No instance with ID {instance_id} found.",
            400: lambda : "Only application/json request content is supported"
        }
        func = switch_statement.get(response.status_code, lambda: f"Webhook returned unrecognized status code {response.status_code}")
        error_message = func()
        if error_message:
            raise Exception(error_message)

    @staticmethod
    def _get_json_input(client_input: object) -> object:
        return json.dumps(client_input) if client_input is not None else None

    def _get_start_new_url(self, instance_id, orchestration_function_name):
        request_url = self._orchestration_bindings.creation_urls['createNewInstancePostUri']
        request_url = request_url.replace(self._function_name_placeholder,
                                          orchestration_function_name)
        request_url = request_url.replace(self._instance_id_placeholder,
                                          f'/{instance_id}'
                                          if instance_id is not None else '')
        return request_url
