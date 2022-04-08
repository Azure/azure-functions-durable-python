|Branch|Status|
|---|---|
|main|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions/_apis/build/status/Azure.azure-functions-durable-python?branchName=main)](https://azfunc.visualstudio.com/Azure%20Functions/_build/latest?definitionId=58&branchName=main)|
|dev|[![Build Status](https://azfunc.visualstudio.com/Azure%20Functions/_apis/build/status/Azure.azure-functions-durable-python?branchName=dev)](https://azfunc.visualstudio.com/Azure%20Functions/_build/latest?definitionId=58&branchName=dev)|

# Durable Functions for Python

 [Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) is an extension of [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) that lets you write stateful functions in a serverless compute environment. The extension lets you define stateful workflows by writing orchestrator functions and stateful entities by writing entity functions using the Azure Functions programming model. Behind the scenes, the extension manages state, checkpoints, and restarts for you, allowing you to focus on your business logic.

 🐍  Find us on PyPi [here](https://pypi.org/project/azure-functions-durable/) 🐍   


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

## Features and fixes coming soon to Extension Bundles

By default, Durable Functions for Python apps are set up to use [Extension Bundles](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-register#extension-bundles) to automatically manage binding extension dependencies; such as the [Durable Functions Extension](https://github.com/Azure/azure-functions-durable-extension). However, there can be a delay between the release of a new version of the Durable Functions Extension and its inclusion in the Extension Bundles feed.

[This query](https://github.com/Azure/azure-functions-durable-extension/issues?q=label%3A%22not+in+bundles+yet%22) provides a list of known upcoming features and bug fixes that are still _on their way_ to being included in Extension bundles.

If you need immediate access to an upcoming change in the Durable Functions Extension, please follow [these](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-register#explicitly-install-extensions) instructions to install the latest version of Durable Functions Nuget package [here](https://www.nuget.org/packages/Microsoft.Azure.WebJobs.Extensions.DurableTask).
