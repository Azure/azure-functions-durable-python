import logging
import azure.durable_functions as df
import json

def generator_function(context):

    json_rule={
        "condition": {
            "wait_events": ["A","B"],
            "logic": "and"
        },
        "satisfied":[
            {
                "activity_func_name": "SuccessActions",
                "args": {
                    "name": "abcd"
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


def main(context: str):
    """This function creates the orchestration and provides
    the durable framework with the core orchestration logic
    
    Arguments:
        context {str} -- Function context containing the orchestration API's 
        and current context of the long running workflow.
    
    Returns:
        OrchestratorState - State of current orchestration
    """
    orchestrate = df.Orchestrator.create(generator_function)
    result = orchestrate(context)
    return result
