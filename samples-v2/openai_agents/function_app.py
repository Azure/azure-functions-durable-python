#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import os
import random

import azure.functions as func
import azure.durable_functions as df

from azure.identity import DefaultAzureCredential
from openai import AsyncAzureOpenAI

from agents import set_default_openai_client


#region Regular Azure OpenAI setup

# Initialize Azure credential
credential = DefaultAzureCredential()

# Token provider function that returns the token
def get_azure_token():
    return credential.get_token("https://cognitiveservices.azure.com/.default").token

# Initialize Azure OpenAI client with DefaultAzureCredential
openai_client = AsyncAzureOpenAI(
    azure_ad_token_provider=get_azure_token,
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
)

# Set the default OpenAI client for the Agents SDK
set_default_openai_client(openai_client)

# endregion


app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def orchestration_starter(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    # Starting a new orchestration instance in the most regular way
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response


@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def hello_world(context):
    import basic.hello_world
    return basic.hello_world.main()

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def agent_lifecycle_example(context):
    import basic.agent_lifecycle_example
    return basic.agent_lifecycle_example.main()


@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def dynamic_system_prompt(context):
    import basic.dynamic_system_prompt
    return basic.dynamic_system_prompt.main()

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def lifecycle_example(context):
    import basic.lifecycle_example
    return basic.lifecycle_example.main()


@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def local_image(context):
    import basic.local_image
    return basic.local_image.main()


@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def non_strict_output_type(context):
    import basic.non_strict_output_type
    return basic.non_strict_output_type.main()


@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def previous_response_id(context):
    import basic.previous_response_id
    return basic.previous_response_id.main()

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def remote_image(context):
    import basic.remote_image
    return basic.remote_image.main()

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def tools(context):
    import basic.tools
    return basic.tools.main()

@app.activity_trigger(input_name="max")
async def random_number_tool(max: int) -> int:
    """Return a random integer between 0 and the given maximum."""
    return random.randint(0, max)

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def message_filter(context):
    import handoffs.message_filter
    return handoffs.message_filter.main(context.create_activity_tool(random_number_tool))
