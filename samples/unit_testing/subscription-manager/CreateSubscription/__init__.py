from ..Subscription.subscriptionmanager import SubscriptionManager
from ..Status.status import Status
from ..Status.inmemorystatusmanager import InMemoryStatusManager
from ..Subscription.subscription import SubscriptionResponse

subscription_resource : SubscriptionResponse = None

"""
Update callback that can be used to update the name, id and provisioning state of a subscription 
on the status object
"""
def update_callback(status: Status):
    status.name = subscription_resource.name
    status.id = subscription_resource.id
    status.creation_status = subscription_resource.properties.provisioningState
    return status

"""
Activity function that invokes the Azure Python ms-rest API's to create a subscription and updates
the status of subscription creation.

SubscriptionResponse: contains details of the subscription whose status is being created
"""
async def main(payload: dict) -> str:
    display_name = payload['subscriptionName']
    sm = SubscriptionManager()

    global subscription_resource 
    subscription_resource = await sm.create_subscription(payload['subscriptionName'],display_name)
    status_mgr = InMemoryStatusManager(payload['customerName'])
    await status_mgr.safe_update_status(update_callback)
    return subscription_resource

