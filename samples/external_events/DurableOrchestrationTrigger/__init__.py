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
        ],
        "failed":[
            {
                "activity_func_name": "FailureActions",
                "args": "" 
            }
        ]
    }
    # timeout_task =

    # tasks = []
    # for event in json_rule["condition"]["wait_events"]:
    #     tasks.append(context.wait_for_external_event(event))
    
    # if json_rule["condition"]["logic"] == 'and':
    #     taskset = context.df.task_all(tasks)
    #     winner = yield context.task_any(taskset)
    #     # winner = yield context.df.task_any(taskset, timeout_task)
    # else: 
    #     # tasks.append(timeout_task)
    #     winner = yield context.task_any(tasks)
    
    # output = []
    # if winner != timeout_task:
    #     for action in json_rule["satisfied"]:
    #         result = yield context.call_activity(action["activity_func_name"], json.dumps(action["args"]))
    #         output.append(result)
    # else:
    #     for action in json_rule["failed"]:
    #         result = yield context.call_activity(action["activity_func_name"], json.dumps(action["args"]))
    #         output.append(result)
    # return output
   

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
