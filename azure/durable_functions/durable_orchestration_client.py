import logging
from .models import DurableOrchestrationClient


def getClient(context) -> DurableOrchestrationClient:
    logging.warninging(str(context))

    return DurableOrchestrationClient(context)
