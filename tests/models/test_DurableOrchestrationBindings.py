import pytest
from azure.durable_functions.models.DurableOrchestrationBindings import DurableOrchestrationBindings


@pytest.mark.parametrize("sample_input, expected_task_hub_name", {(
        '{"taskHubName":"hub1"}',
        "hub1")})
def test_task_hub_parsed(sample_input, expected_task_hub_name):
    binding = DurableOrchestrationBindings(sample_input)
    assert expected_task_hub_name == binding.task_hub_name


@pytest.mark.parametrize("sample_input, test_url, expected_value", {(
        '{"taskHubName":"hub1", "creationUrls": {"a": "b", "c": "d"}}', "a",
        "b")})
def test_task_hub_parsed(sample_input, test_url, expected_value):
    binding = DurableOrchestrationBindings(sample_input)
    assert expected_value == binding.creation_urls[test_url]
