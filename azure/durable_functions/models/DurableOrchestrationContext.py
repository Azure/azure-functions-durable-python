import json
import logging
from typing import List, Any, Dict

from dateutil.parser import parse as dt_parse

from . import (RetryOptions)
from .history import HistoryEvent, HistoryEventType
from ..interfaces import IAction
from ..interfaces import ITaskMethods
from ..models.Task import Task
from ..tasks import call_activity_task, task_all, call_activity_with_retry_task


class DurableOrchestrationContext:

    def __init__(self,
                 context_string: str):
        context: Dict[str, Any] = json.loads(context_string)
        logging.warning(f"!!!Calling orchestrator handle {context}")
        self.histories: List[HistoryEvent] = context.get("history")
        self.instanceId = context.get("instanceId")
        self.isReplaying = context.get("isReplaying")
        self.parentInstanceId = context.get("parentInstanceId")
        self.call_activity = lambda n, i: call_activity_task(
            state=self.histories,
            name=n,
            input_=i)
        self.call_activity_with_retry = lambda n, o, i: call_activity_with_retry_task(
            state=self.histories,
            retry_options=o,
            name=n,
            input_=i)
        self.wait_for_external_event  = lambda n, i: wait_for_external_event_task(
            state=self.histories,
            name=n,
            input_=i)
        self.task_all = lambda t: task_all(state=self.histories, tasks=t)
        self.decision_started_event: HistoryEvent = list(filter(
            # HistoryEventType.OrchestratorStarted
            lambda e_: e_["EventType"] == HistoryEventType.OrchestratorStarted,
            self.histories))[0]
        self.currentUtcDateTime = dt_parse(self.decision_started_event["Timestamp"])
        self.newGuidCounter = 0
        self.actions: List[List[IAction]] = []
        self.Task: ITaskMethods

        def call_activity(name: str, input_=None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        def call_activity_with_retry(
                name: str, retry_options: RetryOptions, input_=None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        def callSubOrchestrator(
                name: str, input=None, instanceId: str = None) -> Task:
            raise NotImplementedError("This is a placeholder.")

        # TODO: more to port over
