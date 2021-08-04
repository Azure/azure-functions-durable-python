import azure.durable_functions as df
import os
from unittest import main,mock
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch,MagicMock
from ..Subscription.subscription import SubscriptionResponse
from ..StatusCheck import main
from ..StatusCheck import update_callback
from ..Status.status import Status

"""
Mock callback that intercepts and inspects status
"""
def mock_callback(status: Status):
    updated_status = update_callback(status)

    # NotFound is returned by LocalSubscription emulation and we expect the same to be set here
    assert updated_status.creation_status == "NotFound"

"""
Test class for Status Check activity function that checks for valid inputs 
"""
class TestStatusCheckActivity(IsolatedAsyncioTestCase):
  
  async def test_status_check_activity_valid_inputs(self):
    payload = {
                'productName' : 'test_product',
                'customerName' : 'microsoft',
                'envName' : 'production',
                'displayName' : 'test',
                'subscriptionName' : 'python_subscription'
            }

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
       
if __name__ == "__main__":
    main()