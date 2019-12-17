import azure.functions as func

from azure.durable_functions import DurableOrchestrationClient


def main(req: func.HttpRequest, starter: str, message):
    client = DurableOrchestrationClient(starter)
    client.start_new('DurableFanoutOrchestrationTrigger', None, None)
    message.set(func.HttpResponse(status_code=200, body=starter))
