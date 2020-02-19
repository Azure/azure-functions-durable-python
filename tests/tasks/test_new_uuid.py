from uuid import uuid1
import datetime
from typing import List, Any, Dict
from datetime import datetime

from azure.durable_functions.tasks.new_uuid import URL_NAMESPACE, \
    _create_deterministic_uuid
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.constants import DATETIME_STRING_FORMAT


def test_create_deterministic_uuid():
    namespace = URL_NAMESPACE
    instance_id = uuid1()
    current_utc_datetime = datetime.now().strftime(DATETIME_STRING_FORMAT);

    name1 = f"{instance_id}_{current_utc_datetime}_0"
    name2 = f"{instance_id}_{current_utc_datetime}_12"

    result1a = _create_deterministic_uuid(namespace, name1)
    result1b = _create_deterministic_uuid(namespace, name1)

    result2a = _create_deterministic_uuid(namespace, name2)
    result2b = _create_deterministic_uuid(namespace, name2)

    assert result1a == result1b
    assert result2a == result2b

    assert result1a != result2a
    assert result1b != result2b


def history_list() -> List[Dict[Any, Any]]:
    history = [{'EventType': 12, 'EventId': -1, 'IsPlayed': False,
                'Timestamp': '2019-12-08T23:18:41.3240927Z'}, {
                   'OrchestrationInstance': {'InstanceId': '48d0f95957504c2fa579e810a390b938',
                                             'ExecutionId': 'fd183ee02e4b4fd18c95b773cfb5452b'},
                   'EventType': 0, 'ParentInstance': None, 'Name': 'DurableOrchestratorTrigger',
                   'Version': '', 'Input': 'null', 'Tags': None, 'EventId': -1, 'IsPlayed': False,
                   'Timestamp': '2019-12-08T23:18:39.756132Z'}]
    return history


def test_new_uuid():
    instance_id = str(uuid1())
    history = history_list()
    context1 = DurableOrchestrationContext(history, instance_id, False, None)

    result1a = context1.new_uuid()
    result1b = context1.new_uuid()

    context2 = DurableOrchestrationContext(history, instance_id, False, None)

    result2a = context2.new_uuid()
    result2b = context2.new_uuid()

    assert result1a == result2a
    assert result1b == result2b

    assert result1a != result1b
    assert result2a != result2b
