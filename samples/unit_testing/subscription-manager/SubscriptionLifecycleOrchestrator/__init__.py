import azure.durable_functions as df 

"""
Durable Orchestration function that calls a set of sub orchestrators through
- function chaining
- fan in/fan out patterns

context: DurableOrchestrationContext
Returns: Id of the subscription that is created
"""
def orchestrator_fn(context: df.DurableOrchestrationContext):

    payload_: str = context.get_input()

    subscription_id = yield context.call_sub_orchestrator("CreateSubscriptionSubOrchestrator", payload_)
    payload_["subscriptionId"] = subscription_id

    provisioning_tasks_ = []
    provisioning_tasks_.append(context.call_sub_orchestrator("RegisterPIMSubOrchestrator",payload_))
    provisioning_tasks_.append(context.call_sub_orchestrator("MgmtGroupSubOrchestrator",payload_))

    yield context.task_all(provisioning_tasks_)
    return subscription_id

main = df.Orchestrator.create(orchestrator_fn)