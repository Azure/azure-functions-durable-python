import logging

from azure.durable_functions import DurableOrchestrationClient
import azure.functions as func


async def main(req: func.HttpRequest, starter: str):
    function_name = req.route_params.get('functionName')
    client = DurableOrchestrationClient(starter)
    instance_id = await client.start_new(function_name, None, None)

    return client.create_check_status_response(req, instance_id)
