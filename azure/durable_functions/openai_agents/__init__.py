"""OpenAI Agents integration for Azure Durable Functions.

This module provides decorators and utilities to integrate OpenAI Agents
with Azure Durable Functions orchestration patterns.
"""

from .decorators import durable_openai_agent_orchestrator
from .context import DurableAIAgentContext

__all__ = [
    'durable_openai_agent_orchestrator',
    'DurableAIAgentContext', 
]