import azure.functions as func

from azure.durable_functions.durable_orchestration_client import get_client


def main(req: func.HttpRequest, starter: str, message):
    client = get_client(starter)
    client.start_new('DurableOrchestrationTrigger', None, None)
    message.set(func.HttpResponse(status_code=200, body="success"))
