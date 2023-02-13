import azure.functions as func
import azure.durable_functions as df

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def durable_trigger(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response

@myApp.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    result = yield context.call_sub_orchestrator("sub_orchestrator", "Seattle")
    return result

@myApp.orchestration_trigger(context_name="context")
def sub_orchestrator(context: df.DurableOrchestrationContext):
    input_ = context.get_input()
    result1 = yield context.call_activity('hello', input_)
    return result1

@myApp.activity_trigger(input_name="name")
def hello(name: str):
    return "Hello " + name