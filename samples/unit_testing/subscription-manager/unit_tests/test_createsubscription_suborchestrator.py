import datetime
import azure.durable_functions as df
import azure.functions as func
from datetime import timedelta
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock, patch
from ..Subscription.subscription import SubscriptionProperties, SubscriptionResponse
from ..CreateSubscriptionSubOrchestrator import orchestrator_fn

#######################################################################
#### Call Activity Mocks ##############################################
#######################################################################
def call_activity_create_subscription(activityName: str, payload):
    assert activityName == "CreateSubscription"
    mock.call_activity.side_effect = call_activity_mock_status_check_succeeded

def call_activity_mock_status_check_accepted(activityName: str, payload):
    assert activityName == "StatusCheck"

def call_activity_mock_status_check_succeeded(activityName: str, payload):
    assert activityName == "StatusCheck"

def call_activity_mock_status_check_notfound(activityName:str, payload):
    mock.call_activity.side_effect = call_activity_create_subscription
    assert activityName == "StatusCheck"

def call_activity_mock_status_check_error(activityName:str, payload):
    assert activityName == "StatusCheck"

#######################################################################
#### Create Timer Mocks ##############################################
#######################################################################

def create_timer_mock(next_checkpoint):
    # check if next_checkpoint got scheduled 1 min more than previous checkpoint
    assert int(next_checkpoint.strftime("%M")) == int(mock.current_utc_datetime.strftime("%M")) + 1

    # change the call_activity side effect to succeeded call
    mock.call_activity.side_effect = call_activity_mock_status_check_succeeded

def create_timer_error_mock(next_checkpoint):
    # check if next_checkpoint got scheduled 1 min more than previous checkpoint
    assert int(next_checkpoint.strftime("%M")) == int(mock.current_utc_datetime.strftime("%M")) + 1

    # change the call_activity side effect to error call
    mock.call_activity.side_effect = call_activity_mock_status_check_error

"""
Test class for CreateSubscriptionSubOrchestrator Durable orchestrator that uses
- Monitor pattern
- Call Activity of StatusCheck and CreateSubscription
"""
class TestEASubscriptionSubOrchestrator(TestCase):

    #######################################################################
    #### Accepted -> Create Monitor -> Succeeded ##########################
    #######################################################################
    def test_ea_subscription_sub_orchestrator_accepted_timer_succeeded(self):
        global mock
        with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
            mock.get_input = MagicMock(return_value={
                'productName' : 'test_product',
                'customerName' : 'microsoft',
                'envName' : 'production',
                'displayName' : 'test'
            })

            # mock call activity that returns subscription response as Accepted
            mock.call_activity.side_effect = call_activity_mock_status_check_accepted
            mock.create_timer.side_effect = create_timer_mock
            mock.current_utc_datetime = datetime.datetime.utcnow()

            accepted_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Accepted"))
            succeeded_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Succeeded"))

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

    #######################################################################
    #### Not Found -> Create Sub -> Create Monitor -> Succeeded ###########
    ####################################################################### 
    def test_ea_subscription_sub_orchestrator_notfound_createsub_timer_succeeded(self):
        global mock
        with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:
            mock.get_input = MagicMock(return_value={
                'productName' : 'test_product',
                'customerName' : 'microsoft',
                'envName' : 'production',
                'displayName' : 'test'
            })

            # mock call activity that returns subscription response as Accepted
            mock.call_activity.side_effect = call_activity_mock_status_check_notfound
            mock.create_timer.side_effect = create_timer_mock
            mock.current_utc_datetime = datetime.datetime.utcnow()

            notfound_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","NotFound"))
            succeeded_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Succeeded"))

            gen_orchestrator = orchestrator_fn(mock)
            try:
                # Make a call to Status check to see and if response is accepted (subscription is in process of being created)
                next(gen_orchestrator)

                # Send back response to orchestrator
                gen_orchestrator.send(notfound_response)

                # Timer is set and now the call succeeds
                next(gen_orchestrator)

                # Send back success response to orchestrator
                gen_orchestrator.send(succeeded_response)

            except StopIteration as e:
                result = e.value
                self.assertEqual('51ba2a78-bec0-4f31-83e7-58c64693a6dd',result)
    

    # The error case is written as an example here, it truly cannot be tested for the code in the orchestrator as
    # the expiry time is not mockable.
    def test_ea_subscription_sub_orchestrator_error_case(self):
        global mock
        with patch('azure.durable_functions.DurableOrchestrationContext',spec=df.DurableOrchestrationContext) as mock:   
            mock.get_input = MagicMock(return_value={
                'productName' : 'test_product',
                'customerName' : 'microsoft',
                'envName' : 'production',
                'displayName' : 'test'
            })

            # mock call activity that returns subscription response as Accepted
            mock.call_activity.side_effect = call_activity_mock_status_check_accepted
            mock.create_timer.side_effect = create_timer_error_mock
            mock.current_utc_datetime = datetime.datetime.utcnow()

            accepted_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Accepted"))
            error_response = SubscriptionResponse("51ba2a78-bec0-4f31-83e7-58c64693a6dd","test","EA",SubscriptionProperties("51ba2a78-bec0-4f31-83e7-58c64693a6dd","Error"))

            gen_orchestrator = orchestrator_fn(mock)
            try:
                # Make a call to Status check to see and if response is accepted (subscription is in process of being created)
                next(gen_orchestrator)

                # Send back response to orchestrator
                gen_orchestrator.send(accepted_response)

                # Timer is set and now the call succeeds
                next(gen_orchestrator)

                # Send back success response to orchestrator
                gen_orchestrator.send(error_response)

                self.assertRaises(Exception,orchestrator_fn)

            except StopIteration as e:
                pass


if __name__ == "__main__":
    main()