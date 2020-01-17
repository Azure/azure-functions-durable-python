"""Binding information for durable functions."""
import json
from typing import Dict


class DurableOrchestrationBindings:
    """Binding information.

    Provides information relevant to the creation and management of
    durable functions.
    """

    def __init__(self, client_data: str):
        """Create a new binding object."""
        context = json.loads(client_data)
        self.task_hub_name: str = context.get('taskHubName')
        self.creation_urls: Dict[str, str] = context.get('creationUrls')
        self.management_urls: Dict[str, str] = context.get('managementUrls')
