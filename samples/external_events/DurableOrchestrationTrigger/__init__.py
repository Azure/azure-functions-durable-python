import json
import logging

import azure.durable_functions as df
import azure.functions as func


def orchestrator_function(context: df.DurableOrchestrationContext):

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
