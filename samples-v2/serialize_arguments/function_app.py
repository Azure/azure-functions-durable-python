import azure.functions as func
import azure.durable_functions as df
from shared_code.MyClasses import SerializableClass

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def durable_trigger(req: func.HttpRequest, client):
    """This function starts up the orchestrator from an HTTP endpoint

    starter: str
        A JSON-formatted string describing the orchestration context

    message:
        An azure functions http output binding, it enables us to establish
        an http response.

    Parameters
    ----------
    req: func.HttpRequest
        An HTTP Request object, it can be used to parse URL
        parameters.
    """
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name, client_input=SerializableClass(5))
    response = client.create_check_status_response(req, instance_id)
    return response

@myApp.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    """This function provides the core function chaining orchestration logic

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API's to
        create orchestrations

    Returns
    -------
    int
        The number contained in the SerializableClass input object
    """
    input_: SerializableClass = context.get_input()
    num1: int = input_.show_number()

    # The custom class is also correctly serialized when calling an activity
    num2 = yield context.call_activity("simple_activity", SerializableClass(5))
    return num1


@myApp.activity_trigger(input_name="payload")
def simple_activity(payload):
    return payload