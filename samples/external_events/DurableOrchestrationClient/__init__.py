import logging
import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient


async def main(req: func.HttpRequest, starter: str):
    function_name = req.route_params.get('functionName')
    client = DurableOrchestrationClient(starter)
    instance_id = await client.start_new(function_name, None, None)

    response_args = client.create_check_status_response(req, instance_id)
    return func.HttpResponse(**response_args)
