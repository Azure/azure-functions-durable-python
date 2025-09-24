# Reference Documentation

Complete reference for the OpenAI Agents Integration for Reliability on Azure Functions (Preview) integration.

## Durable Orchestration

### @app.durable_openai_agent_orchestrator

Primary decorator enabling durable execution for agent invocations.

```python
from azure.durable_functions.openai_agents import durable_openai_agent_orchestrator

@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def my_agent_orchestrator(context):
    # Agent implementation
    pass
```

**Features**:
- Automatic state persistence for agent conversations
- Built-in retry mechanisms for LLM calls
- Tool call durability and replay protection
- Integration with Durable Functions monitoring using the Durable Task Scheduler

**Constraints**:
- Functions must be deterministic (identical outputs for identical inputs)
- No non-deterministic operations: `datetime.now()`, `random`, `uuid.uuid4()`
- See [Durable Functions Code Constraints](https://learn.microsoft.com/azure/azure-functions/durable/durable-functions-code-constraints?tabs=csharp)

### @app.orchestration_trigger

Azure Functions orchestration trigger decorator. Required with `@app.durable_openai_agent_orchestrator`.

```python
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def my_orchestrator(context):
    # ...
```

## Agent Execution

### Runner.run_sync()

Runner for agents in durable orchestration context.

```python
from agents import Agent, Runner

def my_orchestrator(context):
    agent = Agent(name="Assistant", instructions="Be helpful")
    result = Runner.run_sync(agent, "Hello world")
    return result.final_output
```

**Parameters**:
- `agent` (Agent): Agent instance to run
- `messages` (str | list): Input message(s)

**Returns**: Agent result object with `final_output` property

## Tools

### Durable Functions Activity Tools

Durable Function Activities that execute as durable tool invocations. **This is the recommended approach for most use cases** as it provides the strongest correctness guarantees. - **When in doubt - this is the safe choice**

```python
# 1. Define activity function
@app.activity_trigger(input_name="input_param")
async def my_activity(input_param):
    # External API calls, database operations, etc.
    return result

# 2. Use in orchestrator
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator
def my_orchestrator(context):
    agent = Agent(
        tools=[context.create_activity_tool(my_activity)]
    )
    # ...
```

**Components**:
- `@app.activity_trigger(input_name="param")`: Decorator for activity functions
- `context.create_activity_tool(activity_function)`: Creates tool from activity function

**Best For**: External API calls, database operations, file I/O, expensive computations, non-deterministic operations

### Open AI Function Tools

Simple, deterministic tools that execute within the orchestration context. **Recommended only as a performance optimization when you're certain the tool meets all deterministic requirements.**

```python
from agents import function_tool

@function_tool
def calculate(expression: str) -> str:
    """Calculate mathematical expressions."""
    return str(eval(expression))
```

**Requirements**:
- Must be deterministic (same input → same output)
- Should be fast-executing
- No external API calls (use activity tools instead)
- Input/output must be JSON serializable

**Best For**: Calculations, data transformations, validation logic, quick lookups

### Current Limitations

**MCP (Model Context Protocol)**: MCP tool support is not currently available. Use function tools or activity tools instead.

## Constraints

Orchestration functions must be deterministic and replay-safe:

- **Deterministic**: Same input always produces same output
- **Idempotent**: Safe to execute multiple times  
- **Side-effect free**: No external calls in orchestration logic

```python
# ✅ Good: Deterministic
def good_orchestrator(context):
    input_data = context.get_input()
    agent = high_priority_agent if input_data.get("priority") == "high" else standard_agent
    return Runner.run_sync(agent, input_data["content"])

# ❌ Bad: Non-deterministic
def bad_orchestrator(context):
    import random
    agent = agent_a if random.choice([True, False]) else agent_b  # Non-deterministic!
    return Runner.run_sync(agent, context.get_input())
```