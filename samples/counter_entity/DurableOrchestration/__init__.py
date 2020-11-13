# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """This function provides the a simple implementation of an orchestrator
    that signals and then calls a counter Durable Entity.

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API

    Returns
    -------
    state
        The state after applying the operation on the Durable Entity
    """
    entityId = df.EntityId("Counter", "myCounter")
    context.signal_entity(entityId, "add", 3)
    state = yield context.call_entity(entityId, "get")
    return state

main = df.Orchestrator.create(orchestrator_function)