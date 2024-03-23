# Subscription Creation Workflow with Unit Testing 

This project demonstrates a durable workflow that manages a subscription creation long running lifecyle and is adapted from a canonical
real world example.
The durable orchestration, will create a subscription, wait for the subscription to be created (through the durable timer)
and update status of subscription creation in an in-memory status object.

This also demonstrates usage of:

- EasyAuth using decoraters
- Serialization of custom classes
- Unit Test Methodology

# Durable Orchestration Patterns Used

- Fan In/Fan Out
- Sub Orchestrations
- Function Chaining
- Durable Monitor

# Unit Testing Guide

This example shows how we can unit test durable function patterns using python unittest patch and mock constructs and some noteworthy mocks.

## Unit Testing Durable HTTP Start Invocation with decorators for EasyAuth

The Durable HTTP Starter is invoked with a `X-MS-CLIENT-PRINCIPAL` in the header of the HTTP request. When configuring EasyAuth, the function needs to be validated against the claims presented. This validation is done via an authorize decorator in this sample.

When making an HTTP request to the service (GET or PUT), you can use the following token to act as both a SubscriptionManager (PUT) and a SubscriptionReader (GET):

`ICAgICAgICB7CiAgICAgICAgICAgICJhdXRoX3R5cCI6ICJhYWQiLAogICAgICAgICAgICAiY2xhaW1zIjogW3sKICAgICAgICAgICAgICAgICJ0eXAiOiAiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSIsCiAgICAgICAgICAgICAgICAidmFsIjogIlVzZXIiCiAgICAgICAgICAgIH0sIHsKICAgICAgICAgICAgICAgICJ0eXAiOiAiZ3JvdXBzIiwKICAgICAgICAgICAgICAgICJ2YWwiOiAiZWY2ZDJkMWEtNzhlYi00YmIxLTk3YzctYmI4YThlNTA5ZTljIgogICAgICAgICAgICB9LCB7CiAgICAgICAgICAgICAgICAidHlwIjogImdyb3VwcyIsCiAgICAgICAgICAgICAgICAidmFsIjogIjNiMjMxY2UxLTI5YzEtNDQxZS1iZGRiLTAzM2Y5NjQwMTg4OCIKICAgICAgICAgICAgfSwgewogICAgICAgICAgICAgICAgInR5cCI6ICJuYW1lIiwKICAgICAgICAgICAgICAgICJ2YWwiOiAiVGVzdCBVc2VyIgogICAgICAgICAgICB9XSwKICAgICAgICAgICAgIm5hbWVfdHlwIjogImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiLAogICAgICAgICAgICAicm9sZV90eXAiOiAiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIgogICAgICAgIH0=`

For unit testing the decorator (that get's initialized with a specific environment variable) we just patch in the variable before importing the Durable HTTP Start method like this:

```python
with patch.dict(os.environ={"SecurityGroups_SUBSCRIPTION_MANAGERS":"ef6d2d1a-78eb-4bb1-97c7-bb8a8e509e9c"}):
    from ..CreateEnvironmentHTTPStart import main
````

and make sure we are sending the right `X-MS-CLIENT-PRINCIPAL` in the header of the mocked HttpRequest as seen in [this](./subscription-manager/tests/test_createenvhttpstart_validauth.py) test.


We are patching the group-id that gets base64 decoded and compared with the above claims principal sent in the header of the http request

Refer [Auth](./subscription-manager/Auth/authorization.py) for details on how this works

---

## Unit Testing Orchestrator Function

When mocking an orchestrator, the durable orchestration context is mocked like this:

```python
with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
            mock.get_input = MagicMock(return_value={'displayName' : 'test'})
            mock.call_sub_orchestrator.side_effect = sub_orc_mock
            mock.task_all.side_effect = task_all_mock
        
            # To get generator results do a next. If orchestrator response is a list, then wrap the function call around a list
            result = list(orchestrator_fn(mock))
            self.assertEqual('51ba2a78-bec0-4f31-83e7-58c64693a6dd',result[0])
```

MagicMock can be used to return a set of canned values, for eg: `get_input` expects a specific dictionary as shown above.

For intercepting any method calls on the mock, we define a `side_effect` that is a local method. For eg: `task_all_mock` side effect checks the list of tasks that it received

```python
def task_all_mock(tasks:list):
    assert len(tasks) == 2
    return list
```

Here we check if we received two tasks and we can go further and use `assertIsInstance` to check what classes the tasks belong to etc.

Finally we invoke the orchestrator as 

```python
result = list(orchestrator_fn(mock))
```

and further inspect the result

---

## Unit Testing Durable Monitor Pattern

Here the durable monitor calls an activity function to get the status of a subscription creation process. Depending upon the status, it will schedule a durable timer to poll again or will proceed further in the orchestration.

To simulate this in the unit test, we might want to send back the results of `call_activity` into the orchestrator and so the orchestrator is invoked in a specific way taking advantage of the generators.

```python
gen_orchestrator = orchestrator_fn(mock)
            try:
                # Make a call to Status check to see and if response is accepted (subscription is in process of being created)
                next(gen_orchestrator)

                # Send back response to orchestrator
                gen_orchestrator.send(accepted_response)

                # Timer is set and now the call succeeds
                next(gen_orchestrator)

                # Send back success response to orchestrator
                gen_orchestrator.send(succeeded_response)

            except StopIteration as e:
                result = e.value
                self.assertEqual('51ba2a78-bec0-4f31-83e7-58c64693a6dd',result)
```

For more details refer [this test that simulates the durable timer calls](./subscription-manager/tests/test_createsubscription_suborchestrator.py).

---

## Unit Testing Callbacks and patching environment variables

If your activity function or orchestrator or any helper methods use environment variables internally, this code below demonstrates how to patch these environment variables in an isolated manner.

```python
# Patch environment variables
patch_env_mock = mock.patch.dict(os.environ, {"RUNTIME_ENVIRONMENT": "LOCAL",
                                                "STATUS_STORAGE" : "IN-MEMORY"})
patch_env_mock.start()

# Patch the update callback to intercept and inspect status
with patch("subscription-manager.StatusCheck.update_callback") as function_mock:
    function_mock.side_effect = mock_callback
    result = await main(payload)
    self.assertIsInstance(result,SubscriptionResponse)
    self.assertEqual(result.properties.subscriptionId,"1111111-2222-3333-4444-ebc1b75b9d74")
    self.assertEqual(result.properties.provisioningState,"NotFound")
patch_env_mock.stop()
```

---
## Unit testing internal Callback methods

The subscription manager uses a custom callback that gets called from another method invoked
inside of an activity function. The following code demonstrates how to patch these callbacks:

### Assign a side-effect method that can intercept the call

```python
# Patch the update callback to intercept and inspect status
    with patch("subscription-manager.StatusCheck.update_callback") as function_mock:
        function_mock.side_effect = mock_callback
```

### Call the actual callback within the side effect method

```python
def mock_callback(status: Status):
    updated_status = update_callback(status)
```

### Assert the response

```python
def mock_callback(status: Status):
    updated_status = update_callback(status)

    # NotFound is returned by LocalSubscription emulation and we expect the same to be set here
    assert updated_status.creation_status == "NotFound"
```
---

## Running Locally

This example can be run locally the sample call, [test_orchestration.http](./test_orchestration.http) using the [REST Client for VS Code](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)

---
## Running all unit tests

The script [run_unit_tests.sh](./run_unit_tests.sh) can be used to invoke all the tests with the right module paths wired in.
- Create a python virtual environment `python3 -m venv env`
- Activate it `source env/bin/activate`
- Run unit tests `sh run_unit_tests.sh`

---