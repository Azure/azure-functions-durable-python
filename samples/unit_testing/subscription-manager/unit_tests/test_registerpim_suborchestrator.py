import azure.durable_functions as df
import azure.functions as func
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock, patch
from ..Subscription.subscription import SubscriptionProperties, SubscriptionResponse
from ..RegisterPIMSubOrchestrator import orchestrator_fn

"""
Mocked Register PIM Activity function
"""
def call_activity_mock_register_pim(activityName: str, payload):
    assert activityName == "RegisterPIM"
    assert payload["productName"] != None
    assert payload["customerName"] != None
    assert payload["envName"] != None

"""
Test class for RegisterPIMSubOrchestrator Durable orchestrator that calls the activity function
Mocks the DurableOrchestrationContext and checks the sequence of sub-orchestration calls
"""
class TestRegisterPIMSubOrchestrator(TestCase):

  def test_register_pim_sub_orchestrator(self):
    global mock
    with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
        mock.get_input = MagicMock(return_value={
            'productName' : 'test_product',
            'customerName' : 'microsoft',
            'envName' : 'production',
            'displayName' : 'test'
        })

        # mock call activity that calls to register PIM status
        mock.call_activity.side_effect = call_activity_mock_register_pim
        succeeded_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Succeeded"))

        gen_orchestrator = orchestrator_fn(mock)
        try:
            # Make a call to Register PIM activity
            next(gen_orchestrator)

            # Send back subscription response to orchestrator
            gen_orchestrator.send(succeeded_response)
        
        except StopIteration as e:
            result = e.value
            self.assertIsInstance(result,SubscriptionResponse)
            self.assertEqual('51ba2a78-bec0-4f31-83e7-58c64693a6dd',result.id)

if __name__ == "__main__":
    main()