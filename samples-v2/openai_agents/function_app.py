import os

import azure.functions as func
from azure.durable_functions.openai_agents import durable_openai_agent_orchestrator
from azure.identity import AzureDefaultCredential
from openai import AsyncAzureOpenAI

from agents import set_default_openai_client


#region Regular Azure OpenAI setup

# Initialize Azure credential
credential = AzureDefaultCredential()

# Token provider function that returns the token
def get_azure_token():
    return credential.get_token("https://cognitiveservices.azure.com/.default").token

# Initialize Azure OpenAI client with AzureDefaultCredential
openai_client = AsyncAzureOpenAI(
    azure_ad_token_provider=get_azure_token,
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
)

# Set the default OpenAI client for the Agents SDK
set_default_openai_client(openai_client)

# endregion


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def orchestration_starter(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    # Starting a new orchestration instance in the most regular way
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response


@app.orchestration_trigger(context_name="context")
@durable_openai_agent_orchestrator
def hello_world(context):
    import basic.hello_world
    return basic.hello_world.main()
