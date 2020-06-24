import logging

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """This function provides the core function chaining orchestration logic
    and also sets custom status using which a user can see intermittent status of
    the orchestration through get_status client URL.

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history
        and the durable orchestration API's to chain a set of functions

    Returns
    -------
    final_result: str
        Returns the final result after the chain completes

    Yields
    -------
    call_activity: str
        Yields at every step of the function chain orchestration logic
    """

    # Chained functions - output of a function is passed as
    # input to the next function in the chain
    r1 = yield context.call_activity("DurableActivity", "Zero")
    context.set_custom_status(f'{r1} ->')
    r2 = yield context.call_activity("DurableActivity", r1)
    context.set_custom_status(f'{r1} -> {r2} ->')
    r3 = yield context.call_activity("DurableActivity", r2)
    context.set_custom_status(f'{r1} -> {r2} -> {r3}')
    return r3

main = df.Orchestrator.create(orchestrator_function)
