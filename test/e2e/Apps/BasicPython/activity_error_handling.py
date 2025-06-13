from datetime import datetime
import logging
import azure.functions as func
import azure.durable_functions as df

bp = df.Blueprint()

attempt_count = {}

class CustomException(Exception):
    pass

@bp.route(route="RethrowActivityException_HttpStart")
@bp.durable_client_input(client_name="client")
async def rethrow_activity_exception_http(req: func.HttpRequest, client):
    instance_id = await client.start_new('rethrow_activity_exception')
    
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.route(route="CatchActivityException_HttpStart")
@bp.durable_client_input(client_name="client")
async def catch_activity_exception_http(req: func.HttpRequest, client):
    instance_id = await client.start_new('catch_activity_exception')

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.route(route="CatchActivityExceptionFailureDetails_HttpStart")
@bp.durable_client_input(client_name="client")
async def catch_activity_exception_fd_http(req: func.HttpRequest, client):
    instance_id = await client.start_new('catch_activity_exception_failure_details')

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.route(route="RetryActivityException_HttpStart")
@bp.durable_client_input(client_name="client")
async def retry_activity_exception_http(req: func.HttpRequest, client):
    instance_id = await client.start_new('retry_activity_function')

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.route(route="CustomRetryActivityException_HttpStart")
@bp.durable_client_input(client_name="client")
async def custom_retry_activity_exception_http(req: func.HttpRequest, client):
    instance_id = await client.start_new('custom_retry_activity_function')

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

@bp.orchestration_trigger(context_name="context")
def rethrow_activity_exception(context: df.DurableOrchestrationContext):
    yield context.call_activity('raise_exception', context.instance_id)

@bp.orchestration_trigger(context_name="context")
def catch_activity_exception(context: df.DurableOrchestrationContext):
    try:
        yield context.call_activity('raise_exception', context.instance_id)
    except Exception as e:
        logging.error(f"Caught exception: {e}")
        return f"Caught exception: {e}"

@bp.orchestration_trigger(context_name="context")
def catch_activity_exception_failure_details(context: df.DurableOrchestrationContext):
    try:
        yield context.call_activity('raise_exception', context.instance_id)
    except Exception as e:
        logging.error(f"Caught exception: {e}")
        return f"Caught exception: {e}"

@bp.orchestration_trigger(context_name="context")
def retry_activity_function(context: df.DurableOrchestrationContext):
    yield context.call_activity_with_retry('raise_exception', retry_options=df.RetryOptions(
        first_retry_interval_in_milliseconds=5000,
        max_number_of_attempts=3
    ), input_=context.instance_id)
    return "Success"

@bp.orchestration_trigger(context_name="context")
def custom_retry_activity_function(context: df.DurableOrchestrationContext):
    yield context.call_activity_with_retry('raise_complex_exception', retry_options=df.RetryOptions(
        first_retry_interval_in_milliseconds=5000,
        max_number_of_attempts=3
    ), input_=context.instance_id)
    return "Success"

@bp.activity_trigger(input_name="instance")
def raise_exception(instance: str) -> str:
    global attempt_count
    if instance not in attempt_count:
        attempt_count[instance] = 1
        raise CustomException(f"This activity failed")
    return "This activity succeeded"

@bp.activity_trigger(input_name="instance2")
def raise_complex_exception(instance2: str) -> str:
    global attempt_count
    if instance2 not in attempt_count:
        attempt_count[instance2] = 1
        raise CustomException(f"This activity failed") from Exception("More information about the failure")
    return "This activity succeeded"
