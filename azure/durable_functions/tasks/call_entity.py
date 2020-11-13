from typing import List, Any, Optional

from ..models.Task import (
    Task)
from ..models.actions.CallEntityAction import CallEntityAction
from ..models.history import HistoryEvent, HistoryEventType
from .task_utilities import set_processed, parse_history_event, find_event
from ..models.utils.entity_utils import EntityId
from ..models.entities.RequestMessage import RequestMessage
from ..models.entities.ResponseMessage import ResponseMessage
import json


def call_entity_task(
        state: List[HistoryEvent],
        entity_id: EntityId,
        operation_name: str = "",
        input_: Optional[Any] = None):
    """Determine the status of a call-entity task.

    It the task hasn't been scheduled, it returns a Task to schedule. If the task completed,
    we return a completed Task, to process its result.

    Parameters
    ----------
    state: List[HistoryEvent]
        The list of history events to search over to determine the
        current state of the callEntity Task.
    entity_id: EntityId
        An identifier for the entity to call.
    operation_name: str
        The name of the operation the entity needs to execute.
    input_: Any
        The JSON-serializable input to pass to the activity function.

    Returns
    -------
    Task
        A Durable Task that completes when the called entity completes or fails.
    """
    new_action = CallEntityAction(entity_id, operation_name, input_)
    scheduler_id = EntityId.get_scheduler_id(entity_id=entity_id)

    hist_type = HistoryEventType.EVENT_SENT
    extra_constraints = {
        "InstanceId": scheduler_id,
        "Name": "op"
    }
    event_sent = find_event(state, hist_type, extra_constraints)

    event_raised = None
    if event_sent:
        event_input = None
        if hasattr(event_sent, "Input"):
            event_input = RequestMessage.from_json(event_sent.Input)
            hist_type = HistoryEventType.EVENT_RAISED
            extra_constraints = {
                "Name": event_input.id
            }
            event_raised = find_event(state, hist_type, extra_constraints)
        # TODO: does it make sense to have an event_sent but no `Input` attribute ?
        # If not, we should raise an exception here

    set_processed([event_sent, event_raised])
    if event_raised is not None:
        response = parse_history_event(event_raised)
        response = ResponseMessage.from_dict(response)

        # TODO: json.loads inside parse_history_event is not recursive
        #       investigate if response.result is used elsewhere,
        #       which probably requires another deserialization
        result = json.loads(response.result)

        return Task(
            is_completed=True,
            is_faulted=False,
            action=new_action,
            result=result,
            timestamp=event_raised.timestamp,
            id_=event_raised.Name)  # event_raised.TaskScheduledId

    # TODO: this may be missing exception handling, as is JS
    return Task(is_completed=False, is_faulted=False, action=new_action)
