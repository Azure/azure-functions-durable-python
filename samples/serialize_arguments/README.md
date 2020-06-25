# Serializing Custom Classes - Sample

This sample illustrates how to create custom classes that can be serialized for usage in Durable Functions for Python.
To create serializable classes, all we require is for your class to export two static methods: `to_json(<str>)` and `from_json(<str>)`.
The Durable Functions framework will interally call these classes to serialize and de-serialize your custom class. Therefore, you should
design these two functions such that calling `from_json` on the result of `to_json` is able to reconstruct your class.

For an example, please review the `shared_code` directory, where we declare a custom class that we call `SerializableClass` which implements
the required static methods.

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