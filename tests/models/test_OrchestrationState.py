from typing import List

from azure.durable_functions.interfaces.IAction import IAction
from azure.durable_functions.models.actions.CallActivityAction import (
    CallActivityAction,
)
from azure.durable_functions.models.OrchestratorState import OrchestratorState


def test_empty_state_to_json_string():
    actions: List[List[IAction]] = []
    state = OrchestratorState(
        is_done=False,
        actions=actions,
        output=None,
        error=None,
        custom_status=None,
    )
    result = state.to_json_string()
    expected_result = '{"isDone": false, "actions": []}'
    assert expected_result == result


def test_single_action_state_to_json_string():
    actions: List[List[IAction]] = []
    action: IAction = CallActivityAction(
        function_name="MyFunction", input_="AwesomeInput"
    )
    actions.append([action])
    state = OrchestratorState(
        is_done=False,
        actions=actions,
        output=None,
        error=None,
        custom_status=None,
    )
    result = state.to_json_string()
    expected_result = (
        '{"isDone": false, "actions": [[{"actionType": 0, '
        '"functionName": "MyFunction", "input": '
        '"AwesomeInput"}]]}'
    )
    assert expected_result == result
