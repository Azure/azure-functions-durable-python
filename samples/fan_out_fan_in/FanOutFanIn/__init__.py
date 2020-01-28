import json
import azure.durable_functions as df


def generator_function(context):
    activity_count = yield context.df.call_activity("GetActivityCount", 5)
    activity_list = json.loads(activity_count)

    tasks = [context.df.call_activity("ParrotValue", i) for i in activity_list]
        
    tasks_result = yield context.df.task_all(tasks)
    values = [int(t) for t in tasks_result]
    message = yield context.df.call_activity("ShowMeTheSum", values)

    return message


def main(context: str):
    orchestrate = df.Orchestrator.create(generator_function)

    result = orchestrate(context)

    return result



class HistoryEvent:
    """Used to communicate state relevant information from the durable extension to the client."""

    # noinspection PyPep8Naming
    def __init__(self, EventType: HistoryEventType, EventId: str, IsPlayed: bool, Timestamp: str):
        self._event_type: HistoryEventType = EventType
        self._event_id: int = EventId
        self._is_played: bool = IsPlayed
        self._timestamp: datetime = dt_parse(Timestamp)
        self._is_processed: bool = False
      

