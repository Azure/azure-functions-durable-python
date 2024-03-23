import os
import azure.durable_functions as df
from unittest import main,mock
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from ..RegisterPIM import main
from ..RegisterPIM import update_callback

"""
Mock callback that intercepts the update callback to inspect the status
"""
def mock_callback(status):
    update_callback(status)

    # check if pim_enabled was set to True by the activity function
    assert status.pim_enabled == True
    return status

"""
Test class for CreateEASubscription activity function using Local in memory status storage
and canned REST API response from LocalSubscription
"""
class TestRegisterPIMActivity(IsolatedAsyncioTestCase):
  
  async def test_status_check_activity_valid_inputs(self):
    payload = {
                'productName' : 'test_product',
                'customerName' : 'microsoft',
                'envName' : 'production',
                'displayName' : 'test_ea_subscription',
                'subscriptionName' : 'python_subscription'
            }

    # Patch the environment variable here for it to take effect inside the durable function activity call
    patch_env_mock = mock.patch.dict(os.environ, {"RUNTIME_ENVIRONMENT": "LOCAL",
                                                "STATUS_STORAGE" : "IN-MEMORY"})
    # start mock context
    patch_env_mock.start()

    # patch the update callback to intercept the status object and make a call to the actual
    # update object to get back a response that can be asserted
    with patch("subscription-manager.RegisterPIM.update_callback") as function_mock:
        function_mock.side_effect = mock_callback
        result = await main(payload)

    # stop mock context
    patch_env_mock.stop()
       
if __name__ == "__main__":
    main()