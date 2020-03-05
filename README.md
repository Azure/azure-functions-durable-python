|Branch|Status|
|---|---|
|master|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=master)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=master)|
|dev|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=dev)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=dev)|

# Durable Functions for Python

The `azure-functions-durable` [pip](https://pypi.org/project/azure-functions-durable/) package allows you to write [Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) for Python(https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python). Durable Functions is an extension of [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) that lets you write stateful functions and workflows in a serverless environment. The extension manages state, checkpoints, and restarts for you. Durable Functions' advantages include:

* Define workflows in code. No JSON schemas or designers are needed.
* Call other functions synchronously and asynchronously. Output from called functions can be saved to local variables.
* Automatically checkpoint progress whenever the function schedules async work. Local state is never lost if the process recycles or the VM reboots.

You can find more information at the following links:

* [Azure Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
* [Azure Functions Python developers guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Durable Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)

A durable function, or _orchestration_, is a solution made up of different types of Azure Functions:

* **Activity:** the functions and tasks being orchestrated by your workflow.
* **Orchestrator:** a function that describes the way and order actions are executed in code.
* **Client:** the entry point for creating an instance of a durable orchestration.

Durable Functions' function types and features are documented in-depth [here.](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview)

## Getting Started

You can follow the instructions below to get started with a function chaining example, or follow the general checklist below:

1. Install prerequisites:
    - [Azure Functions Core Tools version 2.x](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools)
    - [Azure Storage Emulator](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-emulator) (Windows) or an actual Azure storage account (Mac or Linux)
    - Python 3.6 or later

2. [Create an Azure Functions app.](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python)

3. Install the Durable Functions extension

Run this command from the root folder of your Azure Functions app:
```bash
func extensions install -p Microsoft.Azure.WebJobs.Extensions.DurableTask -v 1.8.3
```

**durable-functions requires Microsoft.Azure.WebJobs.Extensions.DurableTask 1.7.0 or greater.**

4. Install the `azure-durable-functions` pip package at the root of your function app:

Create and activate virtual environment
```
python3 -m venv env
source env/bin/activate
```

```bash
pip install azure-durable-functions
```

5. Write an activity function ([see sample](./samples/python_durable_bindings/DurableActivity)):
```python
def main(name: str) -> str:
    logging.info(f"Activity Triggered: {name}")
    # your code here
```

6. Write an orchestrator function ([see sample](./samples/python_durable_bindings/DurableOrchestrationTrigger)):

```python
def main(context: str):
    orchestrate = df.Orchestrator.create(generator_function)
    result = orchestrate(context)
    return result
```

**Note:** Orchestrator functions must follow certain [code constraints.](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-checkpointing-and-replay#orchestrator-code-constraints)

7. Write your client function ([see sample](./samples/DurableOrchestrationClient/)):

TBD

**Note:** Client functions are started by a trigger binding available in the Azure Functions 2.x major version. [Read more about trigger bindings and 2.x-supported bindings.](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings#overview)

## Samples

The [Durable Functions samples](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-install) demonstrate several common use cases. They are located in the [samples directory.](./samples/) Descriptive documentation is also available:

* [Function Chaining - Hello Sequence](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-sequence)
* [Fan-out/Fan-in - Cloud Backup](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-cloud-backup)
* [Monitors - Weather Watcher](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-monitor)
* [Human Interaction & Timeouts - Phone Verification](https://docs.microsoft.com/en-us/azure/azure-functions/durable-functions-phone-verification)

```python
def generator_function(context):
    outputs = []
    task1 = yield context.call_activity("DurableActivity", "One")
    task2 = yield context.call_activity("DurableActivity", "Two")
    task3 = yield context.call_activity("DurableActivity", "Three")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs
```
