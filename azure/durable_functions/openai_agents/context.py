#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
from typing import Any, Callable, Optional, TYPE_CHECKING, Union

from azure.durable_functions.models.DurableOrchestrationContext import (
    DurableOrchestrationContext,
)
from azure.durable_functions.models.RetryOptions import RetryOptions

from agents import RunContextWrapper, Tool
from agents.function_schema import function_schema
from agents.tool import FunctionTool

from azure.durable_functions.models.Task import TaskBase
from .task_tracker import TaskTracker


if TYPE_CHECKING:
    # At type-check time we want all members / signatures for IDE & linters.
    _BaseDurableContext = DurableOrchestrationContext
else:
    class _BaseDurableContext:  # lightweight runtime stub
        """Runtime stub base class for delegation; real context is wrapped.

        At runtime we avoid inheriting from DurableOrchestrationContext so that
        attribute lookups for its members are delegated via __getattr__ to the
        wrapped ``_context`` instance.
        """

        __slots__ = ()


class DurableAIAgentContext(_BaseDurableContext):
    """Context for AI agents running in Azure Durable Functions orchestration.

    Design
    ------
    * Static analysis / IDEs: Appears to subclass ``DurableOrchestrationContext`` so
      you get autocompletion and type hints (under TYPE_CHECKING branch).
    * Runtime: Inherits from a trivial stub. All durable orchestration operations
      are delegated to the real ``DurableOrchestrationContext`` instance provided
      as ``context`` and stored in ``_context``.

    Consequences
    ------------
    * ``isinstance(DurableAIAgentContext, DurableOrchestrationContext)`` is **False** at
      runtime (expected).
    * Delegation via ``__getattr__`` works for every member of the real context.
    * No reliance on internal initialization side-effects of the durable SDK.
    """

    def __init__(
        self,
        context: DurableOrchestrationContext,
        task_tracker: TaskTracker,
        model_retry_options: Optional[RetryOptions],
    ):
        self._context = context
        self._task_tracker = task_tracker
        self._model_retry_options = model_retry_options

    def call_activity(
        self, name: Union[str, Callable], input_: Optional[Any] = None
    ) -> TaskBase:
        """Schedule an activity for execution.

        Parameters
        ----------
        name: str | Callable
            Either the name of the activity function to call, as a string or,
            in the Python V2 programming model, the activity function itself.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or fails.
        """
        task = self._context.call_activity(name, input_)
        self._task_tracker.record_activity_call()
        return task

    def call_activity_with_retry(
        self,
        name: Union[str, Callable],
        retry_options: RetryOptions,
        input_: Optional[Any] = None,
    ) -> TaskBase:
        """Schedule an activity for execution with retry options.

        Parameters
        ----------
        name: str | Callable
            Either the name of the activity function to call, as a string or,
            in the Python V2 programming model, the activity function itself.
        retry_options: RetryOptions
            The retry options for the activity function.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or
            fails completely.
        """
        task = self._context.call_activity_with_retry(name, retry_options, input_)
        self._task_tracker.record_activity_call()
        return task

    def create_activity_tool(
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
        if activity_func._function is None:
            raise ValueError("The provided function is not a valid Azure Function.")

        if (activity_func._function._trigger is not None
                and activity_func._function._trigger.activity is not None):
            activity_name = activity_func._function._trigger.activity
        else:
            activity_name = activity_func._function._name

        input_name = None
        if (activity_func._function._trigger is not None
                and hasattr(activity_func._function._trigger, 'name')):
            input_name = activity_func._function._trigger.name

        async def run_activity(ctx: RunContextWrapper[Any], input: str) -> Any:
            # Parse JSON input and extract the named value if input_name is specified
            activity_input = input
            if input_name:
                try:
                    parsed_input = json.loads(input)
                    if isinstance(parsed_input, dict) and input_name in parsed_input:
                        activity_input = parsed_input[input_name]
                    # If parsing fails or the named parameter is not found, pass the original input
                except (json.JSONDecodeError, TypeError):
                    pass

            if retry_options:
                result = self._task_tracker.get_activity_call_result_with_retry(
                    activity_name, retry_options, activity_input
                )
            else:
                result = self._task_tracker.get_activity_call_result(activity_name, activity_input)
            return result

        schema = function_schema(
            func=activity_func._function._func,
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

    def __getattr__(self, name):
        """Delegate missing attributes to the underlying DurableOrchestrationContext."""
        try:
            return getattr(self._context, name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __dir__(self):
        """Improve introspection and tab-completion by including delegated attributes."""
        return sorted(set(dir(type(self)) + list(self.__dict__) + dir(self._context)))
