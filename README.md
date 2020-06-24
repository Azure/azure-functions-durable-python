|Branch|Status|
|---|---|
|master|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=master)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=master)|
|dev|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=dev)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=dev)|

# Durable Functions for Python

The `azure-functions-durable` [pip](https://pypi.org/project/azure-functions-durable/) package allows you to write [Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) for [Python](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python). Durable Functions is an extension of [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) that lets you write stateful functions and workflows in a serverless environment. The extension manages state, checkpoints, and restarts for you. Durable Functions' advantages include:

* Define workflows in code. No JSON schemas or designers are needed.
* Call other functions synchronously and asynchronously. Output from called functions can be saved to local variables.
* Automatically checkpoint progress whenever the function schedules async work. Local state is never lost if the process recycles or the VM reboots.

You can find more information at the following links:

* [Azure Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
* [Azure Functions Python developers guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Durable Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=python)

A durable function, or _orchestration_, is a solution made up of different types of Azure Functions:

* **Activity:** the functions and tasks being orchestrated by your workflow.
* **Orchestrator:** a function that describes the way and order actions are executed in code.
* **Client:** the entry point for creating an instance of a durable orchestration.

Durable Functions' function types and features are documented in-depth [here.](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview)

## Current limitations

Python support for Durable Functions is currently in public preview. The following are the current known limitations.

### Functionality

* Sub-orchestrations are not yet supported (planned [#62](https://github.com/Azure/azure-functions-durable-python/issues/62))
* Durable Entities are not yet supported (not yet planned [#96](https://github.com/Azure/azure-functions-durable-python/issues/96))

### Tooling

* Python Durable Functions requires [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) version 3.0.2630 or higher.

## Getting Started

Follow these instructions to get started with Durable Functions in Python:

**🚀 [Python Durable Functions quickstart](https://docs.microsoft.com/azure/azure-functions/durable/quickstart-python-vscode)**

## Samples

Take a look at this project's [samples directory](./samples/):

* [Function Chaining](./samples/function_chaining)
* [Fan-out/Fan-in - Simple](./samples/fan_out_fan_in)
* [Fan-out/Fan-in - TensorFlow](./samples/fan_out_fan_in_tensorflow)
* [External Events - Human Interaction & Timeouts](./samples/external_events)

### Orchestrator example

```python
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    task1 = yield context.call_activity("DurableActivity", "One")
    task2 = yield context.call_activity("DurableActivity", "Two")
    task3 = yield context.call_activity("DurableActivity", "Three")

    outputs = [task1, task2, task3]
    return outputs


main = df.Orchestrator.create(orchestrator_function)
```
