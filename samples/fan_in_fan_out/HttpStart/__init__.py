import logging
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    payload: str = json.loads(req.get_body().decode()) # Load JSON post request data
    instance_id = await client.start_new(req.route_params["functionName"], client_input=payload)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)