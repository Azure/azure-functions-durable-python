import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    activity_count = yield context.call_activity("GetActivityCount", 5)
    activity_list = json.loads(activity_count)

    tasks = [context.call_activity("ParrotValue", i) for i in activity_list]

    tasks_result = yield context.task_all(tasks)
    values = [int(t) for t in tasks_result]
    message = yield context.call_activity("ShowMeTheSum", values)

    return message


main = df.Orchestrator.create(orchestrator_function)
