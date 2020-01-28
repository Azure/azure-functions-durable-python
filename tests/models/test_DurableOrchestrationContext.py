import pytest
from dateutil.parser import parse as dt_parse

from azure.durable_functions.models.DurableOrchestrationContext \
    import DurableOrchestrationContext


@pytest.fixture
def starting_context():
    context = DurableOrchestrationContext.from_json(
        '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,'
        '"Timestamp":"2019-12-08T23:18:41.3240927Z"}, '
        '{"OrchestrationInstance":{'
        '"InstanceId":"48d0f95957504c2fa579e810a390b938", '
        '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,'
        '"ParentInstance":null, '
        '"Name":"DurableOrchestratorTrigger","Version":"","Input":"null",'
        '"Tags":null,"EventId":-1,"IsPlayed":false, '
        '"Timestamp":"2019-12-08T23:18:39.756132Z"}],"input":null,'
        '"instanceId":"48d0f95957504c2fa579e810a390b938", '
        '"isReplaying":false,"parentInstanceId":null} ')
    return context


def test_extracts_is_replaying(starting_context):
    assert not starting_context.is_replaying


def test_extracts_instance_id(starting_context):
    assert "48d0f95957504c2fa579e810a390b938" == starting_context.instance_id


def test_sets_current_utc_datetime(starting_context):
    assert \
        dt_parse("2019-12-08T23:18:41.3240927Z") == \
        starting_context.current_utc_datetime


def test_extracts_histories(starting_context):
    assert 2 == len(starting_context.histories)
