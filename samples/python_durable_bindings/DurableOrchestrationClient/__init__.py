import logging
import azure.functions as func
from azure.durable_functions.constants import DEFAULT_LOCAL_HOST
from azure.durable_functions.durable_orchestration_client import getClient

def main(req: func.HttpRequest, starter: str, message):
    client = getClient("client context")
    message.set(func.HttpResponse(status_code=200, body="success"))