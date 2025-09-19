#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
from dataclasses import replace
from typing import Any, Union

from agents import (
    Agent,
    RunConfig,
    RunResult,
    RunResultStreaming,
    TContext,
    TResponseInputItem,
)
from agents.run import DEFAULT_AGENT_RUNNER, DEFAULT_MAX_TURNS, AgentRunner
from pydantic_core import to_json

from .context import DurableAIAgentContext
from .model_invocation_activity import DurableActivityModel


class DurableOpenAIRunner:
    """Runner for OpenAI agents using Durable Functions orchestration."""

    def __init__(self, context: DurableAIAgentContext, activity_name: str) -> None:
        self._runner = DEFAULT_AGENT_RUNNER or AgentRunner()
        self._context = context
        self._activity_name = activity_name

    def _prepare_run_config(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> tuple[Union[str, list[TResponseInputItem]], RunConfig, dict[str, Any]]:
        """Prepare and validate the run configuration and parameters for agent execution."""
        # Avoid https://github.com/pydantic/pydantic/issues/9541
        normalized_input = json.loads(to_json(input))

        run_config = kwargs.get("run_config") or RunConfig()

        model_name = run_config.model or starting_agent.model
        if model_name and not isinstance(model_name, str):
            raise ValueError(
                "For agent execution in Durable Functions, model name in run_config or "
                "starting_agent must be a string."
            )

        updated_run_config = replace(
            run_config,
            model=DurableActivityModel(
                model_name=model_name,
                task_tracker=self._context._task_tracker,
                retry_options=self._context._model_retry_options,
                activity_name=self._activity_name,
            ),
        )

        run_params = {
            "context": kwargs.get("context"),
            "max_turns": kwargs.get("max_turns", DEFAULT_MAX_TURNS),
            "hooks": kwargs.get("hooks"),
            "previous_response_id": kwargs.get("previous_response_id"),
            "session": kwargs.get("session"),
        }

        return normalized_input, updated_run_config, run_params

    def run_sync(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResult:
        """Run an agent synchronously with the given input and configuration."""
        normalized_input, updated_run_config, run_params = self._prepare_run_config(
            starting_agent, input, **kwargs
        )

        return self._runner.run_sync(
            starting_agent=starting_agent,
            input=normalized_input,
            run_config=updated_run_config,
            **run_params,
        )

    def run(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResult:
        """Run an agent asynchronously. Not supported in Durable Functions."""
        raise RuntimeError("Durable Functions do not support asynchronous runs.")

    def run_streamed(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResultStreaming:
        """Run an agent with streaming. Not supported in Durable Functions."""
        raise RuntimeError("Durable Functions do not support streaming.")
