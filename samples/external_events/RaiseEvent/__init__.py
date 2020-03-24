import json
import logging

from azure.durable_functions import DurableOrchestrationClient
import azure.functions as func


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Activity function to raise an external event to the orchestrator
    
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
        HTTP response object whose body indicates which event
        was raised
    """

    logging.info("Recevied http request to check startus {}".format(starter))
    client = DurableOrchestrationClient(starter)
    instance_id = req.params.get("instance_id")
    logging.info("Will check on instance id: {}".format(instance_id))
    
    event_name = req.params.get("event_name")
    logging.info("Will check on event: {}".format(event_name))

    await client.raise_event(instance_id, event_name, True)
    return func.HttpResponse(f'"{event_name}" event is sent')
