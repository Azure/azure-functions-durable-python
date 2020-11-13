|Branch|Status|
|---|---|
|master|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=master)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=master)|
|dev|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_apis/build/status/Azure%20Functions%20Durable%20Python?branchName=dev)](https://azfunc.visualstudio.com/Azure%20Functions%20Python/_build/latest?definitionId=44&branchName=dev)|

# Durable Functions for Python

 [Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) is a programming model for describing _stateful_ workflows in a serverless enviroment. Durable Functions empowers programmers to specify their
 workflows _as code_, meaning that developers can make good use of Python's idioms,
 tools, libraries, and its overall programming ecosystem to implement complex systems with ease.

 🐍  Find us on PyPi [here](https://pypi.org/project/azure-functions-durable/) 🐍   


## More than just stateful Azure Functions
Durable Functions is offered as an extension of [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview). The extension manages state, checkpoints, and restarts for you. Python Durable Functions' advantages include:

* Defining workflows as code. No JSON schemas or designers are needed.
* Managing return values, exceptions, and control-flow using familiar Python constructs.
* Scheduling serverless functions synchronously and asynchronously.
* Automatically checkpointing progress whenever the function schedules async work. Local state is never lost if the process recycles or the VM reboots.

You can find more information at the following links:

* [Azure Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
* [Azure Functions Python developers guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Durable Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=python)

## Core Concepts

A Durable Functions application is a solution made up of Azure Functions serving one of four distinct roles. These roles are outline below: 

* **Activity:** they are the basic unit of work, a task to be scheduled.
* **Orchestrator:** they describe which actions to execute, in what order to schedule them, deal with exceptions, etc. As their name implies, they organize and manage a workflow to completion.
* **Entity:**  They allow you to read and update small pieces of state. Unlike orchestrators, entities manage state explicitely instead of implicitely managing it via control flow.
* **Client:** They serve as the entry point for creating an instance of a durable application, often times serving to deliver the initiating message that a workflow will use to begin its execution.

Durable Functions' function types and features are documented in-depth [here.](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview).

> Some of the function roles outline above expect specific programming constraints to be followed, such as idempotency and replayability. Please read the documentation linked above for more information.

## Getting Started

Follow these instructions to get started with Durable Functions in Python:

**🚀 [Python Durable Functions quickstart](https://docs.microsoft.com/azure/azure-functions/durable/quickstart-python-vscode)**

## Samples

Take a look at this project's [samples directory](./samples/):

* [Function Chaining](./samples/function_chaining)
* [Fan-out/Fan-in - Simple](./samples/fan_out_fan_in)
* [Fan-out/Fan-in - TensorFlow](./samples/fan_out_fan_in_tensorflow)
* [External Events - Human Interaction & Timeouts](./samples/external_events)

## Tooling

* Python Durable Functions requires [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) version 3.0.2630 or higher.