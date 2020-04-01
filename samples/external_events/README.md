# External Events - Sample
This sample exemplifies how to go about implementing the [Human interactions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=csharp#human) pattern in Python Durable Functions.

## Usage Instructions

### Create a `local.settings.json` file in this directory
This file stores app settings, connection strings, and other settings used by local development tools. Learn more about it [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#local-settings-file).
For this sample, you will only need an `AzureWebJobsStorage` connection string, which you can obtain from the Azure portal.

With you connection string, your `local.settings.json` file should look as follows, with `<your connection string>` replaced with the connection string you obtained from the Azure portal:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your connection string>",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

### Run the Sample
To try this sample, run  `func host start` in this directory. If all the system requirements have been met, and
after some initialization logs, you should see something like the following:

```bash
Http Functions:

        DurableTrigger: [POST,GET] http://localhost:7071/api/orchestrators/{functionName}

        RaiseEvent: [POST,GET] http://localhost:7071/api/RaiseEvent


```

This indicates that your `DurableTrigger` function can be reached via a `GET` or `POST` request to that URL. `DurableTrigger` starts the function-chaning orchestrator whose name is passed as a parameter to the URL. So, to start the orchestrator, which is named `DurableOrchestration`, make a GET request to `http://127.0.0.1:7071/api/orchestrators/DurableOrchestration`.  The second function raises an event.  The combination of these events raised will trigger the final function.  

### Example Use-cases
This section shows different implementation patterns for the trigger function.  These are just some examples to demostrate the applicability of the external event pattern.  

#### 1. Wait for a single external event
  
```
def generator_function(context):
	approved = yield context.wait_for_external_event("Approval")
	if approved:
		return "approved"
	else:
		return "denied"
```

#### 2. Wait for any of the external events

```
def generator_function(context):
	event1 = context.wait_for_external_event("Event1")
	event2 = context.wait_for_external_event("Event2")
	event3 = context.wait_for_external_event("Event3")
	winner = yield context.task_any([event1, event2, event3])
	
	if winner == event1:
		# ...
	elif winner == event2:
		# ...
	elif winner == event3:
		# ...
```


#### 3. Wait for all of the external events

```
def generator_function(context):
	gate1 = context.wait_for_external_event("Event1")
	gate2 = context.wait_for_external_event("Event2")
	gate3 = context.wait_for_external_event("Event3")
	yield context.task_all([gate1, gate2, gate3])
	yield context.call_activity("DurableActivity", "Hello")
```


#### 4. Raise an event

For example, you can create a Http triggered function that raises an event to an orchestrator, and call the following:
```
http://localhost:7071/api/RaiseEvent?instance_id={instance_id}&event_name={event_name}
```
In RaiseEvent/__ init __.py :
```
async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
	client = DurableOrchestrationClient(starter)
	instance_id = req.params.get("instance_id")
	event_name = req.params.get("event_name")
	await client.raise_event(instance_id, event_name, True)

	return func.HttpResponse(f'"{event_name}" event is sent')
```


### Define custom rules to handle external events
  Inspired by some real use cases, here is an example of how you can customize your orchestrators. You can pass in different json rulesets in the request body when you create a new orchestrator instance, and customize the new orchestrator to wait for different events. In the provided sample, this json ruleset will be hard coded.


Example json for a custom ruleset:
```
json_rule = {
	"condition": {
		"wait_events": ["A","B"],
		"logic": "and"
	},
	"satisfied": [
		{
			"activity_func_name": "SuccessActions",
			"args": {
				"name": "Tokyo"
			}
		}
	]
}
```
This ruleset asks the orchestrator to wait for event A and event B. When both events are received, go on and trigger an activity function named "SuccessActions"


In the orchestrator function:
```
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
```

Then in SuccessActions/__ init __.py   (Activity function):
```
def main(args: str) -> str:
	logging.warning(f"Activity Triggered: SuccessActions")
	args= json.loads(args)
	return  f'Hello {args["name"]}'
```