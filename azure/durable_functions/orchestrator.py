"""Durable Orchestrator.

Responsible for orchestrating the execution of the user defined generator
function.
"""
from typing import Callable, Iterator, Any, Generator

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
                 activity_func: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]):
        """Create a new orchestrator for the user defined generator.

        Responsible for orchestrating the execution of the user defined
        generator function.
        :param activity_func: Generator function to orchestrate.
        """
        self.fn: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]] = activity_func

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
        if not isinstance(fn_output, Iterator):
            orchestration_state = OrchestratorState(
                is_done=True,
                output=fn_output,
                actions=self.durable_context.actions,
                custom_status=self.durable_context.custom_status)

        else:
            self.generator = fn_output
            try:
                generation_state = self._generate_next(None)

                while not suspended:
                    self._add_to_actions(generation_state)

                    if should_suspend(generation_state):

                        # The `is_done` field should be False here unless
                        # `continue_as_new` was called. Therefore,
                        # `will_continue_as_new` essentially "tracks"
                        # whether or not the orchestration is done.
                        orchestration_state = OrchestratorState(
                            is_done=self.durable_context.will_continue_as_new,
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

                    self._update_timestamp()
                    self.durable_context._is_replaying = generation_state._is_played
                    generation_state = self._generate_next(generation_state)

            except StopIteration as sie:
                orchestration_state = OrchestratorState(
                    is_done=True,
                    output=sie.value,
                    actions=self.durable_context.actions,
                    custom_status=self.durable_context.custom_status)
            except Exception as e:
                exception_str = str(e)
                orchestration_state = OrchestratorState(
                    is_done=False,
                    output=None,  # Should have no output, after generation range
                    actions=self.durable_context.actions,
                    error=exception_str,
                    custom_status=self.durable_context.custom_status)

                # Create formatted error, using out-of-proc error schema
                error_label = "\n\n$OutOfProcData$:"
                state_str = orchestration_state.to_json_string()
                formatted_error = f"{exception_str}{error_label}{state_str}"

                # Raise exception, re-set stack to original location
                raise Exception(formatted_error) from e

        # No output if continue_as_new was called
        if self.durable_context.will_continue_as_new:
            orchestration_state._output = None

        return orchestration_state.to_json_string()

    def _generate_next(self, partial_result):
        if partial_result is not None:
            gen_result = self.generator.send(partial_result.result)
        else:
            gen_result = self.generator.send(None)

        return gen_result

    def _add_to_actions(self, generation_state):
        # Do not add new tasks to action if continue_as_new was called
        if self.durable_context.will_continue_as_new:
            return
        if (isinstance(generation_state, Task)
                and hasattr(generation_state, "action")):
            self.durable_context.actions.append([generation_state.action])
        elif (isinstance(generation_state, TaskSet)
              and hasattr(generation_state, "actions")):
            self.durable_context.actions.append(generation_state.actions)

    def _update_timestamp(self):
        last_timestamp = self.durable_context.decision_started_event.timestamp
        decision_started_events = [e_ for e_ in self.durable_context.histories
                                   if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED
                                   and e_.timestamp > last_timestamp]
        if len(decision_started_events) != 0:
            self.durable_context.decision_started_event = decision_started_events[0]
            self.durable_context.current_utc_datetime = \
                self.durable_context.decision_started_event.timestamp

    @classmethod
    def create(cls, fn: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]) \
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
