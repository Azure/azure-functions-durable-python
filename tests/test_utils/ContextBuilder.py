import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .json_utils import add_attrib, convert_history_event_to_json_dict
from .constants import DATETIME_STRING_FORMAT
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
            self, event_type: HistoryEventType, id_: int = -1) -> HistoryEvent:
        self.current_datetime = self.current_datetime + timedelta(seconds=1)
        event = HistoryEvent()
        event.EventId = id_
        event.EventType = event_type
        event.IsPlayed = False
        event.Timestamp = \
            self.current_datetime.strftime(DATETIME_STRING_FORMAT)
        return event

    def add_orchestrator_started_event(self):
        event = self.get_base_event(HistoryEventType.OrchestratorStarted)
        self.history_events.append(event)

    def add_orchestrator_completed_event(self):
        event = self.get_base_event(HistoryEventType.OrchestratorCompleted)
        self.history_events.append(event)

    def add_task_scheduled_event(
            self, name: str, id_: int, version: str = '', input_=None):
        event = self.get_base_event(HistoryEventType.TaskScheduled, id_=id_)
        event.name = name
        event.version = version
        event.input_ = input_
        self.history_events.append(event)

    def add_task_completed_event(self, id_: int, result):
        event = self.get_base_event(HistoryEventType.TaskCompleted)
        event.result = result
        event.task_scheduled_id = id_
        self.history_events.append(event)

    def add_task_failed_event(self, id_: int, reason: str, details: str):
        event = self.get_base_event(HistoryEventType.TaskFailed)
        event.reason = reason
        event.details = details
        event.task_scheduled_id = id_
        self.history_events.append(event)

    def add_timer_created_event(self, id_: int):
        fire_at = self.current_datetime.strftime(DATETIME_STRING_FORMAT)
        event = self.get_base_event(HistoryEventType.TimerCreated, id_=id_)
        event.fire_at = fire_at
        self.history_events.append(event)
        return fire_at

    def add_timer_fired_event(self, id_: int, fire_at: str):
        event = self.get_base_event(HistoryEventType.TimerFired)
        event.timer_id = id_
        event.fire_at = fire_at
        event.IsPlayed = True
        self.history_events.append(event)

    def add_execution_started_event(
            self, name: str, version: str = '', input_=None):
        event = self.get_base_event(HistoryEventType.ExecutionStarted)
        event.orchestration_instance = OrchestrationInstance()
        self.instance_id = event.orchestration_instance.instance_id
        event.name = name
        event.version = version
        event.input_ = input_
        event.IsPlayed = True
        self.history_events.append(event)

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'instance_id', 'instanceId')
        add_attrib(json_dict, self, 'parent_instance_id', 'parentInstanceId')
        add_attrib(json_dict, self, 'is_replaying', 'isReplaying')
        add_attrib(json_dict, self, 'input_')

        history_list_as_dict = self.get_history_list_as_dict()
        json_dict['history'] = history_list_as_dict

        return json_dict

    def get_history_list_as_dict(self) -> List[Dict[str, Any]]:
        history_list = []

        for history_event in self.history_events:
            event_as_dict = convert_history_event_to_json_dict(history_event)
            history_list.append(event_as_dict)

        return history_list

    def to_json_string(self) -> str:
        json_dict = self.to_json()

        return json.dumps(json_dict)
