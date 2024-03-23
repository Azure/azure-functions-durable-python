import logging, json
import azure.durable_functions as df 

"""
Demo orchestrator function that can be used to add a subscription to a management group
"""
def orchestrator_fn(context: df.DurableOrchestrationContext):
    output = yield context.call_activity("AddSubscriptionToMgmtGroup")
    return output

main = df.Orchestrator.create(orchestrator_fn)