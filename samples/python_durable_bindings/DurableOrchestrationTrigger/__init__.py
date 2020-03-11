import logging

import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    outputs = []

    task1 = yield context.call_activity("DurableActivity", "One")
    task2 = yield context.call_activity("DurableActivity", "Two")
    task3 = yield context.call_activity("DurableActivity", "Three")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


main = df.Orchestrator.create(orchestrator_function)
