import azure.durable_functions as df
import azure.functions as func
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock, patch
from ..Subscription.subscription import SubscriptionProperties, SubscriptionResponse
from ..SubscriptionLifecycleOrchestrator import orchestrator_fn

"""
Mocks fan in / fan out task_all method
"""
def task_all_mock(tasks:list):
    assert len(tasks) == 2
    return list

"""
Mocks Sub orchestrator calls and makes sure each sub orchestrator call returns the right response
"""
def sub_orc_mock(orchestrator_name:str, payload):
    if orchestrator_name == "CreateSubscriptionSubOrchestrator":
        return "51ba2a78-bec0-4f31-83e7-58c64693a6dd"
    elif orchestrator_name == "RegisterPIMSubOrchestrator":
        return SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd",payload['displayName'],"EA",
                    SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Accepted"))
    else:
        return "Added Subscription to Management Group"

"""
Test class for CreateSubscriptionOrchestrator Durable orchestrator that kicks off sub orchestrations
Mocks the DurableOrchestrationContext and checks the sequence of sub-orchestration calls
"""
class TestCreateEASubscriptionOrchestrator(TestCase):

    def test_create_ea_orchestrator(self):

        global mock
        with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
            mock.get_input = MagicMock(return_value={'displayName' : 'test'})
            mock.call_sub_orchestrator.side_effect = sub_orc_mock
            mock.task_all.side_effect = task_all_mock
        
            # To get generator results do a next. If orchestrator response is a list, then wrap the function call around a list
            result = list(orchestrator_fn(mock))
            self.assertEqual('51ba2a78-bec0-4f31-83e7-58c64693a6dd',result[0])

if __name__ == "__main__":
    main()