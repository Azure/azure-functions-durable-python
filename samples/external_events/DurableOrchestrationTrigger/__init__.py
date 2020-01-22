import logging
import azure.durable_functions as df


def generator_function(context):
    """This function provides the waitForExternalEvent orchestration logic
        
    Arguments:
        context {DurableOrchestrationContext} -- This context has the past history 
        and the durable orchestration API's
    
    Returns:
        {str} -- Returns whether "approved" or "denied"
    
    Yields:
        wait_for_external_event {str} -- Yields at every step of the WaitForExternalEvent logic
    """
    approved = yield context.df.wait_for_external_event("A")

    if approved:
        return "approved"
    else:
        return "denied"


def main(context: str):
    """This function creates the orchestration and provides
    the durable framework with the core orchestration logic
    
    Arguments:
        context {str} -- Function context containing the orchestration API's 
        and current context of the long running workflow.
    
    Returns:
        OrchestratorState - State of current orchestration
    """
    orchestrate = df.Orchestrator.create(generator_function)
    result = orchestrate(context)
    return result
