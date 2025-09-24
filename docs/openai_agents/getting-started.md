# Getting Started with the OpenAI Agents Integration for Reliability on Azure Functions (Preview)

Getting started guide for implementing stateful AI agents using Azure Durable Functions orchestration with automatic checkpointing and replay semantics.

## Prerequisites

- Python 3.10+ runtime environment
- Azure Functions Core Tools v4.x (`npm install -g azure-functions-core-tools@4 --unsafe-perm true`)
- Azure OpenAI service endpoint with model deployment
- Docker (Optional for the Durable Task Scheduler Emulator)

## Environment Setup

### Create an Azure Functions App

This framework is designed specifically for **Azure Functions applications**. You need to create a Python Functions app to use the OpenAI Agents Integration for Reliability on Azure Functions (Preview).

**For new users**: If you're new to Azure Functions, follow these guides to get started:
- [Create your first Python function in Azure](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)
- [Azure Functions Python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)

**For experienced Functions users**: Create a new Python Functions app or use an existing one.

**Note**: The `samples-v2/openai_agents` directory contains a complete working example you can reference or use as a starting point.

### Set Up Local Development Environment

Create and activate a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Install Dependencies

Add the OpenAI Agents dependencies to your `requirements.txt`:

```
azure-functions-durable
azure-functions
openai
openai-agents
azure-identity
```

Then install them:

```bash
pip install -r requirements.txt
```

> Dependency & compatibility: The `azure-functions-durable` package does NOT declare `openai` or `openai-agents` as dependencies. If you need the OpenAI Agents Integration for Reliability on Azure Functions (Preview), explicitly add `openai` and `openai-agents` to your `requirements.txt` (see `samples-v2/openai_agents/requirements.txt`). This integration is validated with the versions currently pinned there (`openai==1.107.3`, `openai-agents==0.3.0`). Because the OpenAI ecosystem changes rapidly, if you encounter issues, first pin to these versions to rule out a version mismatch before filing an issue.

### Configuring Durable Task Scheduler Backend

**Durable Task Scheduler is the preferred backend** for this integration as it provides enhanced performance, better observability, and simplified local development. While not a hard requirement, it's strongly recommended for production workloads.

IMPORTANT: Ensure your function app is using the *preview* extension bundle version 4.34.0 or higher by specifying it in `host.json`:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle.Preview",
    "version": "[4.34.0, 5.0.0)"
  }
}
```

There are two ways to configure the backend locally:

#### Using the Emulator (Recommended)

The emulator simulates a scheduler and taskhub in a Docker container, making it ideal for development and learning.

1. **Pull the Docker Image for the Emulator:**
```bash
docker pull mcr.microsoft.com/dts/dts-emulator:latest
```

2. **Run the Emulator:**
```bash
docker run --name dtsemulator -d -p 8080:8080 -p 8082:8082 mcr.microsoft.com/dts/dts-emulator:latest
```

3. **Wait for container readiness** (approximately 10-15 seconds)

4. **Verify emulator status:**
```bash
curl http://localhost:8080/health
```

**Note**: The sample code automatically uses the default emulator settings (`endpoint: http://localhost:8080`, `taskhub: default`). No additional environment variables are required.

#### Alternative: Azure Storage Backend

If you prefer using Azure Storage as the backend (legacy approach):

```bash
# Uses local storage emulator - requires Azurite
npm install -g azurite
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

Update `local.settings.json`:
```json
{
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true"
  }
}
```

## Configuration

1. **Install project dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure service settings:**

Update `local.settings.json` with your service configuration:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "https://<resource-name>.openai.azure.com/",
    "AZURE_OPENAI_DEPLOYMENT": "<deployment-name>",
    "OPENAI_DEFAULT_MODEL": "<deployment-name>",
    "AZURE_OPENAI_API_VERSION": "2024-10-01-preview",
    "DURABLE_TASK_SCHEDULER_CONNECTION_STRING": "Endpoint=http://localhost:8080;Authentication=None;",
    "TASKHUB": "default"
  }
}
```

## Hello World Example

Execute the included hello world sample.

```python
# basic/hello_world.py - Standard OpenAI Agent
from agents import Agent, Runner

def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )
    result = Runner.run_sync(agent, "Tell me about recursion in programming.")
    return result.final_output
```

**Durable Transformation**: The `@app.durable_openai_agent_orchestrator` decorator in `function_app.py` wraps this agent execution within a Durable Functions orchestrator, providing agent state persisted at each LLM and tool interaction.

## Execution and Monitoring

1. **Start the Azure Functions host:**

Navigate to the `samples-v2/openai_agents` directory and run:

```bash
func start --port 7071
```

2. **Initiate orchestration instance:**

```bash
curl -X POST http://localhost:7071/api/orchestrators/hello_world \
  -H "Content-Type: application/json"
```

Response contains orchestration instance metadata:

```json
{
  "id": "f4b2c8d1e9a7...",
  "statusQueryGetUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/f4b2c8d1e9a7...",
  "sendEventPostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/f4b2c8d1e9a7.../raiseEvent/{eventName}",
  "terminatePostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/f4b2c8d1e9a7.../terminate",
  "purgeHistoryDeleteUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/f4b2c8d1e9a7..."
}
```

3. **Monitor execution via Durable Task Scheduler dashboard:**

Navigate to `http://localhost:8082` for real-time orchestration monitoring:
- Instance execution timeline with LLM call latencies
- State transition logs and checkpoint data
- Retry attempt tracking and failure analysis

## Next Steps

- Reference [Reference Documentation](reference.md) for complete technical details.