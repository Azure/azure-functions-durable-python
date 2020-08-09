from typing import List, Any, Optional

from ..models.Task import (
    Task)
from ..models.actions.CallEntityAction import CallEntityAction
from ..models.history import HistoryEvent, HistoryEventType
from .task_utilities import set_processed, parse_history_event, find_event
from ..models.utils.entity_utils import EntityId
from ..models.entities.RequestMessage import RequestMessage


def call_entity_task(
        state: List[HistoryEvent],
        entity_id: EntityId,
        operation_name: str = "",
        input_: Optional[Any] = None):
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
        if hasattr(event_input, "Input"):
            # TODO: we may need to create a superclass specialization constructor
            event_input = RequestMessage(event_sent.Input)
            hist_type = HistoryEventType.EVENT_RAISED
            extra_constraints = {
                "Name": event_input.id
            }
            event_raised = find_event(state, hist_type, extra_constraints)
        # TODO: does it make sense to have an event_sent but no `Input` attribute ??
        # If not, we should raise an exception here

    set_processed([event_sent, event_raised])
    if event_raised is not None:
        return Task(
            is_completed=True,
            is_faulted=False,
            action=new_action,
            result=parse_history_event(event_raised),
            timestamp=event_raised.timestamp,
            id_=event_raised.TaskScheduledId)

    # TODO: this may be missing exception handling, as is JS
    return Task(is_completed=False, is_faulted=False, action=new_action)