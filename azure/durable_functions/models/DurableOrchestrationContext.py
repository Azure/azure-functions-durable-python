import json
import logging
import datetime
from typing import List, Any, Dict

from dateutil.parser import parse as dt_parse

from . import (RetryOptions)
from .history import HistoryEvent, HistoryEventType
from ..interfaces import IAction
from ..models.Task import Task
from ..tasks import call_activity_task, task_all, call_activity_with_retry_task


class DurableOrchestrationContext:
    """Context of the durable orchestration execution.

    Parameter data for orchestration bindings that can be used to schedule
    function-based activities.
    """

    def __init__(self,
                 context_string: str):
        context: Dict[str, Any] = json.loads(context_string)
        logging.warning(f"!!!Calling orchestrator handle {context}")
        self._histories: List[HistoryEvent] = context.get("history")
        self._instance_id = context.get("instanceId")
        self._is_replaying = context.get("isReplaying")
        self._parent_instance_id = context.get("parentInstanceId")
        self.call_activity = lambda n, i: call_activity_task(
            state=self.histories,
            name=n,
            input_=i)
        self.call_activity_with_retry = \
            lambda n, o, i: call_activity_with_retry_task(
                state=self.histories,
                retry_options=o,
                name=n,
                input_=i)
        self.task_all = lambda t: task_all(state=self.histories, tasks=t)
        self.decision_started_event: HistoryEvent = list(filter(
            lambda e_: e_["EventType"] == HistoryEventType.ORCHESTRATOR_STARTED,
            self.histories))[0]
        self._current_utc_datetime = \
            dt_parse(self.decision_started_event["Timestamp"])
        self.new_guid_counter = 0
        self.actions: List[List[IAction]] = []

    def call_activity(self, name: str, input_=None) -> Task:
        """Schedule an activity for execution.

        :param name: The name of the activity function to call.
        :param input_:The JSON-serializable input to pass to the activity
        function.
        :return: A Durable Task that completes when the called activity
        function completes or fails.
        """
        raise NotImplementedError("This is a placeholder.")

    def call_activity_with_retry(self,
                                 name: str, retry_options: RetryOptions,
                                 input_=None) -> Task:
        """Schedule an activity for execution with retry options.

        :param name: The name of the activity function to call.
        :param retry_options: The retry options for the activity function.
        :param input_: The JSON-serializable input to pass to the activity
        function.
        :return: A Durable Task that completes when the called activity
        function completes or fails completely.
        """
        raise NotImplementedError("This is a placeholder.")

    def call_sub_orchestrator(self,
                              name: str, input_=None,
                              instance_id: str = None) -> Task:
        """Schedule an orchestration function named `name` for execution.

        :param name: The name of the orchestrator function to call.
        :param input_: The JSON-serializable input to pass to the orchestrator
        function.
        :param instance_id: A unique ID to use for the sub-orchestration
        instance. If `instanceId` is not specified, the extension will generate
        an id in the format `<calling orchestrator instance ID>:<#>`
        """
        raise NotImplementedError("This is a placeholder.")

    @property
    def histories(self):
        """Get running history of tasks that have been scheduled."""
        return self._histories

    @property
    def instance_id(self):
        """Get the ID of the current orchestration instance.

        The instance ID is generated and fixed when the orchestrator function
        is scheduled. It can be either auto-generated, in which case it is
        formatted as a GUID, or it can be user-specified with any format.

        :return: The ID of the current orchestration instance.
        """
        return self._instance_id

    @property
    def is_replaying(self):
        """Get the value indicating orchestration replaying itself.

        This property is useful when there is logic that needs to run only when
        the orchestrator function is _not_ replaying. For example, certain
        types of application logging may become too noisy when duplicated as
        part of orchestrator function replay. The orchestrator code could check
        to see whether the function is being replayed and then issue the log
        statements when this value is `false`.

        :return: value indicating whether the orchestrator function is
        currently replaying
        """
        return self._is_replaying

    @property
    def parent_instance_id(self):
        """Get the ID of the parent orchestration.

        The parent instance ID is generated and fixed when the parent
        orchestrator function is scheduled. It can be either auto-generated, in
        which case it is formatted as a GUID, or it can be user-specified with
        any format.
        :return: ID of the parent orchestration of the current
        sub-orchestration instance
        """
        return self._parent_instance_id

    @property
    def current_utc_datetime(self) -> datetime:
        """Get the current date/time.

        This date/time value is derived from the orchestration history. It
        always returns the same value at specific points in the orchestrator
        function code, making it deterministic and safe for replay.
        :return: The current date/time in a way that is safe for use by
        orchestrator functions
        """
        return self._current_utc_datetime

    @current_utc_datetime.setter
    def current_utc_datetime(self, value: datetime):
        self._current_utc_datetime = value
