# Customer Service Sample

This sample demonstrates a customer service agent built with Azure Durable Functions and OpenAI Agents. The agent can handle airline-related queries including FAQ lookups and seat booking.

## Running the Sample

**For complete setup instructions, configuration details, and troubleshooting, see the [Getting Started Guide](/docs/openai_agents/getting-started.md).**

### Step 1: Start the Azure Functions App

From the OpenAI Agents samples root directory (`/samples-v2/openai_agents`), start the Azure Functions host:

```bash
func start
```

The function app will start and listen on `http://localhost:7071` by default.

### Step 2: Start the Interactive Client

In a separate terminal, navigate to the `customer_service` directory and run the client:

```bash
cd customer_service
python customer_service_client.py
```

If your function app is running on a different host or port, you can specify a custom URL:

```bash
python customer_service_client.py --start-url http://<app-host-URL>/api/orchestrators/customer_service
```

The client will:

1. Start a new orchestration instance
2. Wait for prompts from the agent
3. Allow you to interact with the customer service agent interactively

## Usage

Once the client is running, you can:

- Ask FAQ questions (e.g., "What's the baggage policy?", "Is there wifi?")
- Request seat changes (the agent will guide you through the process)
- Type `exit`, `quit`, or `bye` to end the conversation
