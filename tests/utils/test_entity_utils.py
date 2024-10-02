import pytest
from azure.durable_functions.models.utils.entity_utils import EntityId

@pytest.mark.parametrize(
    ("name_e1", "key_1", "name_e2", "key_2", "expected"),
    [
        ("name1", "key1", "name1", "key1", True),
        ("name1", "key1", "name1", "key2", False),
        ("name1", "key1", "name2", "key1", False),
        ("name1", "key1", "name2", "key2", False),
    ],
)
def test_equal_entity_by_name_and_key(name_e1, key_1, name_e2, key_2, expected):

    entity1 = EntityId(name_e1, key_1)
    entity2 = EntityId(name_e2, key_2)

    assert (entity1 == entity2) == expected

def test_equality_with_non_entity_id():

    entity = EntityId("name", "key")

    assert (entity == "not an entity id") == False
