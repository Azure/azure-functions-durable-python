import datetime
from dateutil.parser import parse as dt_parse
from .HistoryEventType import HistoryEventType


class HistoryEvent:
    """Used to communicate state relevant information from the durable extension to the client."""

    # noinspection PyPep8Naming
    def __init__(self, EventType: HistoryEventType, EventId: int, IsPlayed: bool, Timestamp: str,
                 **kwargs):
        self._event_type: HistoryEventType = EventType
        self._event_id: int = EventId
        self._is_played: bool = IsPlayed
        self._timestamp: datetime = dt_parse(Timestamp)
        self._is_processed: bool = False
        if kwargs is not None:
            [self.__setattr__(key, value) for key, value in kwargs.items()]

    @property
    def event_type(self) -> HistoryEventType:
        """Get the history event type

        Returns
        ----------
        HistoryEventType: The type of history event

        """
        return self._event_type

    @property
    def event_id(self) -> int:
        return self._event_id

    @property
    def is_played(self) -> bool:
        return self._is_played

    @property
    def is_processed(self) -> bool:
        return self._is_processed

    @is_processed.setter
    def is_processed(self, value: bool):
        self._is_processed = value

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
