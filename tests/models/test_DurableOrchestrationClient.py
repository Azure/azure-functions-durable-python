import json

from azure.durable_functions.models.DurableOrchestrationClient \
    import DurableOrchestrationClient
from tests.conftest import replace_stand_in_bits, binding_string


def test_get_start_new_url(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "abc123"
    function_name = "myfunction"
    start_new_url = client._get_start_new_url(instance_id, function_name)
    expected_url = replace_stand_in_bits(
        f"BASE_URL/orchestrators/{function_name}/{instance_id}?code=AUTH_CODE")
    assert expected_url == start_new_url


def test_get_input_returns_none_when_none_supplied():
    result = DurableOrchestrationClient._get_json_input(None)
    assert result is None


def test_get_input_returns_json_string(binding_string):
    input_ = json.loads(binding_string)
    result = DurableOrchestrationClient._get_json_input(input_)
    input_as_string = json.dumps(input_)
    assert input_as_string == result
