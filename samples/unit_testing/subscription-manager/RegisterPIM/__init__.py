from ..Status.status import Status
from ..Status.inmemorystatusmanager import InMemoryStatusManager
from ..Subscription.subscription import SubscriptionResponse

subscription_resource : SubscriptionResponse = None

"""
Update callback that can be used to indicate that the privileged identity management is now enabled 
for the subscription
"""
def update_callback(status: Status):

    # set privileged identity as true
    status.pim_enabled = True
    return status

"""
Demo Activity Function that can be used to manage the privileged identity of the subscription
"""
async def main(payload: dict) -> str:

    client_name = payload["customerName"]

    # Register PIM
    global subscription_resource 
    status_mgr = InMemoryStatusManager(client_name)
    await status_mgr.safe_update_status(update_callback)
    return "Elevated PIM"