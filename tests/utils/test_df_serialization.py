"""Tests for the df_serialization shim.

``df_serialization`` is a thin shim over the Azure Functions SDK
serializers in ``azure.functions._durable_functions``:

* When the installed ``azure-functions`` exposes ``df_dumps`` /
  ``df_loads``, this module re-exports them directly.
* Otherwise it falls back to the legacy plain pipeline
  (``json.dumps(value, default=_serialize_custom_object)`` /
  ``json.loads(s, object_hook=_deserialize_custom_object)``).

The richer type-validation / strict-typing behavior lives in (and is
tested by) the SDK; these tests only assert the contract this shim is
responsible for: round-tripping payloads and preserving the wire format.
"""

import json

import azure.functions._durable_functions as _sdk
from azure.durable_functions.models.utils.df_serialization import (
    df_dumps,
    df_loads,
    _get_serialize_default,
)


# ---------------------------------------------------------------------------
# Helper classes
# ---------------------------------------------------------------------------

class PlainPerson:
    """Simple class: to_json returns a dict, from_json accepts a dict."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @staticmethod
    def to_json(obj):
        return {"name": obj.name, "age": obj.age}

    @staticmethod
    def from_json(data):
        return PlainPerson(data["name"], data["age"])

    def __eq__(self, other):
        return (isinstance(other, PlainPerson)
                and self.name == other.name and self.age == other.age)


class Hat:
    """Leaf object for nesting tests."""

    def __init__(self, color: str):
        self.color = color

    @staticmethod
    def to_json(obj):
        return {"color": obj.color}

    @staticmethod
    def from_json(data):
        return Hat(data["color"])

    def __eq__(self, other):
        return isinstance(other, Hat) and self.color == other.color


class NestedOrder:
    """Nested object relying on bottom-up object_hook reconstruction."""

    def __init__(self, item: str, hat: Hat):
        self.item = item
        self.hat = hat

    @staticmethod
    def to_json(obj):
        return {"item": obj.item, "hat": obj.hat}

    @staticmethod
    def from_json(data):
        return NestedOrder(data["item"], data["hat"])

    def __eq__(self, other):
        return (isinstance(other, NestedOrder)
                and self.item == other.item and self.hat == other.hat)


# ===========================================================================
# Primitive round-trips
# ===========================================================================

import pytest


@pytest.mark.parametrize("value", [
    None,
    True,
    False,
    0,
    -1,
    42,
    3.14,
    "",
    "hello",
    [],
    [1, 2, 3],
    [True, None, "mixed"],
    {},
    {"a": 1, "b": [1, 2]},
    {"nested": {"deep": {"value": 7}}},
])
def test_primitive_round_trip(value):
    assert df_loads(df_dumps(value)) == value


# ===========================================================================
# Custom object round-trips (legacy object_hook reconstruction)
# ===========================================================================

def test_simple_object_round_trip():
    obj = PlainPerson("andy", 99)
    assert df_loads(df_dumps(obj)) == obj


def test_nested_object_round_trip():
    obj = NestedOrder("widget", Hat("red"))
    decoded = df_loads(df_dumps(obj))
    assert decoded == obj
    assert isinstance(decoded.hat, Hat)


def test_dict_with_object_property_round_trip():
    payload = {"person": PlainPerson("a", 1), "count": 7}
    decoded = df_loads(df_dumps(payload))
    assert decoded["count"] == 7
    assert isinstance(decoded["person"], PlainPerson)
    assert decoded["person"].name == "a"


def test_list_of_objects_round_trip():
    payload = [PlainPerson("a", 1), PlainPerson("b", 2)]
    decoded = df_loads(df_dumps(payload))
    assert len(decoded) == 2
    assert all(isinstance(p, PlainPerson) for p in decoded)


def test_expected_type_is_accepted():
    """expected_type is part of the call signature; happy-path decoding
    still reconstructs the object regardless of which impl is active."""
    obj = PlainPerson("andy", 99)
    decoded = df_loads(df_dumps(obj), expected_type=PlainPerson)
    assert decoded == obj


# ===========================================================================
# Wire format verification
# ===========================================================================

def test_primitive_wire_format_is_plain_json():
    assert df_dumps({"a": 1, "b": [1, 2]}) == json.dumps({"a": 1, "b": [1, 2]})


def test_custom_object_wire_format_uses_legacy_envelope():
    raw = json.loads(df_dumps(PlainPerson("andy", 99)))
    assert raw["__class__"] == "PlainPerson"
    assert raw["__module__"] == PlainPerson.__module__
    assert raw["__data__"] == {"name": "andy", "age": 99}


# ===========================================================================
# _get_serialize_default
# ===========================================================================

def test_get_serialize_default_is_usable_with_json_dumps():
    default = _get_serialize_default()
    encoded = json.dumps(PlainPerson("andy", 99), default=default)
    raw = json.loads(encoded)
    assert raw["__class__"] == "PlainPerson"


# ===========================================================================
# Shim wiring
# ===========================================================================

def test_shim_prefers_sdk_serializers_when_available():
    """If the installed SDK exposes df_dumps/df_loads, the shim must
    re-export the SDK objects rather than a local fallback."""
    if hasattr(_sdk, "df_dumps"):
        assert df_dumps is _sdk.df_dumps
        assert df_loads is _sdk.df_loads
    else:
        # Fallback path: local functions defined in the shim module.
        assert df_dumps.__module__.endswith("df_serialization")
        assert df_loads.__module__.endswith("df_serialization")


def test_fallback_path_does_not_warn_at_import():
    """Importing the shim must never emit a UserWarning, even on the
    fallback path: the upgrade hint is deferred to first use and logged at
    debug level rather than raised as a warning at import time."""
    import importlib
    import warnings

    from azure.durable_functions.models.utils import df_serialization

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df_serialization)

    upgrade_warnings = [
        w for w in caught
        if issubclass(w.category, UserWarning)
        and "df_dumps" in str(w.message)
    ]
    assert upgrade_warnings == []


def test_fallback_path_logs_once_on_first_use(monkeypatch):
    """On the fallback path, the first serialize/deserialize call logs the
    upgrade hint once at debug level; the SDK path logs nothing."""
    import importlib

    from azure.durable_functions.models.utils import df_serialization
    importlib.reload(df_serialization)

    records = []
    monkeypatch.setattr(
        df_serialization.logger, "debug",
        lambda msg, *a, **k: records.append(msg),
    )

    df_serialization.df_dumps({"a": 1})
    df_serialization.df_loads(df_serialization.df_dumps({"a": 1}))

    fallback_logs = [m for m in records if "df_dumps" in str(m)]
    if hasattr(_sdk, "df_dumps"):
        assert fallback_logs == []
    else:
        # Logged exactly once despite multiple fallback calls.
        assert len(fallback_logs) == 1

