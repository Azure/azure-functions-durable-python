import logging, json
import azure.durable_functions as df 

"""
Demo sub-orchestrator function that can be used to call the register PIM activity function
"""
def orchestrator_fn(context: df.DurableOrchestrationContext):
    
    payload_ = context.get_input()
    output = yield context.call_activity("RegisterPIM",payload_)
    return output

main = df.Orchestrator.create(orchestrator_fn)