import logging
import azure.functions as func
import azure.durable_functions as df

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    if (context.version == "1.0"):
        # Legacy code path
        activity_result = yield context.call_activity('say_hello', "v1.0")
    else:
        # New code path
        activity_result = yield context.call_activity('say_hello', f"v{context.version}")

    """
    While the orchestration is waiting for the external event,
    stop the app, update the defaultVersion in host.json to "2.0",
    then restart the app and send a "Continue" event.
    This orchestration instance should continue with the old version.
    """
    context.set_custom_status("Waiting for Continue event...")
    yield context.wait_for_external_event("Continue")
    context.set_custom_status("Continue event received")
    
    """
    New orchestration instances (including sub-orchestrations)
    will use the current defaultVersion specified in host.json.
    """
    sub_result = yield context.call_sub_orchestrator('my_sub_orchestrator')
    return [f'Orchestration version: {context.version}', f'Suborchestration version: {sub_result}', activity_result]

@myApp.orchestration_trigger(context_name="context")
def my_sub_orchestrator(context: df.DurableOrchestrationContext):
    return context.version

@myApp.activity_trigger(input_name="city")
def say_hello(city: str) -> str:
    return f"Hello {city}!"