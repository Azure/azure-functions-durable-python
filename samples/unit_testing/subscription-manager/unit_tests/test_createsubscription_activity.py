import os
import azure.durable_functions as df
from unittest import main,mock
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from ..Subscription.subscription import SubscriptionResponse
from ..Status.status import Status
from ..CreateSubscription import main,update_callback

"""
Mock callback that intercepts the update_status call as a decorator
"""
def mock_callback(status:Status):
    updated_status = update_callback(status)
    assert updated_status.name == "python_subscription"
    assert updated_status.id == "/providers/Microsoft.Subscription/aliases/python_subscription"
    assert updated_status.creation_status == "Succeeded"
    assert updated_status.pim_enabled == "False"
    return updated_status

"""
Test class for CreateSubscription Activity Function that mocks
the update callback and tests the Subscription Response
"""
class TestCreateSubscription(IsolatedAsyncioTestCase):
  print(os.getcwd())
  async def test_status_check_activity_valid_inputs(self):
    payload = {
                'customerName' : 'microsoft',
                'displayName' : 'test_ea_subscription',
                'subscriptionName' : 'python_subscription'
            }
    patch_env_mock = mock.patch.dict(os.environ, {"RUNTIME_ENVIRONMENT": "LOCAL",
                                                  "STATUS_STORAGE" : "IN-MEMORY"})
    patch_env_mock.start()
    with patch("subscription-manager.CreateSubscription.update_callback") as function_mock:
        function_mock.side_effect = mock_callback
        result = await main(payload)
        self.assertIsInstance(result,SubscriptionResponse)
        self.assertEqual(result.properties.subscriptionId,"1111111-2222-3333-4444-ebc1b75b9d74")
        self.assertEqual(result.properties.provisioningState,"Succeeded")
        self.assertEqual(result.id,"/providers/Microsoft.Subscription/aliases/python_subscription")
        self.assertEqual(result.name,payload['subscriptionName'])
    patch_env_mock.stop()
       
if __name__ == "__main__":
    main()