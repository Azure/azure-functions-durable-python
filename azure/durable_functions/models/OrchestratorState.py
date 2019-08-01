import json
from typing import List, Any, Dict


class OrchestratorState:
    def __init__(self,
                 isDone: bool,
                 actions: List[List[Any]],
                 output: Any,
                 error: str = None,
                 customStatus: Any = None):
        self.isDone: bool = isDone
        self.actions: List[List[Any]] = actions
        self.output: Any = output
        self.error: str = error
        self.customStatus: Any = customStatus

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}
        json_dict['isDone'] = self.isDone
        json_dict['actions'] = []
        for action_list in self.actions:
            action_result_list = []
            for action_obj in action_list:
                action_dict = {}
                if hasattr(action_obj, 'actionType'):
                    action_dict['actionType'] = action_obj.actionType
                if hasattr(action_obj, 'functionName'):
                    action_dict['functionName'] = action_obj.functionName
                if hasattr(action_obj, 'input'):
                    action_dict['input'] = action_obj.input

                action_result_list.append(action_dict)
            json_dict['actions'].append(action_result_list)
        json_dict['output'] = self.output
        json_dict['error'] = self.error
        json_dict['customStatus'] = self.customStatus
        return json_dict

    def to_json_string(self) -> str:
        json_dict = self.to_json()
        return json.dumps(json_dict)
