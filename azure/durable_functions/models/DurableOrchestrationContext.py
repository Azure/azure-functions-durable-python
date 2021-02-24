import json
import datetime
from typing import List, Any, Dict, Optional
from uuid import UUID, uuid5, NAMESPACE_URL

from .RetryOptions import RetryOptions
from .TaskSet import TaskSet
from .FunctionContext import FunctionContext
from .history import HistoryEvent, HistoryEventType
from .actions import Action
from ..models.Task import Task
from ..models.TokenSource import TokenSource
from .utils.entity_utils import EntityId
from ..tasks import call_activity_task, task_all, task_any, call_activity_with_retry_task, \
    wait_for_external_event_task, continue_as_new, new_uuid, call_http, create_timer_task, \
    call_sub_orchestrator_task, call_sub_orchestrator_with_retry_task, call_entity_task, \
    signal_entity_task
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
        self._sub_orchestrator_counter: int = 0
        self._continue_as_new_flag: bool = False
        self.decision_started_event: HistoryEvent = \
            [e_ for e_ in self.histories
             if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED][0]
        self._current_utc_datetime: datetime.datetime = \
            self.decision_started_event.timestamp
        self._new_uuid_counter = 0
        self.actions: List[List[Action]] = []
        self._function_context: FunctionContext = FunctionContext(**kwargs)

        # make _input always a string
        # (consistent with Python Functions generic trigger/input bindings)
        if (isinstance(input, Dict)):
            input = json.dumps(input)
        self._input: Any = input

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

    def call_activity(self, name: str, input_: Optional[Any] = None) -> Task:
        """Schedule an activity for execution.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or fails.
        """
        return call_activity_task(
            state=self.histories,
            name=name,
            input_=input_)

    def call_activity_with_retry(self,
                                 name: str, retry_options: RetryOptions,
                                 input_: Optional[Any] = None) -> Task:
        """Schedule an activity for execution with retry options.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        retry_options: RetryOptions
            The retry options for the activity function.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or
            fails completely.
        """
        return call_activity_with_retry_task(
            state=self.histories,
            retry_options=retry_options,
            name=name,
            input_=input_)

    def call_http(self, method: str, uri: str, content: Optional[str] = None,
                  headers: Optional[Dict[str, str]] = None,
                  token_source: TokenSource = None) -> Task:
        """Schedule a durable HTTP call to the specified endpoint.

        Parameters
        ----------
        method: str
            The HTTP request method.
        uri: str
            The HTTP request uri.
        content: Optional[str]
            The HTTP request content.
        headers: Optional[Dict[str, str]]
            The HTTP request headers.
        token_source: TokenSource
            The source of OAuth token to add to the request.

        Returns
        -------
        Task
            The durable HTTP request to schedule.
        """
        return call_http(
            state=self.histories, method=method, uri=uri, content=content, headers=headers,
            token_source=token_source)

    def call_sub_orchestrator(self,
                              name: str, input_: Optional[Any] = None,
                              instance_id: Optional[str] = None) -> Task:
        """Schedule sub-orchestration function named `name` for execution.

        Parameters
        ----------
        name: str
            The name of the orchestrator function to call.
        input_: Optional[Any]
            The JSON-serializable input to pass to the orchestrator function.
        instance_id: Optional[str]
            A unique ID to use for the sub-orchestration instance.

        Returns
        -------
        Task
            A Durable Task that completes when the called sub-orchestrator completes or fails.
        """
        return call_sub_orchestrator_task(
            context=self,
            state=self.histories,
            name=name,
            input_=input_,
            instance_id=instance_id)

    def call_sub_orchestrator_with_retry(self,
                                         name: str, retry_options: RetryOptions,
                                         input_: Optional[Any] = None,
                                         instance_id: Optional[str] = None) -> Task:
        """Schedule sub-orchestration function named `name` for execution, with retry-options.

        Parameters
        ----------
        name: str
            The name of the activity function to schedule.
        retry_options: RetryOptions
            The settings for retrying this sub-orchestrator in case of a failure.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function. Defaults to None.
        instance_id: str
            The instance ID of the sub-orchestrator to call.

        Returns
        -------
        Task
            A Durable Task that completes when the called sub-orchestrator completes or fails.
        """
        return call_sub_orchestrator_with_retry_task(
            context=self,
            state=self.histories,
            retry_options=retry_options,
            name=name,
            input_=input_,
            instance_id=instance_id)

    def get_input(self) -> Optional[Any]:
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
        return new_uuid(context=self)

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
        return task_all(tasks=activities)

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
        return task_any(tasks=activities)

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
    def current_utc_datetime(self) -> datetime.datetime:
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
    def current_utc_datetime(self, value: datetime.datetime):
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

    def call_entity(self, entityId: EntityId,
                    operationName: str, operationInput: Optional[Any] = None):
        """Get the result of Durable Entity operation given some input.

        Parameters
        ----------
        entityId: EntityId
            The ID of the entity to call
        operationName: str
            The operation to execute
        operationInput: Optional[Any]
            The input for tne operation, defaults to None.

        Returns
        -------
        Task
            A Task of the entity call
        """
        return call_entity_task(self.histories, entityId, operationName, operationInput)

    def signal_entity(self, entityId: EntityId,
                      operationName: str, operationInput: Optional[Any] = None):
        """Send a signal operation to Durable Entity given some input.

        Parameters
        ----------
        entityId: EntityId
            The ID of the entity to call
        operationName: str
            The operation to execute
        operationInput: Optional[Any]
            The input for tne operation, defaults to None.

        Returns
        -------
        Task
            A Task of the entity signal
        """
        return signal_entity_task(self, self.histories, entityId, operationName, operationInput)

    @property
    def will_continue_as_new(self) -> bool:
        """Return true if continue_as_new was called."""
        return self._continue_as_new_flag

    def create_timer(self, fire_at: datetime.datetime) -> Task:
        """Create a Durable Timer Task to implement a deadline at which to wake-up the orchestrator.

        Parameters
        ----------
        fire_at : datetime.datetime
            The time for the timer to trigger

        Returns
        -------
        TimerTask
            A Durable Timer Task that schedules the timer to wake up the activity
        """
        return create_timer_task(state=self.histories, fire_at=fire_at)

    def wait_for_external_event(self, name: str) -> Task:
        """Wait asynchronously for an event to be raised with the name `name`.

        Parameters
        ----------
        name : str
            The event name of the event that the task is waiting for.

        Returns
        -------
        Task
            Task to wait for the event
        """
        return wait_for_external_event_task(state=self.histories, name=name)

    def continue_as_new(self, input_: Any):
        """Schedule the orchestrator to continue as new.

        Parameters
        ----------
        input_ : Any
            The new starting input to the orchestrator.
        """
        return continue_as_new(context=self, input_=input_)

    def new_guid(self) -> UUID:
        """Generate a replay-safe GUID.

        Returns
        -------
        UUID
            A new globally-unique ID
        """
        guid_name = f"{self.instance_id}_{self.current_utc_datetime}"\
            f"_{self._new_uuid_counter}"
        self._new_uuid_counter += 1
        guid = uuid5(NAMESPACE_URL, guid_name)
        return guid
