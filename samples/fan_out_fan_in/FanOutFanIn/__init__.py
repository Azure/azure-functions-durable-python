import json

import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    """This function provides the core fan-out-fan-in orchestration logic

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API

    Returns
    -------
    message
        Returns the result of the "ShowMeTheSum" activity function.

    Yields
    -------
    call_activity: str
        Yields, depending on the `json_rule`, to wait on either all
        tasks to complete, or until one of the tasks completes.
    """

    activity_list = yield context.call_activity("GetActivityCount", 5)

    tasks = [context.call_activity("ParrotValue", i) for i in activity_list]

    values = yield context.task_all(tasks)
    message = yield context.call_activity("ShowMeTheSum", values)

    return message


main = df.Orchestrator.create(orchestrator_function)
