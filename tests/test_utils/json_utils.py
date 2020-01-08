from typing import Any, Dict

from azure.durable_functions.models.history.HistoryEvent import HistoryEvent


def add_attrib(json_dict: Dict[str, Any], object_, attribute_name: str, alt_name: str = None):
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = getattr(object_, attribute_name)


def add_json_attrib(json_dict: Dict[str, Any], object_, attribute_name: str, alt_name: str = None):
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = getattr(object_, attribute_name).to_json()


def convert_history_event_to_json_dict(history_event: HistoryEvent) -> Dict[str, Any]:
    json_dict = {}

    add_attrib(json_dict, history_event, 'EventId')
    add_attrib(json_dict, history_event, 'EventType')
    add_attrib(json_dict, history_event, 'IsPlayed')
    add_attrib(json_dict, history_event, 'Timestamp')
    add_attrib(json_dict, history_event, 'input_', 'Input')
    add_attrib(json_dict, history_event, 'reason', 'Reason')
    add_attrib(json_dict, history_event, 'result', 'Result')
    add_attrib(json_dict, history_event, 'version', 'Version')
    add_attrib(json_dict, history_event, 'task_scheduled_id', 'TaskScheduledId')
    add_attrib(json_dict, history_event, 'tags', 'Tags')
    add_attrib(json_dict, history_event, 'name', 'Name')
    add_json_attrib(json_dict, history_event, 'orchestration_instance', 'OrchestrationInstance')

    return json_dict
