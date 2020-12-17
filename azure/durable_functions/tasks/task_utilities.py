import json
from ..models.history import HistoryEventType, HistoryEvent
from azure.functions._durable_functions import _deserialize_custom_object
from dateutil import parser
from typing import List, Optional, Dict, Any
from ..models.actions.Action import Action
from ..models.Task import Task


def should_suspend(partial_result) -> bool:
    """Check the state of the result to determine if the orchestration should suspend."""
    return bool(partial_result is not None
                and hasattr(partial_result, "is_completed")
                and not partial_result.is_completed)


def parse_history_event(directive_result):
    """Based on the type of event, parse the JSON.serializable portion of the event."""
    event_type = directive_result.event_type
    if event_type is None:
        raise ValueError("EventType is not found in task object")

    # We provide the ability to deserialize custom objects, because the output of this
    # will be passed directly to the orchestrator as the output of some activity
    if event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED:
        return json.loads(directive_result.Result, object_hook=_deserialize_custom_object)
    if event_type == HistoryEventType.TASK_COMPLETED:
        return json.loads(directive_result.Result, object_hook=_deserialize_custom_object)
    if event_type == HistoryEventType.EVENT_RAISED:
        # TODO: Investigate why the payload is in "Input" instead of "Result"
        return json.loads(directive_result.Input, object_hook=_deserialize_custom_object)
    return None


def find_event(state: List[HistoryEvent], event_type: HistoryEventType,
               extra_constraints: Dict[str, Any]) -> Optional[HistoryEvent]:
    """Find event in the histories array as per some constraints.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of events so far in the orchestaration
    event_type: HistoryEventType
        The type of the event we're looking for
    extra_constraints: Dict[str, Any]
        A dictionary of key-value pairs where the key is a property of the
        sought-after event, and value are its expected contents.

    Returns
    -------
    Optional[HistoryEvent]
        The event being searched-for, if found. Else, None.
    """
    def satisfies_contraints(e: HistoryEvent) -> bool:
        """Determine if an event matches our search criteria.

        Parameters
        ----------
        e: HistoryEvent
            An event from the state array

        Returns
        -------
        bool
            True if the event matches our constraints. Else, False.
        """
        for attr, val in extra_constraints.items():
            if hasattr(e, attr) and getattr(e, attr) == val:
                continue
            else:
                return False
        return True

    tasks = [e for e in state
             if e.event_type == event_type
             and satisfies_contraints(e) and not e.is_processed]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_event_raised(state, name):
    """Find if the event with the given event name is raised.

    Parameters
    ----------
    state : List[HistoryEvent]
        List of histories to search from
    name : str
        Name of the event to search for

    Returns
    -------
    HistoryEvent
        The raised event with the given event name that has not yet been processed.
        Returns None if no event with the given conditions was found.

    Raises
    ------
    ValueError
        Raises an error if no name was given when calling this function.
    """
    if not name:
        raise ValueError("Name cannot be empty")

    tasks = [e for e in state
             if e.event_type == HistoryEventType.EVENT_RAISED
             and e.Name == name and not e.is_processed]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_scheduled(state, name):
    """Locate the Scheduled Task.

    Within the state passed, search for an event that has hasn't been processed
    and has the the name provided.
    """
    if not name:
        raise ValueError("Name cannot be empty")

    tasks = [e for e in state
             if e.event_type == HistoryEventType.TASK_SCHEDULED
             and e.Name == name and not e.is_processed]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_completed(state, scheduled_task):
    """Locate the Completed Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a completed  task type,
    and has the a scheduled id that equals the EventId of the provided scheduled task.
    """
    if scheduled_task is None:
        return None

    tasks = [e for e in state if e.event_type == HistoryEventType.TASK_COMPLETED
             and e.TaskScheduledId == scheduled_task.event_id]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_failed(state, scheduled_task):
    """Locate the Failed Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a failed task type,
    and has the a scheduled id that equals the EventId of the provided scheduled task.
    """
    if scheduled_task is None:
        return None

    tasks = [e for e in state if e.event_type == HistoryEventType.TASK_FAILED
             and e.TaskScheduledId == scheduled_task.event_id]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_timer_created(state, fire_at):
    """Locate the Timer Created Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer created task type,
    and has the an event id that is one higher then Scheduled Id of the provided
    failed task provided.
    """
    if fire_at is None:
        return None

    # We remove the timezone metadata,
    # to enable comparisons with timezone-naive datetime objects. This may be dangerous
    fire_at = fire_at.replace(tzinfo=None)
    tasks = []
    for e in state:
        if e.event_type == HistoryEventType.TIMER_CREATED and hasattr(e, "FireAt"):
            if parser.parse(e.FireAt).replace(tzinfo=None) == fire_at:
                tasks.append(e)

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_retry_timer_created(state, failed_task):
    """Locate the Timer Created Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer created task type,
    and has the an event id that is one higher then Scheduled Id of the provided
    failed task provided.
    """
    if failed_task is None:
        return None

    tasks = [e for e in state if e.event_type == HistoryEventType.TIMER_CREATED
             and e.event_id == failed_task.TaskScheduledId + 1]

    if len(tasks) == 0:
        return None

    return tasks[0]


def find_task_retry_timer_fired(state, retry_timer_created):
    """Locate the Timer Fired Task.

    Within the state passed, search for an event that has hasn't been processed,
    is a timer fired task type,
    and has the an timer id that is equal to the EventId of the provided
    timer created task provided.
    """
    if retry_timer_created is None:
        return None

    tasks = [e for e in state if e.event_type == HistoryEventType.TIMER_FIRED
             and e.TimerId == retry_timer_created.event_id]

    if len(tasks) == 0:
        return None

    return tasks[0]


def set_processed(tasks):
    """Set the isProcessed attribute of all of the tasks to true.

    This provides the ability to not look at events that have already been processed within
    searching the history of events.
    """
    for task in tasks:
        if task is not None:
            task.is_processed = True


def find_sub_orchestration(
        state: List[HistoryEvent],
        event_type: HistoryEventType,
        name: Optional[str] = None,
        context=None,
        instance_id: Optional[str] = None,
        scheduled_task: Optional[HistoryEvent] = None) -> Optional[HistoryEvent]:
    """Look-up matching sub-orchestrator event in the state array.

    Parameters
    ----------
    state: List[HistoryEvent]
        The history of Durable events
    event_type: HistoryEventType
        The type of Durable event to look for.
    name: Optional[str]:
        Name of the sub-orchestrator.
    context: Optional['DurableOrchestrationContext']
        A reference to the orchestration context
    instance_id: Optional[str], optional:
        Instance ID of the sub-orchestrator. Defaults to None.
    scheduled_task" Optional[HistoryEvent], optional:
        The corresponding `scheduled` task for the searched-for event,
        only available when looking for a completed or failed event.
        Defaults to None.

    Returns
    -------
    Optional[HistoryEvent]:
        The matching event from the state array, if it exists.
    """

    def gen_err_message(counter: int, mid_message: str, found: str, expected: str) -> str:
        beg = f"The sub-orchestration call (n = {counter}) should be executed with "
        middle = mid_message.format(found, expected)
        end = " Check your code for non-deterministic behavior."
        err_message = beg + middle + end
        return err_message

    event: Optional[HistoryEvent] = find_matching_event(state, event_type, scheduled_task)

    # Test for name and instance_id mistaches and, if so, error out.
    # Also increase sub-orchestrator counter, for reporting.
    if event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_CREATED and (event is not None):

        context._sub_orchestrator_counter += 1
        counter: int = context._sub_orchestrator_counter

        if name is None:
            err = "Tried to lookup suborchestration in history but had not name to reference it."
            raise ValueError(err)

        # TODO: The HistoryEvent does not necessarily have a name or an instance_id
        #       We should create sub-classes of these types like JS does, to ensure their
        #       precense.
        err_message: str = ""
        if not(event.Name == name):
            mid_message = "a function name of {} instead of the provided function name of {}."
            err_message = gen_err_message(counter, mid_message, event.Name, name)
            raise ValueError(err_message)
        if instance_id and not(event.InstanceId == instance_id):
            mid_message = "an instance id of {} instead of the provided instance id of {}."
            err_message = gen_err_message(counter, mid_message, event.Name, name)
            raise ValueError(err_message)

    return event


def find_sub_orchestration_created(
        state: List[HistoryEvent],
        name: str,
        context=None,
        instance_id: Optional[str] = None) -> Optional[HistoryEvent]:
    """Look-up matching sub-orchestrator created event in the state array.

    Parameters
    ----------
    state: List[HistoryEvent]:
        The history of Durable events
    name: str:
        Name of the sub-orchestrator.
    context: Optional['DurableOrchestrationContext']:
        A reference to the orchestration context.
    instance_id: Optional[str], optional:
        Instance ID of the sub-orchestrator. Defaults to None.

    Raises
    ------
    ValueError: When the provided sub-orchestration name or instance_id (if provided) do not
        correspond to the matching event in the state list.

    Returns
    -------
    Optional[HistoryEvent]:
        The matching sub-orchestration creation event. Else, None.
    """
    event_type = HistoryEventType.SUB_ORCHESTRATION_INSTANCE_CREATED
    return find_sub_orchestration(
        state=state,
        event_type=event_type,
        name=name,
        instance_id=instance_id,
        context=context)


def find_sub_orchestration_completed(
        state: List[HistoryEvent],
        scheduled_task: Optional[HistoryEvent]) -> Optional[HistoryEvent]:
    """Look-up the sub-orchestration completed event.

    Parameters
    ----------
    state: List[HistoryEvent]:
        The history of Durable events
    scheduled_task: Optional[HistoryEvent]:
        The sub-orchestration creation event, if found.

    Returns
    -------
    Optional[HistoryEvent]:
        The matching sub-orchestration completed event, if found. Else, None.
    """
    event_type = HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED
    return find_sub_orchestration(
        state=state,
        event_type=event_type,
        scheduled_task=scheduled_task)


def find_sub_orchestration_failed(
        state: List[HistoryEvent],
        scheduled_task: Optional[HistoryEvent]) -> Optional[HistoryEvent]:
    """Look-up the sub-orchestration failure event.

    Parameters
    ----------
    state: List[HistoryEvent]:
        The history of Durable events
    scheduled_task: Optional[HistoryEvent]:
        The sub-orchestration creation event, if found.

    Returns
    -------
    Optional[HistoryEvent]:
        The matching sub-orchestration failure event, if found. Else, None.
    """
    event_type = HistoryEventType.SUB_ORCHESTRATION_INSTANCE_FAILED
    return find_sub_orchestration(
        state=state,
        event_type=event_type,
        scheduled_task=scheduled_task)


def find_matching_event(
        state: List[HistoryEvent],
        event_type: HistoryEventType,
        scheduled_task: Optional[HistoryEvent] = None) -> Optional[HistoryEvent]:
    """Find matching event in the state array, if it exists.

    Parameters
    ----------
    state: List[HistoryEvent]:
        The list of Durable events
    event_type: HistoryEventType:
        The type of event being searched-for.
    scheduled_task" Optional[HistoryEvent], optional:
        The corresponding `scheduled` task for the searched-for event,
        only available when looking for a completed or failed event.
        Defaults to None.

    Returns
    -------
    Optional[HistoryEvent]:
        The matching event from the state array, if it exists.
    """

    def should_preserve(event: HistoryEvent) -> bool:
        """Check if `event` matches the task being searched-for.

        Parameters
        ----------
        event: HistoryEvent:
            An event from the `state` array.

        Returns
        -------
        bool:
            True if `event` matches the task being search-for.
            False otherwise.
        """
        should_preserve = False
        has_correct_type = event.event_type == event_type
        if has_correct_type:
            is_not_processed = not event.is_processed
            extra_constraints = True
            if not (scheduled_task is None):
                extra_constraints = event.TaskScheduledId == scheduled_task.event_id
            should_preserve = has_correct_type and is_not_processed and extra_constraints
        return should_preserve

    event: Optional[HistoryEvent] = None

    # Preverse only the elements of the state array that correspond with the looked-up event
    matches = list(filter(should_preserve, state))

    if len(matches) >= 1:
        # TODO: in many instances, `matches` will be greater than 1 in length. We take the
        # first element because that corresponds to the first non-processed event, which
        # we assume corresponds to the one we are looking for. This may be brittle but
        # is true about other areas of the code as well such as with `call_activity`.
        # We should try to refactor this logic at some point
        event = matches[0]
    return event


def get_retried_task(
        state: List[HistoryEvent], max_number_of_attempts: int, scheduled_type: HistoryEventType,
        completed_type: HistoryEventType, failed_type: HistoryEventType, action: Action) -> Task:
    """Determine the state of scheduling some task for execution with retry options.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of history events
    max_number_of_ints: int
        The maximum number of retrying attempts
    scheduled_type: HistoryEventType
        The event type corresponding to scheduling the searched-for task
    completed_type: HistoryEventType
        The event type corresponding to a completion of the searched-for task
    failed_type: HistoryEventType
        The event type coresponding to the failure of the searched-for task
    action: Action
        The action corresponding to the searched-for task

    Returns
    -------
    Task
        A Task encompassing the state of the scheduled work item, that is,
        either completed, failed, or incomplete.
    """
    # tasks to look for in the state array
    scheduled_task, completed_task = None, None
    failed_task, scheduled_timer_task = None, None
    attempt = 1

    # Note each case below is exclusive, and the order matters
    for event in state:
        event_type = HistoryEventType(event.event_type)

        # Skip processed events
        if event.is_processed:
            continue

        # first we find the scheduled_task
        elif scheduled_task is None:
            if event_type is scheduled_type:
                scheduled_task = event

        # if the task has a correponding completion, we process the events
        # and return a completed task
        elif event_type == completed_type and \
                event.TaskScheduledId == scheduled_task.event_id:
            completed_task = event
            set_processed([scheduled_task, completed_task])
            return Task(
                is_completed=True,
                is_faulted=False,
                action=action,
                result=parse_history_event(completed_task),
                timestamp=completed_task.timestamp,
                id_=completed_task.TaskScheduledId
            )

        # if its failed, we'll have to wait for an upcoming timer scheduled
        elif failed_task is None:
            if event_type is failed_type:
                if event.TaskScheduledId == scheduled_task.event_id:
                    failed_task = event

        # if we have a timer scheduled, we'll have to find a timer fired
        elif scheduled_timer_task is None:
            if event_type is HistoryEventType.TIMER_CREATED:
                scheduled_timer_task = event

        # if we have a timer fired, we check if we still have more attempts for retries.
        # If so, we retry again and clear our found events so far.
        # If not, we process the events and return a completed task
        elif event_type is HistoryEventType.TIMER_FIRED:
            if event.TimerId == scheduled_timer_task.event_id:
                set_processed([scheduled_task, completed_task, failed_task, scheduled_timer_task])
                if attempt >= max_number_of_attempts:
                    return Task(
                        is_completed=True,
                        is_faulted=True,
                        action=action,
                        timestamp=failed_task.timestamp,
                        id_=failed_task.TaskScheduledId,
                        exc=Exception(
                            f"{failed_task.Reason} \n {failed_task.Details}")
                    )
                else:
                    scheduled_task, failed_task, scheduled_timer_task = None, None, None
                    attempt += 1
    return Task(is_completed=False, is_faulted=False, action=action)
