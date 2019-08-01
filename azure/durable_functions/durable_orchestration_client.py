import logging
from .models import DurableOrchestrationClient


def getClient(context) -> DurableOrchestrationClient:
    logging.warn(str(context))
    return DurableOrchestrationClient()
