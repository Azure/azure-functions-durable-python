import json
from typing import Any, Callable, Optional

from azure.durable_functions.models.DurableOrchestrationContext import (
    DurableOrchestrationContext,
)

from agents import RunContextWrapper, Tool
from agents.function_schema import function_schema
from agents.tool import FunctionTool
from .exceptions import YieldException


class DurableAIAgentContext:
    """Context for AI agents running in Azure Durable Functions orchestration."""

    def __init__(self, context: DurableOrchestrationContext):
        self._context = context
        self._activities_called = 0
        self._tasks_to_yield = []

    def _get_activity_call_result(self, activity_name, input: str):
        task = self._context.call_activity(activity_name, input)

        self._activities_called += 1

        histories = self._context.histories
        completed_tasks = [entry for entry in histories if entry.event_type == 5]
        if len(completed_tasks) < self._activities_called:
            # yield immediately
            raise YieldException(task)
        else:
            # yield later
            self._tasks_to_yield.append(task)

            result_json = completed_tasks[self._activities_called - 1].Result
            result = json.loads(result_json)
            return result

    def call_activity(self, activity_name, input: str):
        """Call an activity function and increment the activity counter."""
        task = self._context.call_activity(activity_name, input)
        self._activities_called += 1
        return task

    def set_custom_status(self, status: str):
        """Set custom status for the orchestration."""
        self._context.set_custom_status(status)

    def wait_for_external_event(self, event_name: str):
        """Wait for an external event in the orchestration."""
        return self._context.wait_for_external_event(event_name)

    def _yield_and_clear_tasks(self):
        """Yield all accumulated tasks and clear the tasks list."""
        for task in self._tasks_to_yield:
            yield task
        self._tasks_to_yield.clear()

    def activity_as_tool(
        self,
        activity_func: Callable,
        *,
        description: Optional[str] = None,
    ) -> Tool:
        """Convert an Azure Durable Functions activity to an OpenAI Agents SDK Tool.

        Args
        ----
            activity_func: The Azure Functions activity function to convert
            description: Optional description override for the tool

        Returns
        -------
            Tool: An OpenAI Agents SDK Tool object

        """
        activity_name = activity_func._function._name

        async def run_activity(ctx: RunContextWrapper[Any], input: str) -> Any:
            result = self._get_activity_call_result(activity_name, input)
            return result

        schema = function_schema(
            func=activity_func._function._func,
            name_override=activity_name,
            docstring_style=None,
            description_override=description,
            use_docstring_info=True,
            strict_json_schema=True,
        )

        return FunctionTool(
            name=schema.name,
            description=schema.description or "",
            params_json_schema=schema.params_json_schema,
            on_invoke_tool=run_activity,
            strict_json_schema=True,
        )
