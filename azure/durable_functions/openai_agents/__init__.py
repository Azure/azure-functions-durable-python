"""OpenAI Agents integration for Azure Durable Functions.

This module provides decorators and utilities to integrate OpenAI Agents
with Azure Durable Functions orchestration patterns.
"""

from .context import DurableAIAgentContext

__all__ = [
    'DurableAIAgentContext',
]
