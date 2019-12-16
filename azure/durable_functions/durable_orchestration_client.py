import logging
from .models import DurableOrchestrationClient


def get_client(context) -> DurableOrchestrationClient:
    logging.warning(str(context))

    return DurableOrchestrationClient(context)
