import logging

import azure.durable_functions as df


def generator_function(context):
    outputs = []

    task1 = yield context.callActivity("DurableActivity", "One")
    task2 = yield context.callActivity("DurableActivity", "Two")
    task3 = yield context.callActivity("DurableActivity", "Three")

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
