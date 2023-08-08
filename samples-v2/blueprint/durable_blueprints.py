import logging
import azure.functions as func
import azure.durable_functions as df

# To learn more about blueprints in the Python prog model V2,
# see: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators#blueprints

# Note, the `func` namespace does not contain Durable Functions triggers and bindings, so to register blueprints of
# DF we need to use the `df` package's version of blueprints.
bp = df.Blueprint()

# We define a standard function-chaining DF pattern

@bp.route(route="startOrchestrator")
@bp.durable_client_input(client_name="client")
async def start_orchestrator(req: func.HttpRequest, client):
    instance_id = await client.start_new("my_orchestrator")
    
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    result1 = yield context.call_activity('say_hello', "Tokyo")
    result2 = yield context.call_activity('say_hello', "Seattle")
    result3 = yield context.call_activity('say_hello', "London")
    return [result1, result2, result3]

@bp.activity_trigger(input_name="city")
def say_hello(city: str) -> str:
    return f"Hello {city}!"