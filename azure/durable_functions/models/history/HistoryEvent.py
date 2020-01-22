from .HistoryEventType import HistoryEventType


class HistoryEvent:
    """Used to communicate state relevant information from the durable extension to the client."""

    def __init__(self):
        self.EventType: HistoryEventType
        self.EventId: int
        self.IsPlayed: bool
        self.Timestamp: str
        self.IsProcessed: bool = False
