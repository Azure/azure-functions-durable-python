import logging

import azure.durable_functions as df


def generator_function(context):
    tasks = []

    for i in range(30):
        current_task = context.df.callActivity("DurableActivity", str(i))
        tasks.append(current_task)

    results = yield context.df.task_all(tasks)
    logging.warning(f"!!! fanout results {results}")
    return results


def main(context: str):
    logging.warning("Durable Orchestration Trigger: " + context)
    orchestrate = df.Orchestrator.create(generator_function)
    logging.warning("!!!type(orchestrate) " + str(type(orchestrate)))
    result = orchestrate(context)
    logging.warning("!!!serialized json : " + result)
    logging.warning("!!!type(result) " + str(type(result)))
    return result
