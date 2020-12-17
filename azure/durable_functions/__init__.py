"""Base module for the Python Durable functions.

Exposes the different API components intended for public consumption
"""
from .orchestrator import Orchestrator
from .entity import Entity
from .models.utils.entity_utils import EntityId
from .models.DurableOrchestrationClient import DurableOrchestrationClient
from .models.DurableOrchestrationContext import DurableOrchestrationContext
from .models.DurableEntityContext import DurableEntityContext
from .models.RetryOptions import RetryOptions
from .models.TokenSource import ManagedIdentityTokenSource
import json
from pathlib import Path
import sys
import os


def validate_extension_bundles():
    # No need to validate if we're running tests
    if "pytest" in sys.modules:
        return

    host_path = "host.json"
    bundles_key = "extensionBundle"
    version_key = "version"
    host_file = Path(host_path)

    if not host_file.exists():
        # If it doesn't exist, we ignore it
        return

    with open(host_path) as f:
        host_settings = json.loads(f.read())
        try:
            version_range = host_settings[bundles_key][version_key]
        except Exception:
            # If bundle info is not  available, we ignore it.
            # It's possible the user is using a manual extension install
            return
        if version_range == "[1.*, 2.0.0)":
            message = "Bundles V1 is deprecated. Please update to Bundles V2 in your `host.json`."\
                " You can set extensionBundles version to be: [2.*, 3.0.0)"
            raise Exception(message)


validate_extension_bundles()

__all__ = [
    'Orchestrator',
    'Entity',
    'EntityId',
    'DurableOrchestrationClient',
    'DurableEntityContext',
    'DurableOrchestrationContext',
    'ManagedIdentityTokenSource',
    'RetryOptions'
]
