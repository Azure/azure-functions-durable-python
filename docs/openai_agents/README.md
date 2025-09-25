# OpenAI Agent SDK Integration with Azure Durable Functions (Preview)

Build production-ready AI agents with automatic state persistence and failure recovery.

## Overview

The OpenAI Agent SDK Integration with Azure Durable Functions (Preview) integration combines the familiar OpenAI Agents SDK with Azure Durable Functions to create reliable, stateful AI agents that can survive any failure and continue exactly where they stopped.

## Key Benefits

- **Enhanced Agent Resilience**: Built-in retry mechanisms for LLM calls and tool executions
- **Multi-Agent Orchestration Reliability**: Individual agent failures don't crash entire workflows
- **Built-in Observability**: Monitor agent progress through the Durable Task Scheduler dashboard
- **Familiar Developer Experience**: Keep using the OpenAI Agents SDK with minimal code changes
- **Distributed Compute and Scalability**: Agent workflows automatically scale across multiple compute instances

## Documentation

- [Getting Started](getting-started.md) - Setup and your first durable agent
- [Reference](reference.md) - Complete reference documentation

> Dependency & compatibility: The `azure-functions-durable` package does NOT declare `openai` or `openai-agents` as dependencies. If you need the OpenAI Agent SDK Integration with Azure Durable Functions(Preview), explicitly add `openai` and `openai-agents` to your `requirements.txt` (see `samples-v2/openai_agents/requirements.txt`). This integration is validated with the versions currently pinned there (`openai==1.107.3`, `openai-agents==0.3.0`). Because the OpenAI ecosystem changes rapidly, if you encounter issues, first pin to these versions to rule out a version mismatch before filing an issue.
