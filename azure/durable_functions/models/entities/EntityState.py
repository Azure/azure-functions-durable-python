from typing import List, Optional
from .Signal import Signal
from .OperationResult import OperationResult

class EntityState:
    def __init__(self,
                 results: List[OperationResult],
                 signals: List[Signal],
                 entity_exists: bool = False,
                 state: Optional[str] = None):
        self.entity_exists = entity_exists
        self.state = state
        self._results = results
        self._signals = signals

    @property
    def results(self) -> List[OperationResult]:
        return self._results
    
    @property
    def signals(self) -> List[Signal]:
        return self._signals