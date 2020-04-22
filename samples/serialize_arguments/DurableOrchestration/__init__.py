import logging

import azure.functions as func
import azure.durable_functions as df
from ..shared_code.MyClasses import SerializableClass # TODO: this import is highlight 'red' in VSCode, but works at runtime

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
        The number contained in the input
    """
    input_: SerializableClass = context.get_input()
    number: int = input_.show_number()

    
    # throwaway, seems necessary for the orchestration not to fail
    value = yield context.call_activity("DurableActivity", SerializableClass(24))
    return 11

main = df.Orchestrator.create(orchestrator_function)
