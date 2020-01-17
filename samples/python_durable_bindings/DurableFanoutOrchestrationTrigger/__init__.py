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


if __name__ == "__main__":
    main('{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:18:41.3240927Z"},\
        {"OrchestrationInstance":{"InstanceId":"48d0f95957504c2fa579e810a390b938","ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},\
        "EventType":0,"ParentInstance":null,"Name":"DurableFunctionsOrchestratorJS","Version":"","Input":"null","Tags":null,"EventId":-1,\
        "IsPlayed":false,"Timestamp":"2019-12-08T23:18:39.756132Z"}],"input":null,"instanceId":"48d0f95957504c2fa579e810a390b938",\
        "isReplaying":false,"parentInstanceId":null}')
