from typing import List, Optional
from . import OperationResult, Signal

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