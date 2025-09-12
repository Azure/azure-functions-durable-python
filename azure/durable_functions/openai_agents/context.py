from typing import Any, Callable, Optional

from azure.durable_functions.models.DurableOrchestrationContext import (
    DurableOrchestrationContext,
)
from azure.durable_functions.models.RetryOptions import RetryOptions

from agents import RunContextWrapper, Tool
from agents.function_schema import function_schema
from agents.tool import FunctionTool
from .task_tracker import TaskTracker


class DurableAIAgentContext:
    """Context for AI agents running in Azure Durable Functions orchestration."""

    def __init__(
        self,
        context: DurableOrchestrationContext,
        task_tracker: TaskTracker,
        model_retry_options: Optional[RetryOptions],
    ):
        self._context = context
        self._task_tracker = task_tracker
        self._model_retry_options = model_retry_options

    def call_activity(self, activity_name, input: str):
        """Call an activity function and record the activity call."""
        task = self._context.call_activity(activity_name, input)
        self._task_tracker.record_activity_call()
        return task

    def call_activity_with_retry(
        self, activity_name, retry_options: RetryOptions, input: str = None
    ):
        """Call an activity function with retry options and record the activity call."""
        task = self._context.call_activity_with_retry(activity_name, retry_options, input)
        self._task_tracker.record_activity_call()
        return task

    def set_custom_status(self, status: str):
        """Set custom status for the orchestration."""
        self._context.set_custom_status(status)

    def wait_for_external_event(self, event_name: str):
        """Wait for an external event in the orchestration."""
        return self._context.wait_for_external_event(event_name)

    def activity_as_tool(
        self,
        activity_func: Callable,
        *,
        description: Optional[str] = None,
        retry_options: Optional[RetryOptions] = RetryOptions(
            first_retry_interval_in_milliseconds=2000, max_number_of_attempts=5
        ),
    ) -> Tool:
        """Convert an Azure Durable Functions activity to an OpenAI Agents SDK Tool.

        Args
        ----
            activity_func: The Azure Functions activity function to convert
            description: Optional description override for the tool
            retry_options: The retry options for the activity function

        Returns
        -------
            Tool: An OpenAI Agents SDK Tool object

        """
        activity_name = activity_func._function._name

        async def run_activity(ctx: RunContextWrapper[Any], input: str) -> Any:
            if retry_options:
                result = self._task_tracker.get_activity_call_result_with_retry(
                    activity_name, retry_options, input
                )
            else:
                result = self._task_tracker.get_activity_call_result(activity_name, input)
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
