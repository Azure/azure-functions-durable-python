# Azure Functions Durable OpenAI Agents Samples

This repository contains samples demonstrating how to use OpenAI Agents with Azure Durable Functions in Python.

## Prerequisites

Before running these samples, ensure you have the following:

1. **Python 3.8 or later** installed on your system
2. **Azure Functions Core Tools** v4.x installed ([Installation Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local))
3. **Azure OpenAI Service** set up with a deployed model
4. **Azure CLI** (optional, for authentication)

## Setup

### 1. Clone and Navigate to the Project

```bash
git clone <repository-url>
cd azure-functions-durable-python/samples-v2/openai_agents
```

### 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:
- **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
- **Windows (Command Prompt)**: `.venv\Scripts\activate.bat`
- **macOS/Linux**: `source .venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Durable Functions Extension

Install the Azure Durable Functions extension for OpenAI Agents from the parent directory:

```bash
pip install -e ..\..
```

This step is required because this sample uses a local development version of the `azure.durable_functions.openai_agents` module that extends Azure Durable Functions with OpenAI Agents support. The `-e` flag installs the package in "editable" mode, which means changes to the source code will be reflected immediately without reinstalling.

### 5. Configure Environment Variables

Copy the template file and update it with your Azure OpenAI settings:

```bash
cp local.settings.json.template local.settings.json
```

Edit `local.settings.json` and replace the placeholder values:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "https://your-openai-service.openai.azure.com/",
    "AZURE_OPENAI_DEPLOYMENT": "your-gpt-deployment-name",
    "AZURE_OPENAI_API_VERSION": "2025-03-01-preview"
  }
}
```

**Required Configuration:**
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
- `AZURE_OPENAI_DEPLOYMENT`: The name of your deployed GPT model
- `AZURE_OPENAI_API_VERSION`: API version (default: "2025-03-01-preview")

### 6. Authentication

This sample uses Azure Default Credential for authentication. Make sure you're authenticated to Azure:

```bash
az login
```

Alternatively, you can use other authentication methods supported by Azure Default Credential:
- Managed Identity (when running in Azure)
- Visual Studio/VS Code authentication
- Environment variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`)

## Running the Samples

### 1. Start the Azure Functions Host

```bash
func host start
```

The function app will start and display the available endpoints.

### 2. Trigger the Hello World Sample

Once the function is running, you can trigger the orchestrator using HTTP requests:

```bash
# Start the hello_world orchestration
curl -X POST "http://localhost:7071/api/orchestrators/hello_world"
```

This will return a response with URLs to check the orchestration status:

```json
{
    "id": "abc123...",
    "statusQueryGetUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../",
    "sendEventPostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../raiseEvent/{eventName}",
    "terminatePostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../terminate",
    "purgeHistoryDeleteUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../",
    "restartPostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/abc123.../restart"
}
```

### 3. Check Orchestration Status

Use the `statusQueryGetUri` from the response to check the status:

```bash
curl "http://localhost:7071/runtime/webhooks/durabletask/instances/{instance-id}/"
```

## Available Samples

### Hello World (`basic/hello_world.py`)

A simple example that demonstrates:
- Creating an OpenAI Agent with specific instructions (responds only in haikus)
- Running the agent synchronously with a query about recursion
- Returning the agent's response

The agent is configured to respond only in haiku format and will answer questions about programming concepts.

## Project Structure

```
openai_agents/
├── function_app.py              # Main Azure Functions app with orchestrator
├── requirements.txt             # Python dependencies
├── host.json                   # Azure Functions host configuration
├── local.settings.json.template # Environment variables template
├── local.settings.json         # Your local configuration (gitignored)
├── basic/
│   └── hello_world.py          # Hello world agent sample
└── README.md                   # This file
```

## Key Components

### `function_app.py`
- Sets up Azure OpenAI client with Azure Default Credential
- Configures the durable functions orchestrator
- Provides HTTP trigger for starting orchestrations

### `basic/hello_world.py`
- Demonstrates basic agent creation and execution
- Shows how to use the OpenAI Agents SDK with custom instructions

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure you're logged in to Azure CLI or have proper environment variables set
2. **OpenAI Endpoint Errors**: Verify your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT` settings
3. **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed
4. **Function Host Issues**: Make sure Azure Functions Core Tools are properly installed

### Debugging

- Check the function logs in the terminal where you ran `func host start`
- Use the status URLs returned by the orchestrator to monitor execution
- Verify your Azure OpenAI service is accessible and the deployment is active

## Next Steps

- Explore more complex agent scenarios
- Add custom tools and functions to your agents
- Integrate with other Azure services
- Deploy to Azure Functions for production use

## Resources

- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OpenAI Agents SDK](https://github.com/openai/openai-python)
