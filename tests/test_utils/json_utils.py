from typing import Any, Dict

from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.models.utils.json_utils \
    import add_attrib, add_json_attrib


def convert_history_event_to_json_dict(
        history_event: HistoryEvent) -> Dict[str, Any]:
    json_dict = {}

    add_attrib(json_dict, history_event, 'EventId')
    add_attrib(json_dict, history_event, 'EventType')
    add_attrib(json_dict, history_event, 'IsPlayed')
    add_attrib(json_dict, history_event, 'Timestamp')
    add_attrib(json_dict, history_event, 'input_', 'Input')
    add_attrib(json_dict, history_event, 'reason', 'Reason')
    add_attrib(json_dict, history_event, 'details', 'Details')
    add_attrib(json_dict, history_event, 'result', 'Result')
    add_attrib(json_dict, history_event, 'version', 'Version')
    add_attrib(json_dict, history_event, 'retry_options', 'retryOptions')
    add_attrib(json_dict, history_event,
               'task_scheduled_id', 'TaskScheduledId')
    add_attrib(json_dict, history_event, 'tags', 'Tags')
    add_attrib(json_dict, history_event, 'fire_at', 'FireAt')
    add_attrib(json_dict, history_event, 'timer_id', 'TimerId')
    add_attrib(json_dict, history_event, 'name', 'Name')
    add_json_attrib(json_dict, history_event,
                    'orchestration_instance', 'OrchestrationInstance')

    return json_dict
