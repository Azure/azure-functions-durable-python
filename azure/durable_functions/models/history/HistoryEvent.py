from datetime import datetime
from .HistoryEventType import HistoryEventType


class HistoryEvent:
    def __init__(self):
        self.EventType: HistoryEventType
        self.EventId: int
        self.IsPlayed: bool
        self.Timestamp: datetime
        self.IsProcessed: bool = False
