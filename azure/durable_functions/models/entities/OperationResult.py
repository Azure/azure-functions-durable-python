from typing import Optional

class OperationResult: #  inherit from orch state?
    def __init__(self,
                 is_error: bool,
                 duration: int,
                 result: Optional[str] = None):
        self._is_error: bool = is_error
        self._duration: int =  duration
        self._result: Optional[str] = result
        
    @property
    def is_error(self):
        return self._is_error
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def result(self):
        return self._result