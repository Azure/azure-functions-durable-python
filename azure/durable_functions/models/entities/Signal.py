from ..utils.entity_utils import EntityId

class Signal:
    def __init__(self,
                 target: EntityId,
                 name: str,
                 input_: str):
        self._target = target
        self._name = name
        self._input = input_

    @property
    def target(self) -> EntityId:
        return self._target
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def input(self) -> str:
        return self._input