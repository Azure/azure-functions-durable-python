import logging
import azure.functions as func

from azure.durable_functions import DurableOrchestrationClient


def main(req: func.HttpRequest, starter: str, message):
    function_name = req.route_params.get('functionName')
    logging.warning(f"!!!functionName: ${function_name}")
    client = DurableOrchestrationClient(starter)
    client.start_new(function_name, None, None)
    message.set(func.HttpResponse(status_code=200, body=starter))
