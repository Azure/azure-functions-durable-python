import logging, json
import azure.durable_functions as df 
import azure.functions as func
from ..Status.inmemorystatusmanager import InMemoryStatusManager
from ..Status.status import Status
from ..Auth import authorization
from ..Auth.knowngroups import SecurityGroups

"""
Update callback that can be customized to make any changes to the status
"""
def update_callback(status: Status):
    return status

"""
Durable HTTP Start that kicks off orchestration for creating subscriptions

Returns:
    Response that contains status URL's to monitor the orchestration
"""
@authorization.authorize([SecurityGroups.subscription_managers])
async def main(req: func.HttpRequest,starter:str) -> func.HttpResponse:

    client = df.DurableOrchestrationClient(starter)

    # Payload that contains how a subscription environment is created
    payload: str = json.loads(req.get_body().decode())
    client_name: str = req.route_params.get('clientName')
    orchestrator_name: str = "SubscriptionLifecycleOrchestrator"

    headers = {}

    if client_name is None:
        return func.HttpResponse(
            "Must include clientName (in the body of the http)",
            headers=headers, status_code=400)
    else:
        # Initialize a new status for this client in-memory
        status_mgr = InMemoryStatusManager(client_name)
        await status_mgr.safe_update_status(update_callback)
        payload["customerName"] = client_name
        payload["subscriptionId"] = None
        instance_id = await client.start_new(orchestration_function_name=orchestrator_name,instance_id=None,client_input=payload)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req,instance_id)