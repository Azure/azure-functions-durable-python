import logging

from azure.durable_functions import DurableOrchestrationClient
import azure.functions as func


async def main(req: func.HttpRequest, starter: str):

    logging.debug("Recevied http request call with value {}".format(starter))
    function_name = req.route_params.get('functionName')
    client = DurableOrchestrationClient(starter)

    logging.debug("About to call function {} asyncrounously".format(function_name))
    instance_id = await client.start_new(function_name, None, None)

    return client.create_check_status_response(req, instance_id)
