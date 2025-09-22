#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import inspect
from typing import Any

from azure.durable_functions.models.DurableOrchestrationContext import (
    DurableOrchestrationContext,
)
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType
from azure.durable_functions.models.RetryOptions import RetryOptions

from .exceptions import YieldException


class TaskTracker:
    """Tracks activity calls and handles task result processing for durable AI agents."""

    def __init__(self, context: DurableOrchestrationContext):
        self._context = context
        self._activities_called = 0
        self._tasks_to_yield = []

    def _get_activity_result_or_raise(self, task):
        """Return the activity result if available; otherwise raise ``YieldException`` to defer.

        The first time an activity is scheduled its result won't yet exist in the
        orchestration history, so we raise ``YieldException`` with the task so the
        orchestrator can yield it. On replay, once the corresponding TASK_COMPLETED
        history event is present, we capture the result and queue the task for a
        later yield (to preserve ordering) while returning the deserialized value.
        """
        self.record_activity_call()

        histories = self._context.histories
        completed_tasks = [
            entry for entry in histories
            if entry.event_type == HistoryEventType.TASK_COMPLETED
        ]
        if len(completed_tasks) < self._activities_called:
            # Result not yet available in history -> raise to signal a yield now
            raise YieldException(task)
        # Result exists (replay). Queue task to be yielded after returning value.
        #
        # We cannot just yield it now because this method can be called from
        # deeply nested code paths that we don't control (such as the
        # OpenAI Agents SDK internals), and yielding here would lead to
        # unintended behavior. Instead, we queue the task to be yielded
        # later and return the result recorded in the history, so the
        # code invoking this method can continue executing normally.
        self._tasks_to_yield.append(task)

        result_json = completed_tasks[self._activities_called - 1].Result
        result = json.loads(result_json)
        return result

    def get_activity_call_result(self, activity_name, input: Any):
        """Call an activity and return its result or raise ``YieldException`` if pending."""
        task = self._context.call_activity(activity_name, input)
        return self._get_activity_result_or_raise(task)

    def get_activity_call_result_with_retry(
        self, activity_name, retry_options: RetryOptions, input: Any
    ):
        """Call an activity with retry and return its result or raise YieldException if pending."""
        task = self._context.call_activity_with_retry(activity_name, retry_options, input)
        return self._get_activity_result_or_raise(task)

    def record_activity_call(self):
        """Record that an activity was called."""
        self._activities_called += 1

    def _yield_and_clear_tasks(self):
        """Yield all accumulated tasks and clear the tasks list."""
        for task in self._tasks_to_yield:
            yield task
        self._tasks_to_yield.clear()

    def execute_orchestrator_function(self, func):
        """Execute the orchestrator function with comprehensive task and exception handling.

        The orchestrator function can exhibit any combination of the following behaviors:
        - Execute regular code and return a value or raise an exception
        - Invoke get_activity_call_result or get_activity_call_result_with_retry, which leads to
          either interrupting the orchestrator function immediately (because of YieldException),
          or queueing the task for later yielding while continuing execution
        - Invoke DurableAIAgentContext.call_activity or call_activity_with_retry (which must lead
          to corresponding record_activity_call invocations)
        - Yield tasks (typically produced by DurableAIAgentContext methods like call_activity,
          wait_for_external_event, etc.), which may or may not interrupt orchestrator function
          execution
        - Mix all of the above in any combination

        This method converts both YieldException and regular yields into a sequence of yields
        preserving the order, while also capturing return values through the generator protocol.
        For example, if the orchestrator function yields task A, then queues task B for yielding,
        then raises YieldException wrapping task C, this method makes sure that the resulting
        sequence of yields is: (A, B, C).

        Args
        ----
            func: The orchestrator function to execute (generator or regular function)

        Yields
        ------
            Tasks yielded by the orchestrator function and tasks wrapped in YieldException

        Returns
        -------
            The return value from the orchestrator function
        """
        if inspect.isgeneratorfunction(func):
            gen = iter(func())
            try:
                # prime the subiterator
                value = next(gen)
                yield from self._yield_and_clear_tasks()
                while True:
                    try:
                        # send whatever was sent into us down to the subgenerator
                        yield from self._yield_and_clear_tasks()
                        sent = yield value
                    except GeneratorExit:
                        # ensure the subgenerator is closed
                        if hasattr(gen, "close"):
                            gen.close()
                        raise
                    except BaseException as exc:
                        # forward thrown exceptions if possible
                        if hasattr(gen, "throw"):
                            value = gen.throw(type(exc), exc, exc.__traceback__)
                        else:
                            raise
                    else:
                        # normal path: forward .send (or .__next__)
                        if hasattr(gen, "send"):
                            value = gen.send(sent)
                        else:
                            value = next(gen)
            except StopIteration as e:
                yield from self._yield_and_clear_tasks()
                return TaskTracker._durable_serializer(e.value)
            except YieldException as e:
                yield from self._yield_and_clear_tasks()
                yield e.task
        else:
            try:
                result = func()
                return TaskTracker._durable_serializer(result)
            except YieldException as e:
                yield from self._yield_and_clear_tasks()
                yield e.task
            finally:
                yield from self._yield_and_clear_tasks()

    @staticmethod
    def _durable_serializer(obj: Any) -> str:
        # Strings are already "serialized"
        if type(obj) is str:
            return obj

        # Serialize "Durable" and OpenAI models, and typed dictionaries
        if callable(getattr(obj, "to_json", None)):
            return obj.to_json()

        # Serialize Pydantic models
        if callable(getattr(obj, "model_dump_json", None)):
            return obj.model_dump_json()

        # Fallback to default JSON serialization
        return json.dumps(obj)
