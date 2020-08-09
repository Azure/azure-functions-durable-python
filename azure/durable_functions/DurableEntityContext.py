from typing import Optional, Any
from .models.utils.entity_utils import EntityId
from .models.entities import EntityState, OperationResult
from azure.functions._durable_functions import _deserialize_custom_object
from datetime import datetime
import json

class DurableEntityContext:

    def __init__(self,
                 entity_name: str,
                 entity_key: str,
                 entity_id: EntityId,
                 operation_name: Optional[str],
                 is_newly_constructed: bool):
        self._entity_name: str = entity_name
        self._entity_key: str = entity_key
        self._operation_name: str = operation_name
        self._is_newly_constructed: bool = is_newly_constructed
        # TODO: the name _entity_state is very confusing
        self._entity_state: EntityState = EntityState(results=[], signals=[])
        self.curr_req = None # TODO: we need to figure out this one, also better naming

    @property
    def entity_name(self):
        return self._entity_name
    
    @property
    def entity_key(self):
        return self._entity_key
    
    @property
    def operation_name(self):
        return self._operation_name
    
    @property
    def is_newly_constructed(self):
        return self._is_newly_constructed

    @classmethod
    def from_json(cls, json_str: str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

    def set_state(self, state: Any) -> None:
        self._entity_state.entity_exists = True
        self._entity_state.entity_state = json.dumps(state)

    def get_input(self) -> Any:
        input_ = None
        req_input = self.curr_req.input
        input_ = None if req_input is None else self.from_json_util(req_input)
        return input_
    
    def set_result(self, start_time: datetime, result: Any) -> None:
        self._entity_state.entity_exists = True
        # TODO: the helper below should be in a utils file 
        duration = self._elapsed_milliseconds_since(start_time)
        new_result = OperationResult(
            is_error=False,
            duration=duration,
            result=result)
        self._entity_state.results.append(new_result)
    
    def destruct_on_exit(self) -> None:
        self._entity_state.entity_exists = False
        self._entity_state.entity_state = None
    
    def _elapsed_milliseconds_since(self, start_time: datetime):
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        # TODO: double-check this is a milliseconds diff
        return elapsed_time
    
    def from_json_util(self, json_str):
        # TODO: this should be a util elsewhere
        return json.loads(json_str, object_hook=_deserialize_custom_object)
