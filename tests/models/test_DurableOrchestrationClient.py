import json

from azure.durable_functions.models.DurableOrchestrationClient \
    import DurableOrchestrationClient
from tests.conftest import replace_stand_in_bits
from tests.test_utils.constants import RPC_BASE_URL
from unittest.mock import Mock


# noinspection PyProtectedMember
def test_get_start_new_url(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "abc123"
    function_name = "my_function"
    start_new_url = client._get_start_new_url(instance_id, function_name)
    expected_url = replace_stand_in_bits(
        f"{RPC_BASE_URL}orchestrators/{function_name}/{instance_id}")
    assert expected_url == start_new_url


# noinspection PyProtectedMember
def test_get_input_returns_none_when_none_supplied():
    result = DurableOrchestrationClient._get_json_input(None)
    assert result is None


# noinspection PyProtectedMember
def test_get_input_returns_json_string(binding_string):
    input_ = json.loads(binding_string)
    result = DurableOrchestrationClient._get_json_input(input_)
    input_as_string = json.dumps(input_)
    assert input_as_string == result


# noinspection PyProtectedMember
def test_get_raise_event_url(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "abc123"
    event_name = "test_event_name"
    task_hub_name = "test_task_hub"
    connection_name = "test_connection"
    raise_event_url = client._get_raise_event_url(instance_id, event_name, task_hub_name,
                                                  connection_name)

    expected_url = replace_stand_in_bits(
        f"{RPC_BASE_URL}instances/{instance_id}/raiseEvent/{event_name}"
        f"?taskHub=test_task_hub&connection=test_connection")

    assert expected_url == raise_event_url


def test_create_check_status_response(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "abc123"
    request = Mock(url="http://test_azure.net/api/orchestrators/DurableOrchestrationTrigger")
    returned_response = client.create_check_status_response(request, instance_id)

    http_management_payload = {
        "id": "abc123",
        "statusQueryGetUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/abc123?taskHub"
            r"=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "sendEventPostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/abc123/raiseEvent/{"
            r"eventName}?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "terminatePostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/abc123/terminate"
            r"?reason={text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "rewindPostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/abc123/rewind?reason"
            r"={text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "purgeHistoryDeleteUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"abc123?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE"
    }
    for key, _ in http_management_payload.items():
        http_management_payload[key] = replace_stand_in_bits(http_management_payload[key])
    expected_response = {
        "status_code": 202,
        "body": json.dumps(http_management_payload),
        "headers": {
            "Content-Type": "application/json",
            "Location": http_management_payload["statusQueryGetUri"],
            "Retry-After": "10",
        },
    }

    for k, v in expected_response.get("headers").items():
        assert v == returned_response.headers.get(k)
    assert expected_response.get("status_code") == returned_response.status_code
    assert expected_response.get("body") == returned_response.get_body().decode()
