# Function Chaining - Sample

This sample exemplifies how to go about implementing [Sub-Orchestration](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-sub-orchestrations?tabs=csharp) in Python Durable Functions.

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

        durable_trigger: [POST,GET] http://localhost:7071/api/start_sub
```

This indicates that your `durable_trigger` function can be reached via a `GET` or `POST` request to that URL. `durable_trigger` starts the function-chaning orchestrator whose name is passed as a parameter to the URL. So, to start the orchestrator, which is named `orchestrator`, make a GET request to `http://127.0.0.1:7071/api/orchestrators/orchestrator`.

And that's it! You should see a JSON response with five URLs to monitor the status of the orchestration. To learn more about this, please read [here](TODO)!