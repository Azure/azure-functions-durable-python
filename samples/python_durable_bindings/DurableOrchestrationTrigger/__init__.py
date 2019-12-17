import logging
import azure.functions as func
import azure.durable_functions as df


def generator_function(context):
    outputs = []

    task1 = yield context.df.callActivity("DurableActivity", "One")
    logging.warning(f"!!!task1: {task1}")

    task2 = yield context.df.callActivity("DurableActivity", "Two")
    logging.warning(f"!!!task2: {task2}")

    task3 = yield context.df.callActivity("DurableActivity", "Three")
    logging.warning(f"!!!task3: {task3}")


    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


def main(context: str):
    logging.warning("Durable Orchestration Trigger: " + context)
    orchestrate = df.Orchestrator.create(generator_function)
    logging.warning("!!!type(orchestrate) " + str(type(orchestrate)))
    result = orchestrate(context)
    logging.warning("!!!serialized json : " + result)
    logging.warning("!!!type(result) " + str(type(result)))

    return result
