import json
import logging
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
from .model_invocation_activity import _DurableModelStub

logger = logging.getLogger(__name__)


class DurableOpenAIRunner:
    def __init__(self, context: DurableAIAgentContext) -> None:
        self._runner = DEFAULT_AGENT_RUNNER or AgentRunner()
        self.context = context

    def run_sync(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResult:
        # workaround for https://github.com/pydantic/pydantic/issues/9541
        # ValidatorIterator returned
        input_json = to_json(input)
        input = json.loads(input_json)

        context = kwargs.get("context")
        max_turns = kwargs.get("max_turns", DEFAULT_MAX_TURNS)
        hooks = kwargs.get("hooks")
        run_config = kwargs.get("run_config")
        previous_response_id = kwargs.get("previous_response_id")
        session = kwargs.get("session")

        if run_config is None:
            run_config = RunConfig()

        model_name = run_config.model or starting_agent.model
        if model_name is not None and not isinstance(model_name, str):
            raise ValueError(
                "Durable Functions require a model name to be a string in the run config and/or agent."
            )
        
        updated_run_config = replace(
            run_config,
            model = _DurableModelStub(
                model_name = model_name,
                context = self.context,
            ),
        )

        return self._runner.run_sync(
            starting_agent=starting_agent,
            input=input,
            context=context,
            max_turns=max_turns,
            hooks=hooks,
            run_config=updated_run_config,
            previous_response_id=previous_response_id,
            session=session,
        )

    def run(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResult:
        raise RuntimeError("Durable Functions do not support asynchronous runs.")

    def run_streamed(
        self,
        starting_agent: Agent[TContext],
        input: Union[str, list[TResponseInputItem]],
        **kwargs: Any,
    ) -> RunResultStreaming:
        raise RuntimeError("Durable Functions do not support streaming.")