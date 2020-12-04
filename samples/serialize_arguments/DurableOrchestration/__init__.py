import logging

import azure.functions as func
import azure.durable_functions as df
from ..shared_code.MyClasses import SerializableClass

def orchestrator_function(context: df.DurableOrchestrationContext):
    """This function provides the core function chaining orchestration logic

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API's to
        create orchestrations

    Returns
    -------
    int
        The number contained in the SerializableClass input object
    """
    input_: SerializableClass = context.get_input()
    num1: int = input_.show_number()

    # The custom class is also correctly serialized when calling an activity
    num2 = yield context.call_activity("DurableActivity", SerializableClass(5))
    return num1

main = df.Orchestrator.create(orchestrator_function)
