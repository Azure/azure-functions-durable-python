import logging
import azure.functions as func
import azure.durable_functions as df


def generator_function(context):
    tasks = []

    for i in range(30):
        current_task = context.df.callActivity("DurableActivity", str(i))
        tasks.append(current_task)

    results = yield context.df.task_all(tasks)
    logging.warn(f"!!! fanout results {results}")
    return results


def main(context: str):
    logging.warn("Durable Orchestration Trigger: " + context)
    orchestrate = df.Orchestrator.create(generator_function)
    logging.warn("!!!type(orchestrate) " + str(type(orchestrate)))
    result = orchestrate(context)
    logging.warn("!!!serialized json : " + result)
    logging.warn("!!!type(result) " + str(type(result)))
    return result
