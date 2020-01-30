import json
import datetime
from typing import List, Any, Dict

from . import (RetryOptions)
from .history import HistoryEvent, HistoryEventType
from ..interfaces import IAction
from ..models.Task import Task
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from ..tasks import \
    call_activity_task, task_all,call_activity_with_retry_task,create_timer_task
=======
from ..tasks import call_activity_task, task_all, call_activity_with_retry_task, wait_for_external_event_task
>>>>>>> fix bugs to make waitForExternalEvent working
=======
from ..tasks import call_activity_task, task_all, call_activity_with_retry_task, \
=======
from ..tasks import call_activity_task, task_all, task_any, call_activity_with_retry_task, \
>>>>>>> implement task_any function
    wait_for_external_event_task
>>>>>>> flake8 fixes


class DurableOrchestrationContext:
    """Context of the durable orchestration execution.

    Parameter data for orchestration bindings that can be used to schedule
    function-based activities.
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    # noinspection PyPep8Naming
    def __init__(self,
<<<<<<< HEAD
                 context_string: str):
        context: Dict[str, Any] = json.loads(context_string)
        self._histories: List[HistoryEvent] = [HistoryEvent(**he) for he in context.get("history")]
        self._instance_id = context.get("instanceId")
        self._is_replaying = context.get("isReplaying")
        self._parent_instance_id = context.get("parentInstanceId")
<<<<<<< HEAD
        self.input:str = context.get("input")
        self.call_activity = lambda n, i: call_activity_task(
=======
=======
                 history: Dict[Any, Any], instanceId: str, isReplaying: bool,
                 parentInstanceId: str, **kwargs):
        self._histories: List[HistoryEvent] = [HistoryEvent(**he) for he in history]
        self._instance_id: str = instanceId
        self._is_replaying: bool = isReplaying
        self._parent_instance_id: str = parentInstanceId
>>>>>>> Refactor json conversion
        self.call_activity = lambda n, i=None: call_activity_task(
>>>>>>> Base implementation of tests
            state=self.histories,
            name=n,
            input_=i)
<<<<<<< HEAD
        self.call_activity_with_retry = \
            lambda n, o, i=None: call_activity_with_retry_task(
                state=self.histories,
                retry_options=o,
                name=n,
                input_=i)
<<<<<<< HEAD
        self.create_timer = lambda d: create_timer_task(state=self.histories,fire_at=d)
=======
        self.call_activity_with_retry = lambda n, o, i: call_activity_with_retry_task(
            state=self.histories,
            retry_options=o,
            name=n,
            input_=i)
        self.wait_for_external_event = lambda n: wait_for_external_event_task(
            state=self.histories,
            name=n)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> fix bugs to make waitForExternalEvent working
=======
        self.task_any = lambda t: task_any(state=self.histories, tasks=t)
>>>>>>> implement task_any function
=======
=======
        self.create_timer = lambda d: create_timer_task(
            state=self.histories,
            fire_at=d)
>>>>>>> create timer first pass
        self.task_any = lambda t: task_any(tasks=t)
>>>>>>> remove state in task_any
        self.task_all = lambda t: task_all(state=self.histories, tasks=t)
=======
        self.task_all = lambda t: task_all(tasks=t)
<<<<<<< HEAD
>>>>>>> test failed scenario
        self.decision_started_event: HistoryEvent = list(filter(
            lambda e_: e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED,
            self.histories))[0]
=======
        self.decision_started_event: HistoryEvent = \
            [e_ for e_ in self.histories
             if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED][0]
>>>>>>> Remove IFunctionContext abstraction
        self._current_utc_datetime = \
<<<<<<< HEAD
            dt_parse(self.decision_started_event["Timestamp"])
        self._custom_status = None
=======
            self.decision_started_event.timestamp
>>>>>>> Refactoring HistoryEvent
        self.new_guid_counter = 0
        self.actions: List[List[IAction]] = []
<<<<<<< HEAD
    
    
    def get_input(input: Any) -> Any:
        """        
        Returns
        -------
        str
            Returns the input parameters obtained in the context of a Azure Function call
        """
        return input
=======
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)

    @classmethod
    def from_json(cls, json_string):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_string: Context passed a JSON serializable value to be converted into an
        instance of the class

        Returns
        -------
        DurableOrchestrationContext: new instance of the durable orchestration context class
        """
        json_dict = json.loads(json_string)
        return cls(**json_dict)
<<<<<<< HEAD
>>>>>>> Refactor json conversion
=======
    
    def get_input(input: Any) -> Any:
        """        
        Returns
        -------
        str
            Returns the input parameters obtained in the context of a Azure Function call
        """
        return input
>>>>>>> create timer first pass

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

    def task_all(self, activities: List[HistoryEvent]) -> List[Task]:
        """Schedule the execution of all activities.

        Similar to Promise.all. When called with `yield` or `return`, returns an
        array containing the results of all [[Task]]s passed to it. It returns
        when all of the [[Task]] instances have completed.

        Throws an exception if any of the activities fails
        Parameters
        ----------
        activities: List of activities to schedule

        Returns
        -------
        The results of all activities.
        """
        raise NotImplementedError("This is a placeholder.")

    def task_any(self, activities: List[HistoryEvent]) -> List[Task]:
        """Schedule the execution of all activities.

        Similar to Promise.race. When called with `yield` or `return`, returns
        the first [[Task]] instance to complete.

        Throws an exception if all of the activities fail
        Parameters
        ----------
        activities: List of activities to schedule

        Returns
        -------
        The first [[Task]] instance to complete.
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
