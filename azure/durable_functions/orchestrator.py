import logging
import traceback
from typing import Callable, Iterator, Any, Union

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

    def handle(self, context_string: str):
        durable_context = DurableOrchestrationContext(context_string)
        activity_context = IFunctionContext(df=durable_context)

        gen = self.fn(activity_context)
        partial_result: Union[Task, TaskSet] = None

        try:
            if partial_result is not None:
                gen_result = gen.send(partial_result.result)
            else:
                gen_result = gen.send(None)

            while True:
                logging.warning(f"!!!actions {activity_context.df.actions}")
                logging.warning(f"!!!Generator Execution {gen_result}")

                partial_result = gen_result

                if (isinstance(partial_result, Task)
                        and hasattr(partial_result, "action")):
                    activity_context.df.actions.append([partial_result.action])
                elif (isinstance(partial_result, TaskSet)
                      and hasattr(partial_result, "actions")):
                    activity_context.df.actions.append(partial_result.actions)

                if should_suspend(partial_result):
                    logging.warning(f"!!!Generator Suspended")
                    response = OrchestratorState(
                        isDone=False,
                        output=None,
                        actions=activity_context.df.actions,
                        customStatus=self.customStatus)
                    return response.to_json_string()

                if (isinstance(partial_result, Task)
                    or isinstance(partial_result, TaskSet)) and (
                        partial_result.isFaulted):
                    gen.throw(partial_result.exception)
                    continue

                last_timestamp = dt_parse(decision_started_event["Timestamp"])
                decision_started_events = list(
                    filter(lambda e_: (
                            e_["EventType"] == HistoryEventType.OrchestratorStarted
                            and dt_parse(e_["Timestamp"]) > last_timestamp),
                           activity_context.df.histories))

                if len(decision_started_events) == 0:
                    activity_context.df.currentUtcDateTime = None
                    activity_context.df.currentTimestamp = None
                else:
                    decision_started_event = decision_started_events[0]
                    new_timestamp = dt_parse(decision_started_event["Timestamp"])
                    activity_context.df.currentUtcDateTime = new_timestamp
                    activity_context.df.currentTimestamp = new_timestamp

                logging.warning(f"!!!Generator Execution {gen_result}")
                if partial_result is not None:
                    gen_result = gen.send(partial_result.result)
                else:
                    gen_result = gen.send(None)
        except StopIteration as sie:
            logging.warning(f"!!!Generator Termination StopIteration {sie}")
            response = OrchestratorState(
                isDone=True,
                output=sie.value,
                actions=activity_context.df.actions,
                customStatus=self.customStatus)
            return response.to_json_string()
        except Exception as e:
            e_string = traceback.format_exc()
            logging.warning(f"!!!Generator Termination Exception {e_string}")
            response = OrchestratorState(
                isDone=False,
                output=None,  # Should have no output, after generation range
                actions=activity_context.df.actions,
                error=str(e),
                customStatus=self.customStatus)
            return response.to_json_string()

    @classmethod
    def create(cls, fn):
        logging.warning("!!!Calling orchestrator create")
        return lambda context: Orchestrator(fn).handle(context)
