import logging
import azure.functions as func
import json
from azure.durable_functions import DurableOrchestrationClient


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = DurableOrchestrationClient(starter)
    instance_id = req.params.get("instance_id")
    event_name = req.params.get("event_name")
    await client.raise_event(instance_id, event_name, True)

    return func.HttpResponse(f'"{event_name}" event is sent')
