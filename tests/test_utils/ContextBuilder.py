import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .json_utils import add_attrib, convert_history_event_to_json_dict
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from tests.orchestrator.models.OrchestrationInstance \
    import OrchestrationInstance
from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.models.history.HistoryEventType \
    import HistoryEventType


class ContextBuilder:
    def __init__(self, name: str):
        self.instance_id = uuid.uuid4()
        self.is_replaying: bool = False
        self.input_ = None
        self.parent_instance_id = None
        self.history_events: List[HistoryEvent] = []
        self.current_datetime: datetime = datetime.now()
        self.add_orchestrator_started_event()
        self.add_execution_started_event(name)

    def get_base_event(
            self, event_type: HistoryEventType, id_: int = -1,
            is_played: bool = False, timestamp=None) -> HistoryEvent:
        self.current_datetime = self.current_datetime + timedelta(seconds=1)
        if not timestamp:
            timestamp = self.current_datetime
        event = HistoryEvent(EventType=event_type, EventId=id_,
                             IsPlayed=is_played,
                             Timestamp=timestamp.strftime(DATETIME_STRING_FORMAT))

        return event

    def add_orchestrator_started_event(self):
        event = self.get_base_event(HistoryEventType.ORCHESTRATOR_STARTED)
        self.history_events.append(event)

    def add_orchestrator_completed_event(self):
        event = self.get_base_event(HistoryEventType.ORCHESTRATOR_COMPLETED)
        self.history_events.append(event)

    def add_task_scheduled_event(
            self, name: str, id_: int, version: str = '', input_=None):
        event = self.get_base_event(HistoryEventType.TASK_SCHEDULED, id_=id_)
        event.Name = name
        event.Version = version
        event.Input_ = input_
        self.history_events.append(event)

    def add_task_completed_event(self, id_: int, result):
        event = self.get_base_event(HistoryEventType.TASK_COMPLETED)
        event.Result = result
        event.TaskScheduledId = id_
        self.history_events.append(event)

    def add_task_failed_event(self, id_: int, reason: str, details: str):
        event = self.get_base_event(HistoryEventType.TASK_FAILED)
        event.Reason = reason
        event.Details = details
        event.TaskScheduledId = id_
        self.history_events.append(event)

    def add_timer_created_event(self, id_: int):
        fire_at = self.current_datetime.strftime(DATETIME_STRING_FORMAT)
        event = self.get_base_event(HistoryEventType.TIMER_CREATED, id_=id_)
        event.FireAt = fire_at
        self.history_events.append(event)
        return fire_at

    def add_timer_fired_event(self, id_: int, fire_at: str):
        event = self.get_base_event(HistoryEventType.TIMER_FIRED, is_played=True)
        event.TimerId = id_
        event.FireAt = fire_at
        self.history_events.append(event)

    def add_execution_started_event(
            self, name: str, version: str = '', input_=None):
        event = self.get_base_event(HistoryEventType.EXECUTION_STARTED, is_played=True)
        event.orchestration_instance = OrchestrationInstance()
        self.instance_id = event.orchestration_instance.instance_id
        event.Name = name
        event.Version = version
        event.Input = input_
        self.history_events.append(event)

    def add_event_raised_event(self, name: str, id_: int, input_=None, timestamp=None):
        event = self.get_base_event(HistoryEventType.EVENT_RAISED, id_=id_, timestamp=timestamp)
        event.Name = name
        event.Input = input_
        # event.timestamp = timestamp
        self.history_events.append(event)

    def to_json(self, **kwargs) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'instance_id', 'instanceId')
        add_attrib(json_dict, self, 'parent_instance_id', 'parentInstanceId')
        add_attrib(json_dict, self, 'is_replaying', 'isReplaying')
        add_attrib(json_dict, self, 'input_', "input")

        history_list_as_dict = self.get_history_list_as_dict()
        json_dict['history'] = history_list_as_dict

        if kwargs is not None:
            for key, value in kwargs.items():
                json_dict[key] = value

        return json_dict

    def get_history_list_as_dict(self) -> List[Dict[str, Any]]:
        history_list = []

        for history_event in self.history_events:
            event_as_dict = convert_history_event_to_json_dict(history_event)
            history_list.append(event_as_dict)

        return history_list

    def to_json_string(self, **kwargs) -> str:
        json_dict = self.to_json(**kwargs)

        return json.dumps(json_dict)
