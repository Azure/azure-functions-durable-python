from typing import List, Any, Optional
from ..models.actions.SignalEntityAction import SignalEntityAction
from ..models.history import HistoryEvent, HistoryEventType
from .task_utilities import set_processed, find_event
from ..models.utils.entity_utils import EntityId


def signal_entity_task(
        context,
        state: List[HistoryEvent],
        entity_id: EntityId,
        operation_name: str = "",
        input_: Optional[Any] = None):
    """Signal a entity operation.

    It the action hasn't been scheduled, it appends the action.
    If the action has been scheduled, no ops.

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
    """
    new_action = SignalEntityAction(entity_id, operation_name, input_)
    scheduler_id = EntityId.get_scheduler_id(entity_id=entity_id)

    hist_type = HistoryEventType.EVENT_SENT
    extra_constraints = {
        "InstanceId": scheduler_id,
        "Name": "op"
    }

    event_sent = find_event(state, hist_type, extra_constraints)
    set_processed([event_sent])
    context.actions.append([new_action])

    if event_sent:
        return
