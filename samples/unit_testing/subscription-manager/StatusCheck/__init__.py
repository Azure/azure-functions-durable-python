from ..Subscription.subscriptionmanager import SubscriptionManager
from ..Status.status import Status
from ..Status.inmemorystatusmanager import InMemoryStatusManager
from ..Subscription.subscription import SubscriptionResponse
import os

subscription_resource : SubscriptionResponse = None

"""
Update callback that can be used to set the provisioning state in the subscription status
"""
def update_callback(status: Status):
    status.creation_status = subscription_resource.properties.provisioningState
    return status

"""
Activity Function that performs a status check of the subscription creation process
by invoking the required Azure API's via Python ms-rest.
It also updates the status of the subscription before returning a SubscriptionResponse.

SubscriptionResponse : contains details of the subscription whose status is being checked
"""
async def main(payload: dict) -> str:

    sm = SubscriptionManager()
    
    client_name = payload["customerName"]
    subscription_name = payload["subscriptionName"]

    # Query for subscription status
    global subscription_resource 
    subscription_resource = await sm.get_subscription_status(subscription_name)
    status_mgr = InMemoryStatusManager(client_name)

    # Update status
    await status_mgr.safe_update_status(update_callback)
    return subscription_resource