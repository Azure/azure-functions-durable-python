import azure.durable_functions as df 
from datetime import datetime,timedelta
from ..Subscription.subscription import SubscriptionResponse

def get_expiry_time(context: df.DurableOrchestrationContext):
    return context.current_utc_datetime + timedelta(minutes=2)

"""
Orchestrator function that checks the status of subscription 
creation until it gets successfully created or errors out.

context: DurableOrchestrationContext
Returns: Id of the subscription that got created
"""
def orchestrator_fn(context: df.DurableOrchestrationContext):

    payload_ = context.get_input()
    customer_name = payload_["customerName"]
    payload_["subscriptionName"] = f"{customer_name}"

    # Check upto 1 hour
    expiry_time = get_expiry_time(context)
    
    subscription_details : SubscriptionResponse = None

    while context.current_utc_datetime < expiry_time:
        subscription_details = yield context.call_activity("StatusCheck",payload_)

        # If subscription is not found call the activity function to create it
        if subscription_details.properties.provisioningState == "NotFound":
            yield context.call_activity("CreateSubscription",payload_)
        elif subscription_details.properties.provisioningState == "Succeeded":
            break

        # If neither it means the subscription creation request is accepted, wait for 60 seconds 
        # and poll again
        next_checkpoint = context.current_utc_datetime + timedelta(seconds=60)
        yield context.create_timer(next_checkpoint)

    if subscription_details.properties.provisioningState != "Succeeded":
        raise Exception("Subscription creation ended without being successful")
    return subscription_details.properties.subscriptionId

main = df.Orchestrator.create(orchestrator_fn)