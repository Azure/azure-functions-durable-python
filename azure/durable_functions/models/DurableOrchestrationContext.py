import json
import datetime
from typing import List, Any, Dict

from . import (RetryOptions, TaskSet)
from .FunctionContext import FunctionContext
from .history import HistoryEvent, HistoryEventType
from .actions import Action
from ..models.Task import Task
from ..models.TokenSource import TokenSource
from ..tasks import call_activity_task, task_all, task_any, call_activity_with_retry_task, \
    wait_for_external_event_task, continue_as_new, new_uuid, call_http
from azure.functions._durable_functions import _deserialize_custom_object


class DurableOrchestrationContext:
    """Context of the durable orchestration execution.

    Parameter data for orchestration bindings that can be used to schedule
    function-based activities.
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self,
                 history: List[Dict[Any, Any]], instanceId: str, isReplaying: bool,
                 parentInstanceId: str, input: Any = None, **kwargs):
        self._histories: List[HistoryEvent] = [HistoryEvent(**he) for he in history]
        self._instance_id: str = instanceId
        self._is_replaying: bool = isReplaying
        self._parent_instance_id: str = parentInstanceId
        self._custom_status: Any = None
        self._new_uuid_counter: int = 0
        self.call_activity = lambda n, i=None: call_activity_task(
            state=self.histories,
            name=n,
            input_=i)
        self.call_activity_with_retry = \
            lambda n, o, i=None: call_activity_with_retry_task(
                state=self.histories,
                retry_options=o,
                name=n,
                input_=i)
        self.call_http = lambda method, uri, content=None, headers=None, token_source=None: \
            call_http(
                state=self.histories, method=method, uri=uri, content=content, headers=headers,
                token_source=token_source)
        self.wait_for_external_event = lambda n: wait_for_external_event_task(
            state=self.histories,
            name=n)
        self.new_uuid = lambda: new_uuid(context=self)
        self.continue_as_new = lambda i: continue_as_new(input_=i)
        self.task_any = lambda t: task_any(tasks=t)
        self.task_all = lambda t: task_all(tasks=t)
        self.decision_started_event: HistoryEvent = \
            [e_ for e_ in self.histories
             if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED][0]
        self._current_utc_datetime = \
            self.decision_started_event.timestamp
        self._new_uuid_counter = 0
        self.actions: List[List[Action]] = []
        self._function_context: FunctionContext = FunctionContext(**kwargs)

        # make _input always a string
        # (consistent with Python Functions generic trigger/input bindings)
        if (isinstance(input, Dict)):
            input = json.dumps(input)
        self._input: str = input

    @classmethod
    def from_json(cls, json_string: str):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_string: str
            Context passed a JSON serializable value to be converted into an instance of the class

        Returns
        -------
        DurableOrchestrationContext
            New instance of the durable orchestration context class
        """
        # We should consider parsing the `Input` field here as well,
        # intead of doing so lazily when `get_input` is called.
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    def call_activity(self, name: str, input_=None) -> Task:
        """Schedule an activity for execution.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        input_:
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or fails.
        """
        raise NotImplementedError("This is a placeholder.")

    def call_activity_with_retry(self,
                                 name: str, retry_options: RetryOptions,
                                 input_=None) -> Task:
        """Schedule an activity for execution with retry options.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        retry_options: RetryOptions
            The retry options for the activity function.
        input_:
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or
            fails completely.
        """
        raise NotImplementedError("This is a placeholder.")

    def call_http(self, method: str, uri: str, content: str = None,
                  headers: Dict[str, str] = None, token_source: TokenSource = None) -> Task:
        """Schedule a durable HTTP call to the specified endpoint.

        Parameters
        ----------
        method: str
            The HTTP request method.
        uri: str
            The HTTP request uri.
        content: str
            The HTTP request content.
        headers: Dict[str, str]
            The HTTP request headers.
        token_source: TokenSource
            The source of OAuth token to add to the request.

        Returns
        -------
        Task
            The durable HTTP request to schedule.
        """
        raise NotImplementedError("This is a placeholder.")

    def call_sub_orchestrator(self,
                              name: str, input_=None,
                              instance_id: str = None) -> Task:
        """Schedule an orchestration function named `name` for execution.

        Parameters
        ----------
        name: str
            The name of the orchestrator function to call.
        input_:
            The JSON-serializable input to pass to the orchestrator function.
        instance_id: str
            A unique ID to use for the sub-orchestration instance. If `instanceId` is not
            specified, the extension will generate an id in the format `<calling orchestrator
            instance ID>:<#>`
        """
        raise NotImplementedError("This is a placeholder.")

    def get_input(self) -> str:
        """Get the orchestration input."""
        return None if self._input is None else json.loads(self._input,
                                                           object_hook=_deserialize_custom_object)

    def new_uuid(self) -> str:
        """Create a new UUID that is safe for replay within an orchestration or operation.

        The default implementation of this method creates a name-based UUID
        using the algorithm from RFC 4122 §4.3. The name input used to generate
        this value is a combination of the orchestration instance ID and an
        internally managed sequence number.

        Returns
        -------
        str
            New UUID that is safe for replay within an orchestration or operation.
        """
        raise NotImplementedError("This is a placeholder.")

    def task_all(self, activities: List[Task]) -> TaskSet:
        """Schedule the execution of all activities.

        Similar to Promise.all. When called with `yield` or `return`, returns an
        array containing the results of all [[Task]]s passed to it. It returns
        when all of the [[Task]] instances have completed.

        Throws an exception if any of the activities fails
        Parameters
        ----------
        activities: List[Task]
            List of activities to schedule

        Returns
        -------
        TaskSet
            The results of all activities.
        """
        raise NotImplementedError("This is a placeholder.")

    def task_any(self, activities: List[Task]) -> TaskSet:
        """Schedule the execution of all activities.

        Similar to Promise.race. When called with `yield` or `return`, returns
        the first [[Task]] instance to complete.

        Throws an exception if all of the activities fail

        Parameters
        ----------
        activities: List[Task]
            List of activities to schedule

        Returns
        -------
        TaskSet
            The first [[Task]] instance to complete.
        """
        raise NotImplementedError("This is a placeholder.")

    def set_custom_status(self, status: Any):
        """Set the customized orchestration status for your orchestrator function.

        This status is also returned by the orchestration client through the get_status API

        Parameters
        ----------
        status : str
            Customized status provided by the orchestrator
        """
        self._custom_status = status

    @property
    def custom_status(self):
        """Get customized status of current orchestration."""
        return self._custom_status

    @property
    def histories(self):
        """Get running history of tasks that have been scheduled."""
        return self._histories

    @property
    def instance_id(self) -> str:
        """Get the ID of the current orchestration instance.

        The instance ID is generated and fixed when the orchestrator function
        is scheduled. It can be either auto-generated, in which case it is
        formatted as a GUID, or it can be user-specified with any format.

        Returns
        -------
        str
            The ID of the current orchestration instance.
        """
        return self._instance_id

    @property
    def is_replaying(self) -> bool:
        """Get the value indicating orchestration replaying itself.

        This property is useful when there is logic that needs to run only when
        the orchestrator function is _not_ replaying. For example, certain
        types of application logging may become too noisy when duplicated as
        part of orchestrator function replay. The orchestrator code could check
        to see whether the function is being replayed and then issue the log
        statements when this value is `false`.

        Returns
        -------
        bool
            Value indicating whether the orchestrator function is currently replaying.
        """
        return self._is_replaying

    @property
    def parent_instance_id(self) -> str:
        """Get the ID of the parent orchestration.

        The parent instance ID is generated and fixed when the parent
        orchestrator function is scheduled. It can be either auto-generated, in
        which case it is formatted as a GUID, or it can be user-specified with
        any format.

        Returns
        -------
        str
            ID of the parent orchestration of the current sub-orchestration instance
        """
        return self._parent_instance_id

    @property
    def current_utc_datetime(self) -> datetime:
        """Get the current date/time.

        This date/time value is derived from the orchestration history. It
        always returns the same value at specific points in the orchestrator
        function code, making it deterministic and safe for replay.

        Returns
        -------
        datetime
            The current date/time in a way that is safe for use by orchestrator functions
        """
        return self._current_utc_datetime

    @current_utc_datetime.setter
    def current_utc_datetime(self, value: datetime):
        self._current_utc_datetime = value

    @property
    def function_context(self) -> FunctionContext:
        """Get the function level attributes not used by durable orchestrator.

        Returns
        -------
        FunctionContext
            Object containing function level attributes not used by durable orchestrator.
        """
        return self._function_context
