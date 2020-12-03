# Function Chaining with Custom Status - Sample

This sample demonstrates how to go about implementing the [Function Chaining](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=csharp#chaining) pattern in Python Durable Functions.

It additionally demonstrates how to go about setting intermittent status while an orchestation is executing. This enables a user to monitor the status of the orchestration through a custom message set by the user.

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
```

This indicates that your `DurableTrigger` function can be reached via a `GET` or `POST` request to that URL. `DurableTrigger` starts the function-chaning orchestrator whose name is passed as a parameter to the URL. So, to start the orchestrator, which is named `DurableOrchestration`, make a GET request to `http://127.0.0.1:7071/api/orchestrators/DurableOrchestration`.

And that's it! You should see a JSON response with five URLs to monitor the status of the orchestration. To learn more about this, please read [here](TODO)!