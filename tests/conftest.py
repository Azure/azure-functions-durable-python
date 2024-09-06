import pytest
import json

import azure.durable_functions as df
import azure.functions as func
from tests.test_utils.constants import RPC_BASE_URL
from azure.durable_functions.models.DurableOrchestrationBindings import \
    DurableOrchestrationBindings

TASK_HUB_NAME = "DurableFunctionsHub"
BASE_URL = "http://localhost:7071/runtime/webhooks/durabletask"
AUTH_CODE = "NOT-REAL-AUTH"


def get_binding_string():
    binding = {
        "taskHubName": TASK_HUB_NAME,
        "creationUrls": {
            "createNewInstancePostUri": f"{BASE_URL}/orchestrators/"
                                        "{functionName}[/{instanceId}]?code="
                                        f"{AUTH_CODE}",
            "createAndWaitOnNewInstancePostUri": f"{BASE_URL}/orchestrators/"
                                                 "{functionName}[/{instanceId}]?timeout="
                                                 "{timeoutInSeconds}&pollingInterval="
                                                 "{intervalInSeconds}&code="
                                                 f"{AUTH_CODE}"
        },
        "managementUrls": {
            "id": "INSTANCEID",
            "statusQueryGetUri": f"{BASE_URL}/instances/INSTANCEID?taskHub=DurableFunctionsHub&"
                                 f"connection=Storage&code={AUTH_CODE}",
            "sendEventPostUri": f"{BASE_URL}/instances/INSTANCEID/raiseEvent/"
                                "{eventName}?taskHub="
                                f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
            "terminatePostUri": f"{BASE_URL}/instances/INSTANCEID/terminate?reason="
                                "{text}&taskHub="
                                f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
            "rewindPostUri": f"{BASE_URL}/instances/INSTANCEID/rewind?reason="
                             "{text}&taskHub="
                             f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
            "purgeHistoryDeleteUri": f"{BASE_URL}/instances/INSTANCEID?taskHub="
                                     f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
            "suspendPostUri": f"{BASE_URL}/instances/INSTANCEID/suspend?reason="
                                "{text}&taskHub="
                                f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
            "resumePostUri": f"{BASE_URL}/instances/INSTANCEID/resume?reason="
                                "{text}&taskHub="
                                f"{TASK_HUB_NAME}&connection=Storage&code={AUTH_CODE}",
        },
        "rpcBaseUrl": RPC_BASE_URL
    }
    binding_string = json.dumps(binding)

    binding_string = replace_stand_in_bits(binding_string)
    return binding_string


@pytest.fixture()
def binding_string():
    return get_binding_string()


@pytest.fixture()
def binding_info():
    binding = DurableOrchestrationBindings.from_json(get_binding_string())
    return binding


def replace_stand_in_bits(binding_string):
    binding_string = binding_string.replace("TASK_HUB_NAME", TASK_HUB_NAME)
    binding_string = binding_string.replace("BASE_URL", BASE_URL)
    binding_string = binding_string.replace("AUTH_CODE", AUTH_CODE)
    return binding_string

@pytest.fixture()
def app():
    app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
    return app
