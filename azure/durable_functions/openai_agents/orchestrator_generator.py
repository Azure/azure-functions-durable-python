#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from functools import partial
from typing import Optional
from agents import ModelProvider, ModelResponse
from agents.run import set_default_agent_runner
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.RetryOptions import RetryOptions
from .model_invocation_activity import DurableModelActivityInput, ModelInvoker
from .task_tracker import TaskTracker
from .runner import DurableOpenAIRunner
from .context import DurableAIAgentContext
from .event_loop import ensure_event_loop
from .usage_telemetry import UsageTelemetry


async def durable_openai_agent_activity(input: str, model_provider: ModelProvider) -> str:
    """Activity logic that handles OpenAI model invocations."""
    activity_input = DurableModelActivityInput.from_json(input)

    model_invoker = ModelInvoker(model_provider=model_provider)
    result = await model_invoker.invoke_model_activity(activity_input)

    # Use safe/public Pydantic API when possible. Prefer model_dump_json if result is a BaseModel
    # Otherwise handle common types (str/bytes/dict/list) and fall back to json.dumps.
    import json as _json

    if hasattr(result, "model_dump_json"):
        # Pydantic v2 BaseModel
        json_str = result.model_dump_json()
    else:
        if isinstance(result, bytes):
            json_str = result.decode()
        elif isinstance(result, str):
            json_str = result
        else:
            # Try the internal serializer as a last resort, but fall back to json.dumps
            try:
                json_bytes = ModelResponse.__pydantic_serializer__.to_json(result)
                json_str = json_bytes.decode()
            except Exception:
                json_str = _json.dumps(result)

    return json_str


def durable_openai_agent_orchestrator_generator(
        func,
        durable_orchestration_context: DurableOrchestrationContext,
        model_retry_options: Optional[RetryOptions],
        activity_name: str,
):
    """Adapts the synchronous OpenAI Agents function to an Durable orchestrator generator."""
    # Log versions the first time this generator is invoked
    UsageTelemetry.log_usage_once()

    ensure_event_loop()
    task_tracker = TaskTracker(durable_orchestration_context)
    durable_ai_agent_context = DurableAIAgentContext(
        durable_orchestration_context, task_tracker, model_retry_options
    )
    durable_openai_runner = DurableOpenAIRunner(
        context=durable_ai_agent_context, activity_name=activity_name)
    set_default_agent_runner(durable_openai_runner)

    func_with_context = partial(func, durable_ai_agent_context)
    return task_tracker.execute_orchestrator_function(func_with_context)
