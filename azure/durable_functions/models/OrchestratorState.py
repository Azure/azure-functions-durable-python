import json
from typing import List, Any, Dict
from .utils.json_utils import add_attrib


class OrchestratorState:
    def __init__(self,
                 is_done: bool,
                 actions: List[List[Any]],
                 output: Any,
                 error: str = None,
                 custom_status: Any = None):
        self.is_done: bool = is_done
        self.actions: List[List[Any]] = actions
        self.output: Any = output
        self.error: str = error
        self.custom_status: Any = custom_status

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}
        add_attrib(json_dict, self, 'is_done', 'isDone')
        self.add_actions(json_dict)
        if self.output:
            json_dict['output'] = self.output
        if self.error:
            json_dict['error'] = self.error
        if self.custom_status:
            json_dict['customStatus'] = self.custom_status
        return json_dict

    def add_actions(self, json_dict):
        json_dict['actions'] = []
        for action_list in self.actions:
            action_result_list = []
            for action_obj in action_list:
                action_result_list.append(action_obj.to_json())
            json_dict['actions'].append(action_result_list)

    def to_json_string(self) -> str:
        json_dict = self.to_json()
        return json.dumps(json_dict)
