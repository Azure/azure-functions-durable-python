import pytest
import json
from typing import List

from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.tasks.call_activity import call_activity_task
from azure.durable_functions.models.actions.ActionType import ActionType
from azure.durable_functions.models.actions.CallActivityAction import \
    CallActivityAction


# noinspection PyTypeChecker
def test_generates_schedule_task():
    histories_string = '[{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
                       '{"OrchestrationInstance":{' \
                       '"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
                       '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},' \
                       '"EventType":0,"ParentInstance":null,' \
                       '"Name":"DurableFunctionsOrchestratorJS",' \
                       '"Version":"","Input":"null","Tags":null,' \
                       '"EventId":-1,' \
                       '"IsPlayed":false,"Timestamp":"2019-12-08T23:18:39' \
                       '.756132Z"}] '

    histories: List[HistoryEvent] = json.loads(histories_string)
    result = call_activity_task(state=histories, name="Hello", input_="Tokyo")
    assert not result._is_completed
    action: CallActivityAction = result._action
    assert ActionType.CallActivity == action.action_type
    assert "Hello" == action.function_name
    assert "Tokyo" == action.input_


@pytest.mark.skip(
    reason="Need to either change to use the context builder or remove. Is "
           "redundant with other tests")
def test_generates_completed_task():
    histories_string = '[{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
                       '{"OrchestrationInstance":{' \
                       '"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
                       '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},' \
                       '"EventType":0,"ParentInstance":null,' \
                       '"Name":"DurableFunctionsOrchestratorJS",' \
                       '"Version":"","Input":"null","Tags":null,' \
                       '"EventId":-1,' \
                       '"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39' \
                       '.756132Z"},{"EventType":4,"Name":"Hello",' \
                       '"Version":"","Input":null,"EventId":0,' \
                       '"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5313393Z"},' \
                       '{"EventType":13,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5320985Z"},' \
                       '{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:52.4899106Z"},' \
                       '{"EventType":5,"TaskScheduledId":0,' \
                       '"Result":"\"Hello Tokyo!\"","EventId":-1,' \
                       '"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.7873033Z"}]'

    histories: List[HistoryEvent] = json.loads(histories_string)
    result = call_activity_task(state=histories, name="Hello", input_="Tokyo")
    assert result._is_completed


# noinspection PyTypeChecker
@pytest.mark.skip(
    reason="Need to either change to use the context builder or remove. Is "
           "redundant with other tests")
def test_generates_schedule_task_for_second_activity():
    histories_string = '[{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
                       '{"OrchestrationInstance":{' \
                       '"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
                       '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},' \
                       '"EventType":0,"ParentInstance":null,' \
                       '"Name":"DurableFunctionsOrchestratorJS",' \
                       '"Version":"","Input":"null","Tags":null,' \
                       '"EventId":-1,' \
                       '"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39' \
                       '.756132Z"},{"EventType":4,"Name":"Hello",' \
                       '"Version":"","Input":null,"EventId":0,' \
                       '"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5313393Z"},' \
                       '{"EventType":13,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5320985Z"},' \
                       '{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:52.4899106Z"},' \
                       '{"EventType":5,"TaskScheduledId":0,' \
                       '"Result":"\"Hello Tokyo!\"","EventId":-1,' \
                       '"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.7873033Z"}]'

    histories: List[HistoryEvent] = json.loads(histories_string)
    call_activity_task(state=histories, name="Hello", input_="Tokyo")
    result = call_activity_task(state=histories, name="Hello",
                                input_="Seattle")
    assert not result._is_completed
    action: CallActivityAction = result._action
    assert ActionType.CallActivity == action.action_type
    assert "Hello" == action.function_name
    assert "Seattle" == action.input_


# noinspection PyTypeChecker
@pytest.mark.skip(
    reason="Need to either change to use the context builder or remove. Is "
           "redundant with other tests")
def test_generates_completed_task_for_second_activity():
    histories_string = '[{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
                       '{"OrchestrationInstance":{' \
                       '"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
                       '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},' \
                       '"EventType":0,"ParentInstance":null,' \
                       '"Name":"DurableFunctionsOrchestratorJS",' \
                       '"Version":"","Input":"null","Tags":null,' \
                       '"EventId":-1,' \
                       '"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39' \
                       '.756132Z"},{"EventType":4,"Name":"Hello",' \
                       '"Version":"","Input":null,"EventId":0,' \
                       '"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5313393Z"},' \
                       '{"EventType":13,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:51.5320985Z"},' \
                       '{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:29:52.4899106Z"},' \
                       '{"EventType":5,"TaskScheduledId":0,' \
                       '"Result":"\"Hello Tokyo!\"","EventId":-1,' \
                       '"IsPlayed":true,' \
                       '"Timestamp":"2019-12-08T23:29:51.7873033Z"},' \
                       '{"EventType":4,"Name":"Hello","Version":"",' \
                       '"Input":null,"EventId":1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:34:12.2632487Z"},' \
                       '{"EventType":13,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:34:12.263286Z"},' \
                       '{"EventType":12,"EventId":-1,"IsPlayed":false,' \
                       '"Timestamp":"2019-12-08T23:34:12.8710525Z"},' \
                       '{"EventType":5,"TaskScheduledId":1,' \
                       '"Result":"\"Hello ' \
                       'Seattle!\"","EventId":-1,' \
                       '"IsPlayed":false,"Timestamp":"2019-12-08T23:34:12' \
                       '.561288Z"}] '

    histories: List[HistoryEvent] = json.loads(histories_string)
    call_activity_task(state=histories, name="Hello", input_="Tokyo")
    result = call_activity_task(state=histories, name="Hello",
                                input_="Seattle")
    assert result._is_completed
    action: CallActivityAction = result._action
    assert ActionType.CallActivity == action.action_type
    assert "Hello" == action.function_name
    assert "Seattle" == action.input_
