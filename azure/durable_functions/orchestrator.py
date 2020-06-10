"""Durable Orchestrator.

Responsible for orchestrating the execution of the user defined generator
function.
"""
from typing import Callable, Iterator, Any

from .models import (
    DurableOrchestrationContext,
    Task,
    TaskSet,
    OrchestratorState)
from .models.history import HistoryEventType
from .tasks import should_suspend

import azure.functions as func


class Orchestrator:
    """Durable Orchestration Class.

    Responsible for orchestrating the execution of the user defined generator
    function.
    """

    def __init__(self,
                 activity_func: Callable[[DurableOrchestrationContext], Iterator[Any]]):
        """Create a new orchestrator for the user defined generator.

        Responsible for orchestrating the execution of the user defined
        generator function.
        :param activity_func: Generator function to orchestrate.
        """
        self.fn: Callable[[DurableOrchestrationContext], Iterator[Any]] = activity_func

    def handle(self, context: DurableOrchestrationContext):
        """Handle the orchestration of the user defined generator function.

        Called each time the durable extension executes an activity and needs
        the client to handle the result.

        :param context: the context of what has been executed by
        the durable extension.
        :return: the resulting orchestration state, with instructions back to
        the durable extension.
        """
        self.durable_context = context
        self.generator = None
        suspended = False

        fn_output = self.fn(self.durable_context)
        # If `fn_output` is not an Iterator, then the orchestrator
        # function does not make use of its context parameter. If so,
        # `fn_output` is the return value instead of a generator
        if isinstance(fn_output, Iterator):
            self.generator = fn_output

        else:
            orchestration_state = OrchestratorState(
                is_done=True,
                output=fn_output,
                actions=self.durable_context.actions,
                custom_status=self.durable_context.custom_status)
            return orchestration_state.to_json_string()
        try:
            generation_state = self._generate_next(None)

            while not suspended:
                self._add_to_actions(generation_state)

                if should_suspend(generation_state):
                    orchestration_state = OrchestratorState(
                        is_done=False,
                        output=None,
                        actions=self.durable_context.actions,
                        custom_status=self.durable_context.custom_status)
                    suspended = True
                    continue

                if (isinstance(generation_state, Task)
                    or isinstance(generation_state, TaskSet)) and (
                        generation_state.is_faulted):
                    generation_state = self.generator.throw(
                        generation_state.exception)
                    continue

                self._reset_timestamp()
                generation_state = self._generate_next(generation_state)

        except StopIteration as sie:
            orchestration_state = OrchestratorState(
                is_done=True,
                output=sie.value,
                actions=self.durable_context.actions,
                custom_status=self.durable_context.custom_status)
        except Exception as e:
            orchestration_state = OrchestratorState(
                is_done=False,
                output=None,  # Should have no output, after generation range
                actions=self.durable_context.actions,
                error=str(e),
                custom_status=self.durable_context.custom_status)

        return orchestration_state.to_json_string()

    def _generate_next(self, partial_result):
        if partial_result is not None:
            gen_result = self.generator.send(partial_result.result)
        else:
            gen_result = self.generator.send(None)
        return gen_result

    def _add_to_actions(self, generation_state):
        if (isinstance(generation_state, Task)
                and hasattr(generation_state, "action")):
            self.durable_context.actions.append([generation_state.action])
        elif (isinstance(generation_state, TaskSet)
              and hasattr(generation_state, "actions")):
            self.durable_context.actions.append(generation_state.actions)

    def _reset_timestamp(self):
        last_timestamp = self.durable_context.decision_started_event.timestamp
        decision_started_events = [e_ for e_ in self.durable_context.histories
                                   if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED
                                   and e_.timestamp > last_timestamp]
        if len(decision_started_events) == 0:
            self.durable_context.current_utc_datetime = None
        else:
            self.durable_context.decision_started_event = \
                decision_started_events[0]
            self.durable_context.current_utc_datetime = \
                self.durable_context.decision_started_event.timestamp

    @classmethod
    def create(cls, fn: Callable[[DurableOrchestrationContext], Iterator[Any]]) \
            -> Callable[[Any], str]:
        """Create an instance of the orchestration class.

        Parameters
        ----------
        fn: Callable[[DurableOrchestrationContext], Iterator[Any]]
            Generator function that needs orchestration

        Returns
        -------
        Callable[[Any], str]
            Handle function of the newly created orchestration client
        """

        def handle(context: func.OrchestrationContext) -> str:
            context_body = getattr(context, "body", None)
            if context_body is None:
                context_body = context
            return Orchestrator(fn).handle(DurableOrchestrationContext.from_json(context_body))

        return handle
