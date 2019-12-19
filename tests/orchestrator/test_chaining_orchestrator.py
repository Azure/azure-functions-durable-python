import pytest
import json

from azure.durable_functions.orchestrator import Orchestrator
from tests.orchestrator.chaining_context import *


def generator_function(context):
    outputs = []

    task1 = yield context.df.callActivity("Hello", "Tokyo")
    task2 = yield context.df.callActivity("Hello", "Seattle")
    task3 = yield context.df.callActivity("Hello", "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


@pytest.mark.parametrize("context, output_state",
                         [(HANDLE_ONE, STATE_ONE),
                          (HANDLE_TWO, STATE_TWO),
                          (HANDLE_THREE, STATE_THREE),
                          (HANDLE_FOUR, STATE_FOUR)])
def test_orchestration_state_output(context, output_state):
    orchestrator = Orchestrator(generator_function)
    result = json.loads(orchestrator.handle(context))
    expected = json.loads(output_state)
    assert_attribute_equal(expected, result, "isDone")
    assert_actions_are_equal(expected, result)
    assert_attribute_equal(expected, result, "output")
    assert_attribute_equal(expected, result, "error")
    assert_attribute_equal(expected, result, "customStatus")


def assert_attribute_equal(expected, result, attribute):
    if hasattr(expected, attribute):
        assert expected.get(attribute) == result.get(attribute)
    else:
        assert not hasattr(result, attribute)


def assert_actions_are_equal(expected, result):
    expected_actions = expected.get("actions")
    result_actions = result.get("actions")
    assert len(expected_actions) == len(result_actions)
    for index in range(len(expected_actions)):
        assert expected_actions[index][0]["functionName"] == result_actions[index][0]["functionName"]
        assert expected_actions[index][0]["input"] == result_actions[index][0]["input"]
        assert expected_actions[index][0]["actionType"] == result_actions[index][0]["actionType"]
