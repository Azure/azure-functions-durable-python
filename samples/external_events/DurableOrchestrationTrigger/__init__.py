import json
import logging
from typing import List
import azure.durable_functions as df
import azure.functions as func


def orchestrator_function(context: df.DurableOrchestrationContext) -> List[str]:

    """This function provides the core function chaining orchestration logic

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API

    Returns
    -------
    output: List[str]
        Returns an array of result by the activity functions.

    Yields
    -------
    call_activity: str
        Yields, depending on the `json_rule`, to wait on either all
        tasks to complete, or until one of the tasks completes.
    """

    json_rule = {
        "condition": {
            "wait_events": ["A","B"],
            "logic": "and"
        },
        "satisfied":[
            {
                "activity_func_name": "SuccessActions",
                "args": {
                    "name": "Tokyo"
                }
            }
        ]
    }

    tasks = []
    for event in json_rule["condition"]["wait_events"]:
        tasks.append(context.wait_for_external_event(event))

    if json_rule["condition"]["logic"] == 'and':
        yield context.task_all(tasks)
    elif json_rule["condition"]["logic"] == 'or':
        yield context.task_any(tasks)

    output = []
    for action in json_rule["satisfied"]:
        result = yield context.call_activity(action["activity_func_name"], json.dumps(action["args"]))
        output.append(result)

    return output


main = df.Orchestrator.create(orchestrator_function)
