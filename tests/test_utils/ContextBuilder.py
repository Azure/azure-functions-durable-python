import uuid
from typing import List, Any, Dict


from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType

def add_attrib(json_dict: Dict[str, Any], object_, attribute_name: str, alt_name: str = None):
    if hasattr(object_, 'actionType'):
        json_dict[alt_name or attribute_name] = getattr(object_, attribute_name)


class ContextBuilder:
    def __init__(self):
        self.instance_id = uuid.uuid4()
        self.is_replaying: bool = True
        self.history_events: List[HistoryEvent] = []

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'instance_id', 'instanceId')
        add_attrib(json_dict, self, 'parent_instance_id', 'parentInstanceId')
        add_attrib(json_dict, self, 'is_replaying', 'isReplaying')
        add_attrib(json_dict, self, 'input')



        return json_dict


    def convert_history_event_to_json_dict(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'EventId')
        add_attrib(json_dict, self, 'EventType')
        add_attrib(json_dict, self, 'IsPlayed')
        add_attrib(json_dict, self, 'Timestamp')


        return json_dict