import logging
import azure.functions as func
import azure.durable_functions as df

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def HttpStart(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def E1_SayHello(context: df.DurableOrchestrationContext):
    result1 = yield context.call_activity('say_hello', "Tokyo")
    result2 = yield context.call_activity('say_hello', "Seattle")
    result3 = yield context.call_activity('say_hello', "London")
    return [result1, result2, result3]

@myApp.activity_trigger(input_name="city")
def E1_SayHello(city: str) -> str:
    return f"Hello {city}!"