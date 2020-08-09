from typing import List, Optional, Any
from ..utils.entity_utils import EntityId

class RequestMessage:
    def __init__(self,
                 id_: str,
                 name: Optional[str] = None,
                 signal: Optional[bool] = None,
                 input_: Optional[str] = None,
                 arg: Optional[Any] = None,
                 parent: Optional[str] = None,
                 lockset: Optional[List[EntityId]] = None,
                 pos: Optional[int] = None):
        # TODO: this class has too many optionals, may speak to
        # over-caution, but it mimics the JS class. Investigate if
        # these many Optionals are necessary.
        self.id: id_ 
        self.name: name
        self.signal: signal
        self.input: input_
        self.arg: arg
        self.parent: parent
        self.lockset: lockset
        self.pos: pos