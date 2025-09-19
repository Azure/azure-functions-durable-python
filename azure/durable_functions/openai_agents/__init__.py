#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
"""OpenAI Agents integration for Durable Functions.

This module provides decorators and utilities to integrate OpenAI Agents
with Durable Functions orchestration patterns.
"""

from .context import DurableAIAgentContext

__all__ = [
    'DurableAIAgentContext',
]
