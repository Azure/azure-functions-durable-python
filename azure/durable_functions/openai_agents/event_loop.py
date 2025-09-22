#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import asyncio


def ensure_event_loop():
    """Ensure an event loop is available for sync execution context.

    This is necessary when calling Runner.run_sync from Azure Functions
    Durable orchestrators, which run in a synchronous context but need
    an event loop for internal async operations.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
