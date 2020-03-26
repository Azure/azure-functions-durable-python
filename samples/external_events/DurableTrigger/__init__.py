import logging

from azure.durable_functions import DurableOrchestrationClient
import azure.functions as func


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """This function starts up the orchestrator from an HTTP endpoint

    Parameters
    ----------
    req: func.HttpRequest
        An HTTP Request object, it can be used to parse URL
        parameters.

    starter: str
        A JSON-formatted string describing the orchestration context

    Returns
    -------
    func.HttpResponse
        An HTTP response containing useful URLs for monitoring the
        status of newly generated orchestration instance
    """

    logging.debug("Recevied http request call with value {}".format(starter))
    function_name = req.route_params.get('functionName')
    client = DurableOrchestrationClient(starter)

    logging.debug("About to call function {} asyncrounously".format(function_name))
    instance_id = await client.start_new(function_name)

    return client.create_check_status_response(req, instance_id)
