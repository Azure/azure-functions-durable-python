import json
import logging
from typing import Any, Dict, Union, cast

import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient
from azure.durable_functions.models.utils.entity_utils import EntityId


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = DurableOrchestrationClient(starter)
    entity_name, entity_key = req.route_params["entityName"], req.route_params["entityKey"]
    
    entity_identifier = EntityId(entity_name, entity_key)

    entity_state_response = await client.read_entity_state(entity_identifier)

    if not entity_state_response.entity_exists:
        return func.HttpResponse("Entity not found", status_code=404)

    return func.HttpResponse(json.dumps({
        "entity": entity_name,
        "key": entity_key,
        "state": entity_state_response.entity_state
    }))
    