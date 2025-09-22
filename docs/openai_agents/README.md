# Durable OpenAI Agents

Build production-ready AI agents with automatic state persistence and failure recovery.

## Overview

The Durable OpenAI Agents integration combines the familiar OpenAI Agents SDK with Azure Durable Functions to create reliable, stateful AI agents that can survive any failure and continue exactly where they stopped.

## Key Benefits

- **Enhanced Agent Resilience**: Built-in retry mechanisms for LLM calls and tool executions
- **Multi-Agent Orchestration Reliability**: Individual agent failures don't crash entire workflows
- **Built-in Observability**: Monitor agent progress through the Durable Task Scheduler dashboard
- **Familiar Developer Experience**: Keep using the OpenAI Agents SDK with minimal code changes
- **Distributed Compute and Scalability**: Agent workflows automatically scale across multiple compute instances

## Documentation

- [Getting Started](getting-started.md) - Setup and your first durable agent
- [Reference](reference.md) - Complete reference documentation

> Compatibility note: The Durable OpenAI Agents integration has been validated with the OpenAI packages pinned in the sample application's `samples-v2/openai_agents/requirements.txt` (currently `openai==1.107.3` and `openai-agents==0.3.0`). Because the OpenAI packages release frequently and may introduce breaking API or behavioral changes, we recommend pinning to those versions if you face unexpected issues before reporting a bug.
