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
* [Durable Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)

A durable function, or _orchestration_, is a solution made up of different types of Azure Functions:

* **Activity:** the functions and tasks being orchestrated by your workflow.
* **Orchestrator:** a function that describes the way and order actions are executed in code.
* **Client:** the entry point for creating an instance of a durable orchestration.

Durable Functions' function types and features are documented in-depth [here.](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview)

## Current limitations

We're actively working on Python support for Durable Functions and we expect a Public Preview announcement in Q2 CY2020. The following are the current known limitations.

### Functionality

* `DurableOrchestrationContext.create_timer()` is not yet supported (coming soon [#35](https://github.com/Azure/azure-functions-durable-python/issues/35))
* Sub-orchestrations are not yet supported (planned [#62](https://github.com/Azure/azure-functions-durable-python/issues/62))
* Durable Entities are not yet supported (not yet planned [#96](https://github.com/Azure/azure-functions-durable-python/issues/96))

### Tooling

* Python Durable Functions requires updated versions of Azure Functions Core Tools that includes Python worker [1.1.0](https://github.com/Azure/azure-functions-python-worker/releases/tag/1.1.0), templates ([bundle-1.2.0](https://github.com/Azure/azure-functions-templates/releases/tag/bundle-1.2.0)), and extension bundles ([1.2.0](https://github.com/Azure/azure-functions-extension-bundles/releases/tag/1.2.0)) that are not yet released (ETA May 2020). Use the VS Code dev container in the [Getting Started](#getting-started) section to access a development environment with the required versions of the tools installed.

### Deployment

* Python Durable Functions requires an updated version of the Azure Functions Python language worker ([1.1.0](https://github.com/Azure/azure-functions-python-worker/releases/tag/1.1.0)) that is not yet available in Azure. Deploy your Python Durable Functions apps in containers (requires Premium or App Service plans). (Linux consumption plan support ETA May 2020)

## Getting Started

Follow these instructions to get started with Durable Functions in Python:

**🚀 [Python Durable Functions quickstart](https://aka.ms/pythondurable)**

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
