import logging

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    tasks = []

    for i in range(30):
        current_task = context.call_activity("DurableActivity", str(i))
        tasks.append(current_task)

    results = yield context.task_all(tasks)
    logging.warning(f"!!! fanout results {results}")
    return results


main = df.Orchestrator.create(orchestrator_function)
