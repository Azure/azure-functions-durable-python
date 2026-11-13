import copy
import json
from unittest.mock import AsyncMock
from urllib.parse import urlsplit

import azure.functions as func
import pytest

from azure.durable_functions.models.DurableOrchestrationBindings import (
    DurableOrchestrationBindings)
from azure.durable_functions.models.DurableOrchestrationClient import (
    DurableOrchestrationClient)


BASE_URL = "https://notification.test/runtime/webhooks/durabletask"
QUERIES = [
    "taskHub=hub&connection=storage&code=synthetic-INSTANCEID%2Bkey%2F%3D",
    "CoDe=synthetic-INSTANCEID%2Bkey%2F%3D&site=value%2Bone",
    "%63ode=synthetic-INSTANCEID%2Bkey%2F%3D&CODE=duplicate",
    "taskHub=hub&connection=storage",
    "",
]


def binding(query):
    suffix = "?" + query if query else ""
    reason = "?reason={text}" + ("&" + query if query else "")
    return {
        "taskHubName": "hub",
        "rpcBaseUrl": "http://rpc.test/durabletask/",
        "creationUrls": {
            "createNewInstancePostUri":
                BASE_URL + "/orchestrators/{functionName}[/{instanceId}]" + suffix,
        },
        "managementUrls": {
            "id": "INSTANCEID",
            "statusQueryGetUri": BASE_URL + "/instances/INSTANCEID" + suffix,
            "sendEventPostUri":
                BASE_URL + "/instances/INSTANCEID/raiseEvent/{eventName}" + suffix,
            "terminatePostUri": BASE_URL + "/instances/INSTANCEID/terminate" + reason,
        },
    }


@pytest.mark.parametrize("query", QUERIES)
def test_binding_preserves_host_urls_and_query_strings(query):
    data = binding(query)
    original = copy.deepcopy(data)
    bindings = DurableOrchestrationBindings(**data)

    assert bindings.creation_urls == data["creationUrls"]
    assert bindings.management_urls == data["managementUrls"]
    assert data == original


@pytest.mark.parametrize("query", QUERIES)
def test_response_preserves_host_query_and_string_only_payload(query):
    data = binding(query)
    original = copy.deepcopy(data)
    client = DurableOrchestrationClient(json.dumps(data))
    request = func.HttpRequest(
        "GET", "https://frontend.test/api/start?code=starter-key", body=b"")

    response = client.create_check_status_response(request, "instance")
    payload = json.loads(response.get_body())

    expected = {
        key: value.replace("https://notification.test/", "https://frontend.test/")
        .replace("INSTANCEID", "instance", 1)
        for key, value in data["managementUrls"].items()
    }
    assert response.status_code == 202
    assert response.headers["Location"] == payload["statusQueryGetUri"]
    assert response.headers["Retry-After"] == "10"
    assert payload == expected
    assert all(isinstance(value, str) for value in payload.values())
    assert "requiredHeaders" not in payload
    assert "starter-key" not in json.dumps(payload)
    assert "{eventName}" in payload["sendEventPostUri"]
    assert data == original


@pytest.mark.parametrize("query", QUERIES)
def test_payload_instances_do_not_modify_the_binding(query):
    data = binding(query)
    original = copy.deepcopy(data)
    client = DurableOrchestrationClient(json.dumps(data))
    first = client.create_http_management_payload("first")
    first["statusQueryGetUri"] = "changed"
    second = client.create_http_management_payload("second")

    assert second["id"] == "second"
    assert second["statusQueryGetUri"] == \
        data["managementUrls"]["statusQueryGetUri"].replace("INSTANCEID", "second", 1)
    assert data == original


@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.asyncio
async def test_management_uses_rpc_without_public_key_credentials(query):
    client = DurableOrchestrationClient(json.dumps(binding(query)))
    client._post_async_request = AsyncMock(return_value=[202, {"id": "instance"}])

    assert await client.start_new("Allowed", "instance") == "instance"

    args, kwargs = client._post_async_request.await_args
    assert args[0] == "http://rpc.test/durabletask/orchestrators/Allowed/instance"
    assert "headers" not in kwargs
    assert "code" not in urlsplit(args[0]).query
    assert "synthetic" not in str((args, kwargs))
