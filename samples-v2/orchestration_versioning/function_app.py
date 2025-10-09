import logging
import azure.functions as func
import azure.durable_functions as df

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    
    # Get optional version from query parameter
    version = req.params.get('version')
    
    if version:
        instance_id = await client.start_new(function_name, version=version)
        logging.info(f"Started orchestration with ID = '{instance_id}' and version = '{version}'.")
    else:
        instance_id = await client.start_new(function_name)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
    
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    # context.version contains the value of defaultVersion in host.json
    # at the moment when the orchestration was created.
    if (context.version == "1.0"):
        # Legacy code path
        activity_result = yield context.call_activity('activity_a')
    else:
        # New code path
        activity_result = yield context.call_activity('activity_b')

    # Provide an opportunity to update and restart the app
    context.set_custom_status("Waiting for Continue event...")
    yield context.wait_for_external_event("Continue")
    context.set_custom_status("Continue event received")
    
    # You can explicitly pass a version to sub-orchestrators
    sub_result_with_version = yield context.call_sub_orchestrator('my_sub_orchestrator', version="0.9")
    
    # Without specifying version, the sub-orchestrator will use the current defaultVersion
    sub_result_default = yield context.call_sub_orchestrator('my_sub_orchestrator')
    
    return [
        f'Orchestration version: {context.version}', 
        f'Suborchestration version (explicit): {sub_result_with_version}',
        f'Suborchestration version (default): {sub_result_default}',
        activity_result
    ]

@myApp.orchestration_trigger(context_name="context")
def my_sub_orchestrator(context: df.DurableOrchestrationContext):
    return context.version

@myApp.activity_trigger(input_name="input")
def activity_a(input: str) -> str:
    return f"Hello from A!"

@myApp.activity_trigger(input_name="input")
def activity_b(input: str) -> str:
    return f"Hello from B!"
