import azure.durable_functions as df
from unittest import main
from unittest import TestCase
from unittest.mock import patch
from ..MgmtGroupSubOrchestrator import orchestrator_fn

def call_activity_mock_add_sub_to_mgmt_group(activityName: str):
    assert activityName == "AddSubscriptionToMgmtGroup"

"""
Test class for MgmtGroupSubOrchestrator Durable orchestrator that kicks off an activity function
Mocks the DurableOrchestrationContext and checks the sequence of sub-orchestration calls
"""
class TestMgmtGroupSubOrchestrator(TestCase):

  def test_mgmt_group_sub_orchestrator(self):
    global mock
    with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
       
        # mock call activity that calls to add subscription to management group
        mock.call_activity.side_effect = call_activity_mock_add_sub_to_mgmt_group

        generator_fn = orchestrator_fn(mock)

        # send mock response back to generator
        mock_response = "Added subscription to management group"

        try:
             next(generator_fn)

             # send back mock response so that we can verify in test
             generator_fn.send(mock_response)
             
        except StopIteration as e:
             result = e.value
             self.assertEqual(result,'Added subscription to management group')

if __name__ == "__main__":
    main()