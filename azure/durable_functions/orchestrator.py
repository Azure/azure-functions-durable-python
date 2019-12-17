import json
import logging
import traceback
from datetime import datetime
from typing import Callable, Iterator, List, Any, Union, Dict

from dateutil.parser import parse as dt_parse

from .interfaces import IFunctionContext, IAction
from .models import (
    DurableOrchestrationContext,
    Task,
    TaskSet,
    OrchestratorState)
from .models.history import HistoryEvent, HistoryEventType
from .tasks.call_activity import call_activity
from .tasks.task_all import task_all
from .tasks.task_utilities import should_suspend


class Orchestrator:
    def __init__(self,
                 activity_func: Callable[[IFunctionContext], Iterator[Any]]):
        self.fn: Callable[[IFunctionContext], Iterator[Any]] = activity_func
        self.currentUtcDateTime: datetime = None
        self.customStatus: Any = None
        self.newGuidCounter: int = 0

    def handle(self, context_string: str):
        context: Dict[str, Any] = json.loads(context_string)
        logging.warning(f"!!!Calling orchestrator handle {context}")
        context_histories: List[HistoryEvent] = context.get("history")
        context_instance_id = context.get("instanceId")
        context_is_replaying = context.get("isReplaying")
        context_parent_instance_id = context.get("parentInstanceId")

        decision_started_event: HistoryEvent = list(filter(
            # HistoryEventType.OrchestratorStarted
            lambda e_: e_["EventType"] == HistoryEventType.OrchestratorStarted,
            context_histories))[0]

        self.currentUtcDateTime = dt_parse(decision_started_event["Timestamp"])
        self.newGuidCounter = 0

        durable_context = DurableOrchestrationContext(
            instanceId=context_instance_id,
            isReplaying=context_is_replaying,
            parentInstanceId=context_parent_instance_id,
            callActivity=lambda n, i: call_activity(
                state=context_histories,
                name=n,
                input_=i),
            task_all=lambda t: task_all(state=context_histories, tasks=t),
            currentUtcDateTime=self.currentUtcDateTime)
        activity_context = IFunctionContext(df=durable_context)

        gen = self.fn(activity_context)
        actions: List[List[IAction]] = []
        partial_result: Union[Task, TaskSet] = None

        try:
            if partial_result is not None:
                gen_result = gen.send(partial_result.result)
            else:
                gen_result = gen.send(None)

            while True:
                logging.warning(f"!!!actions {actions}")
                logging.warning(f"!!!Generator Execution {gen_result}")

                partial_result = gen_result

                if (isinstance(partial_result, Task)
                        and hasattr(partial_result, "action")):
                    actions.append([partial_result.action])
                elif (isinstance(partial_result, TaskSet)
                      and hasattr(partial_result, "actions")):
                    actions.append(partial_result.actions)

                if should_suspend(partial_result):
                    logging.warning(f"!!!Generator Suspended")
                    response = OrchestratorState(
                        isDone=False,
                        output=None,
                        actions=actions,
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
                           context_histories))

                if len(decision_started_events) == 0:
                    activity_context.df.currentUtcDateTime = None
                    self.currentTimestamp = None
                else:
                    decision_started_event = decision_started_events[0]
                    new_timestamp = dt_parse(decision_started_event["Timestamp"])
                    activity_context.df.currentUtcDateTime = new_timestamp
                    self.currentTimestamp = new_timestamp

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
                actions=actions,
                customStatus=self.customStatus)
            return response.to_json_string()
        except Exception as e:
            e_string = traceback.format_exc()
            logging.warning(f"!!!Generator Termination Exception {e_string}")
            response = OrchestratorState(
                isDone=False,
                output=None,  # Should have no output, after generation range
                actions=actions,
                error=str(e),
                customStatus=self.customStatus)
            return response.to_json_string()

    @classmethod
    def create(cls, fn):
        logging.warning("!!!Calling orchestrator create")
        return lambda context: Orchestrator(fn).handle(context)
