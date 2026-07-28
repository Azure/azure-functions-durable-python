|Branch|Status|
|---|---|
|main|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions/_apis/build/status/Azure.azure-functions-durable-python?branchName=main)](https://azfunc.visualstudio.com/Azure%20Functions/_build/latest?definitionId=58&branchName=main)|
|dev|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions/_apis/build/status/Azure.azure-functions-durable-python?branchName=dev)](https://azfunc.visualstudio.com/Azure%20Functions/_build/latest?definitionId=58&branchName=dev)|

# Durable Functions for Python

 [Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) is an extension of [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) that lets you write stateful functions in a serverless compute environment. The extension lets you define stateful workflows by writing orchestrator functions and stateful entities by writing entity functions using the Azure Functions programming model. Behind the scenes, the extension manages state, checkpoints, and restarts for you, allowing you to focus on your business logic.

 🐍  Find us on PyPi [here](https://pypi.org/project/azure-functions-durable/) 🐍   

## Durable Functions Python 2.0 beta

Version `2.0.0b1` of `azure-functions-durable` is now available from the
[Durable Task Python SDK](https://github.com/microsoft/durabletask-python).
This ground-up rewrite builds on the `durabletask` runtime. We encourage users
to try the beta and share feedback.

See the [Azure Functions Durable 2.x documentation](https://github.com/microsoft/durabletask-python/tree/main/azure-functions-durable)
for installation guidance and a comprehensive list of changes, including
breaking changes from 1.x.

When version 2.0.0 is released, this project will receive security patches
only. An official deprecation date is yet to be determined.

You can find more information at the following links:

* [Azure Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
* [Azure Functions Python developers guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Durable Functions overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=python)
* [Core concepts and features overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview).

> Durable Functions expects certain programming constraints to be followed. Please read the documentation linked above for more information.

## Getting Started

Follow these instructions to get started with Durable Functions in Python:

**🚀 [Python Durable Functions quickstart](https://docs.microsoft.com/azure/azure-functions/durable/quickstart-python-vscode)**

## Tooling

* Python Durable Functions requires [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) version 3.0.2630 or higher.

## OpenAI Agent SDK Integration with Azure Durable Functions (Preview)

Build resilient, stateful AI agents backed by Durable Functions orchestration—see the full documentation at [docs/openai_agents/README.md](docs/openai_agents/README.md).
