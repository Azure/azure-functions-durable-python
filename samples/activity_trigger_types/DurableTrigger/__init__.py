import logging

from azure.durable_functions import DurableOrchestrationClient
import azure.functions as func


async def main(req: func.HttpRequest, starter: str, message):
    """This function starts up the orchestrator from an HTTP endpoint

    Parameters
    ----------
    req: func.HttpRequest
        An HTTP Request object, it can be used to parse URL
        parameters.

    starter: str
        A JSON-formatted string describing the orchestration context

    message:
        An azure functions http output binding, it enables us to establish
        an http response.
    """

    function_name = req.route_params.get('functionName')
    logging.info(starter)
    client = DurableOrchestrationClient(starter)
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    message.set(response)