import logging
import traceback
from typing import Callable, Iterator, Any

from dateutil.parser import parse as dt_parse

from .interfaces import IFunctionContext
from .models import (
    DurableOrchestrationContext,
    Task,
    TaskSet,
    OrchestratorState)
from .models.history import HistoryEventType
from .tasks import should_suspend


class Orchestrator:
    def __init__(self,
                 activity_func: Callable[[IFunctionContext], Iterator[Any]]):
        self.fn: Callable[[IFunctionContext], Iterator[Any]] = activity_func
        self.customStatus: Any = None

    # noinspection PyAttributeOutsideInit
    def handle(self, context_string: str):
        self.durable_context = DurableOrchestrationContext(context_string)
        activity_context = IFunctionContext(df=self.durable_context)

        self.generator = self.fn(activity_context)

        try:
            starting_state = self._generate_next(None)

            orchestration_state = self._get_orchestration_state(starting_state)
        except StopIteration as sie:
            logging.warning(f"!!!Generator Termination StopIteration {sie}")
            orchestration_state = OrchestratorState(
                isDone=True,
                output=sie.value,
                actions=self.durable_context.actions,
                customStatus=self.customStatus)
        except Exception as e:
            e_string = traceback.format_exc()
            logging.warning(f"!!!Generator Termination Exception {e_string}")
            orchestration_state = OrchestratorState(
                isDone=False,
                output=None,  # Should have no output, after generation range
                actions=self.durable_context.actions,
                error=str(e),
                customStatus=self.customStatus)

        return orchestration_state.to_json_string()

    def _generate_next(self, partial_result):
        if partial_result is not None:
            gen_result = self.generator.send(partial_result.result)
        else:
            gen_result = self.generator.send(None)
        return gen_result

    def _get_orchestration_state(self, generation_state):
        logging.warning(f"!!!actions {self.durable_context.actions}")
        logging.warning(f"!!!Generator Execution {generation_state}")

        self._add_to_actions(generation_state)

        if should_suspend(generation_state):
            logging.warning(f"!!!Generator Suspended")
            return OrchestratorState(
                isDone=False,
                output=None,
                actions=self.durable_context.actions,
                customStatus=self.customStatus)

        if (isinstance(generation_state, Task)
            or isinstance(generation_state, TaskSet)) and (
                generation_state.isFaulted):
            return self._get_orchestration_state(self.generator.throw(generation_state.exception))

        self._reset_timestamp()

        logging.warning(f"!!!Generator Execution {generation_state}")
        return self._get_orchestration_state(self._generate_next(generation_state))

    def _add_to_actions(self, generation_state):
        if (isinstance(generation_state, Task)
                and hasattr(generation_state, "action")):
            self.durable_context.actions.append([generation_state.action])
        elif (isinstance(generation_state, TaskSet)
              and hasattr(generation_state, "actions")):
            self.durable_context.actions.append(generation_state.actions)

    def _reset_timestamp(self):
        last_timestamp = dt_parse(self.durable_context.decision_started_event.Timestamp)
        decision_started_events = list(
            filter(lambda e_: (
                    e_["EventType"] == HistoryEventType.OrchestratorStarted
                    and dt_parse(e_["Timestamp"]) > last_timestamp),
                   self.durable_context.histories))
        if len(decision_started_events) == 0:
            self.durable_context.currentUtcDateTime = None
        else:
            self.durable_context.decision_started_event = decision_started_events[0]
            self.durable_context.currentUtcDateTime = dt_parse(self.durable_context.decision_started_event.Timestamp)

    @classmethod
    def create(cls, fn):
        logging.warning("!!!Calling orchestrator create")
        return lambda context: Orchestrator(fn).handle(context)
