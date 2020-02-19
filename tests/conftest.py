import pytest
from azure.durable_functions.models.DurableOrchestrationBindings import \
    DurableOrchestrationBindings


TASK_HUB_NAME = "DurableFunctionsHub"
BASE_URL = "http://localhost:7071/runtime/webhooks/durabletask"
AUTH_CODE = "iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ=="


def get_binding_string():
    binding_string = '{"taskHubName":"DurableFunctionsHub","creationUrls":{' \
                     '"createNewInstancePostUri":"http://localhost:7071/runtime/webhooks/' \
                     'durabletask/orchestrators/{functionName}[/{instanceId}]?code=' \
                     'iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ==",' \
                     '"createAndWaitOnNewInstancePostUri":"http://localhost:7071/runtime' \
                     '/webhooks/durabletask/orchestrators/{functionName}[/{' \
                     'instanceId}]?timeout={timeoutInSeconds}&pollingInterval={' \
                     'intervalInSeconds}&code=iDFeaQCSAIuXoodl6' \
                     '/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ=="},"managementUrls":{' \
                     '"id":"INSTANCEID",' \
                     '"statusQueryGetUri":"http://localhost:7071/runtime/webhooks/durabletask' \
                     '/instances/INSTANCEID?taskHub=DurableFunctionsHub&connection=Storage&code' \
                     '=iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ==",' \
                     '"sendEventPostUri":"http://localhost:7071/runtime/webhooks/durabletask' \
                     '/instances/INSTANCEID/raiseEvent/{' \
                     'eventName}?taskHub=DurableFunctionsHub&connection=Storage&code' \
                     '=iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ==",' \
                     '"terminatePostUri":"http://localhost:7071/runtime/webhooks/durabletask' \
                     '/instances/INSTANCEID/terminate?reason={' \
                     'text}&taskHub=DurableFunctionsHub&connection=Storage&code' \
                     '=iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ==",' \
                     '"rewindPostUri":"http://localhost:7071/runtime/webhooks/durabletask' \
                     '/instances/INSTANCEID/rewind?reason={' \
                     'text}&taskHub=DurableFunctionsHub&connection=Storage&code' \
                     '=iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ==",' \
                     '"purgeHistoryDeleteUri":"http://localhost:7071/runtime/webhooks' \
                     '/durabletask/instances/INSTANCEID?taskHub=DurableFunctionsHub&connection' \
                     '=Storage&code=iDFeaQCSAIuXoodl6/w3rdvHZ6Nl7yJwRrHfeInNWDJjuiunhxk8dQ=="},' \
                     '"rpcBaseUrl":"http://127.0.0.1:17071/durabletask/"} '

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
