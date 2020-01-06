import pytest
from azure.durable_functions.models.DurableOrchestrationBindings import DurableOrchestrationBindings


TASK_HUB_NAME = "DurableFunctionsHub"
BASE_URL = "http://localhost:7071/runtime/webhooks/durabletask"
AUTH_CODE = "GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg=="


def get_binding_string():
    binding_string = '{"taskHubName":"TASK_HUB_NAME","creationUrls":{' \
                     '"createNewInstancePostUri":"BASE_URL/orchestrators/{functionName}[/{' \
                     'instanceId}]?code=AUTH_CODE","createAndWaitOnNewInstancePostUri":"BASE_URL/orchestrators/{' \
                     'functionName}[/{instanceId}]?timeout={timeoutInSeconds}&pollingInterval={' \
                     'intervalInSeconds}&code=AUTH_CODE"},"managementUrls":{"id":"INSTANCEID",' \
                     '"statusQueryGetUri":"BASE_URL/instances/INSTANCEID?taskHub=TASK_HUB_NAME&connection' \
                     '=Storage&code=AUTH_CODE","sendEventPostUri":"BASE_URL/instances/INSTANCEID/raiseEvent/{' \
                     'eventName}?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",' \
                     '"terminatePostUri":"BASE_URL/instances/INSTANCEID/terminate?reason={' \
                     'text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",' \
                     '"rewindPostUri":"BASE_URL/instances/INSTANCEID/rewind?reason={' \
                     'text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",' \
                     '"purgeHistoryDeleteUri":"BASE_URL/instances/INSTANCEID?taskHub=TASK_HUB_NAME&connection' \
                     '=Storage&code=AUTH_CODE"}}'

    binding_string = replace_stand_in_bits(binding_string)
    return binding_string


@pytest.fixture()
def binding_string():
    return get_binding_string()


@pytest.fixture()
def binding_info():
    binding = DurableOrchestrationBindings(get_binding_string())
    return binding


def replace_stand_in_bits(binding_string):
    binding_string = binding_string.replace("TASK_HUB_NAME", TASK_HUB_NAME)
    binding_string = binding_string.replace("BASE_URL", BASE_URL)
    binding_string = binding_string.replace("AUTH_CODE", AUTH_CODE)
    return binding_string
