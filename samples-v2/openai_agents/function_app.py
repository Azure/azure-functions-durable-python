import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def hello_orchestration_starter(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response


@app.orchestration_trigger(context_name="context")
def basic_hello_world_orchestrator(context):
    result = yield context.call_activity("openai_agent_activity")
    return result

# Activity for OpenAI agent execution
@app.activity_trigger(input_name="input")
async def openai_agent_activity(input: str):
    # TODO: Instead of wrapping this code in an activity function like this,
    # we should be able to invoke it from the orchestrator directly.
    # In order to enable this, Runner.run invocations should be implicitly
    # wrapped in activity invocations. 
    from basic.hello_world import main
    result = await main()
    return result
