import json
import azure.durable_functions as df


def generator_function(context):
    activity_count = yield context.call_activity("GetActivityCount", 5)
    activity_list = json.loads(activity_count)

    tasks = [context.call_activity("ParrotValue", i) for i in activity_list]

    tasks_result = yield context.task_all(tasks)
    values = [int(t) for t in tasks_result]
    message = yield context.call_activity("ShowMeTheSum", values)

    return message


def main(context: str):
    orchestrate = df.Orchestrator.create(generator_function)

    result = orchestrate(context)

    return result
