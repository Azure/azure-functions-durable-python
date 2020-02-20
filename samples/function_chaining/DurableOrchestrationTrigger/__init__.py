import logging
import azure.durable_functions as df

def generator_function(context):
    """This function provides the core function chaining orchestration logic
    
    Parameters
    ----------
    context : DurableOrchestrationContext
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
    r1 = yield context.call_activity("DurableActivity", "One")
    r2 = yield context.call_activity("DurableActivity", r1)
    final_result = yield context.call_activity("DurableActivity", r2)

    return final_result

def main(context:str):
    """This function creates the orchestration and provides
    the durable framework with the core orchestration logic
    
    Parameters
    ----------
    context : str
        Function context containing the orchestration API's 
        and current context of the long running workflow.
    
    Returns:
        OrchestratorState - State of currently running orchestration
    """
    orchestrate = df.Orchestrator.create(generator_function)
    result = orchestrate(context)
    return result