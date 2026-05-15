"""Centralized JSON serialization for Durable Functions payloads.

This module wraps the legacy `json.dumps(value, default=_serialize_custom_object)`
/ `json.loads(s, object_hook=_deserialize_custom_object)` pipeline from
`azure.functions._durable_functions` behind `df_dumps` and `df_loads`.

The wire format is **unchanged** -- builtins serialize to plain JSON and custom
objects use the `{"__class__": ..., "__module__": ..., "__data__": ...}`
convention that the Durable extension and downstream consumers already expect.

`df_loads` adds an optional `expected_type` parameter that controls
type validation.  Behavior depends on the typing mode:

* **Loose mode** (default) -- the payload is inspected before
  deserialization and a warning is logged on type mismatch, then the
  legacy ``object_hook`` pipeline runs as usual.
* **Strict mode** -- ``import_module`` is never called on either side.
  On encode, ``to_json`` is called on the top-level object only and
  the result must be plain-JSON-serializable (nested custom objects
  are **not** auto-encoded -- ``to_json`` must handle them).  On
  decode, ``expected_type.from_json`` is invoked directly with plain
  JSON data.  A ``TypeError`` is raised on type mismatch or if
  ``expected_type`` is not provided for a custom-object payload.
  Opt in by setting ``AZURE_FUNCTIONS_DURABLE_STRICT_TYPING`` to a
  truthy value (``1``, ``true``, ``yes``)."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from azure.functions._durable_functions import (
    _deserialize_custom_object,
    _serialize_custom_object,
)

logger = logging.getLogger(__name__)

_STRICT_ENV_VAR = "AZURE_FUNCTIONS_DURABLE_STRICT_TYPING"
_TRUTHY = frozenset({"1", "true", "yes"})


def _is_strict_mode() -> bool:
    return os.environ.get(_STRICT_ENV_VAR, "").strip().lower() in _TRUTHY


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def df_dumps(value: Any) -> str:
    """Serialize *value* to a JSON string.

    In **loose mode** (default), custom objects are encoded recursively
    via the legacy ``default=_serialize_custom_object`` handler — any
    nested custom object is automatically wrapped in the
    ``{"__class__", "__module__", "__data__"}`` envelope.

    In **strict mode**, the top-level custom object (if it has
    ``to_json``) is wrapped in the legacy envelope, but the
    ``__data__`` payload is serialized as **plain JSON** — no
    ``default=`` hook fires.  This means ``to_json()`` must return a
    value that is natively JSON-serializable (dicts, lists, strings,
    numbers, bools, None).  A ``TypeError`` is raised at encode time
    if any nested value is not serializable.
    """
    if _is_strict_mode():
        if hasattr(value, "to_json"):
            envelope = _serialize_custom_object(value)
            return json.dumps(envelope)
        # Primitive / plain-JSON value — serialize without default=
        # so stray custom objects are caught immediately.
        return json.dumps(value)
    return json.dumps(value, default=_serialize_custom_object)


def df_loads(s: str, expected_type: Optional[type] = None) -> Any:
    """Deserialize a JSON string, optionally validating the result type.

    Parameters
    ----------
    s : str
        The JSON-encoded payload.
    expected_type : type, optional
        When provided the raw JSON is parsed first (without triggering
        ``import_module`` via the legacy ``object_hook``).  If the
        payload is a legacy custom-object dict its embedded class info
        is validated against *expected_type* **before** any module is
        imported.  A matching *expected_type* is used to call
        ``from_json`` directly, avoiding ``import_module`` entirely.
        In loose mode a warning is emitted on mismatch; in strict mode
        a ``TypeError`` is raised.
    """
    if expected_type is not None:
        return _loads_with_expected_type(s, expected_type)

    if _is_strict_mode():
        return _loads_strict_no_type(s)

    return json.loads(s, object_hook=_deserialize_custom_object)


def _loads_strict_no_type(s: str) -> Any:
    """Strict-mode fallback when no *expected_type* is available.

    Parses without ``object_hook`` so ``import_module`` is never called.
    If the top-level value is a legacy custom-object dict, raises
    ``TypeError`` — the caller must supply an ``expected_type`` to
    deserialize custom objects in strict mode.
    """
    raw = json.loads(s)
    if _is_legacy_custom_dict(raw):
        raise TypeError(
            "df_loads: strict mode requires expected_type to "
            "deserialize custom-object payloads, but none was provided. "
            f"Payload declares {raw['__module__']}.{raw['__class__']}."
        )
    return raw


def _get_serialize_default():
    """Return the `default` callback for `json.dumps`.

    Use this in places that build their own `json.dumps` call (e.g.
    `OrchestratorState.to_json_string`) rather than going through
    `df_dumps`.

    In strict mode returns ``None`` — `OrchestratorState` fields are
    already serialized via `df_dumps` so there should be no remaining
    custom objects to encode.  A stray custom object will raise
    ``TypeError`` from ``json.dumps``, surfacing the problem early.
    """
    if _is_strict_mode():
        return None
    return _serialize_custom_object


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LEGACY_KEYS = frozenset({"__class__", "__module__", "__data__"})


def _is_legacy_custom_dict(d: Any) -> bool:
    """Return True if *d* is a dict with legacy custom-object markers."""
    return isinstance(d, dict) and _LEGACY_KEYS.issubset(d)


def _loads_with_expected_type(s: str, expected_type: type) -> Any:
    """Parse *s* and validate against *expected_type*.

    The raw JSON is parsed **without** the legacy ``object_hook`` so we
    can inspect the payload before ``import_module`` fires.

    * **Strict mode** -- for custom-object payloads, calls
      ``expected_type.from_json`` directly (no ``import_module``).  For
      primitives, validates then returns the plain value.  Raises
      ``TypeError`` on mismatch.
    * **Loose mode** -- logs a warning on mismatch, then falls through
      to the normal ``json.loads(s, object_hook=...)`` legacy path.
    """
    raw = json.loads(s)
    strict = _is_strict_mode()

    if _is_legacy_custom_dict(raw):
        class_name = raw["__class__"]
        module_name = raw["__module__"]
        type_matches = (class_name == expected_type.__name__
                        and module_name == expected_type.__module__)

        if not type_matches:
            msg = (
                f"df_loads: payload declares class "
                f"{module_name}.{class_name} but expected "
                f"{expected_type.__module__}.{expected_type.__name__}"
            )
            if strict:
                raise TypeError(msg)
            logger.warning(msg)

        if strict:
            # Bypass import_module entirely — call from_json directly.
            if not _has_json_protocol(expected_type):
                raise TypeError(
                    f"df_loads: expected_type "
                    f"{expected_type.__module__}.{expected_type.__name__} "
                    f"does not expose from_json"
                )
            return expected_type.from_json(raw["__data__"])

        # Loose mode — legacy deserialization.
        return json.loads(s, object_hook=_deserialize_custom_object)

    # Primitive / plain-JSON payload — validate the Python type.
    if not _is_compatible(raw, expected_type):
        msg = (
            f"df_loads: deserialized value ({type(raw).__name__}) is not "
            f"compatible with expected type {expected_type}"
        )
        if strict:
            raise TypeError(msg)
        logger.warning(msg)

    if strict:
        return raw
    # Loose mode — use legacy deserializer so nested custom objects
    # (inside dicts/lists) are still reconstructed via object_hook.
    return json.loads(s, object_hook=_deserialize_custom_object)

def _has_json_protocol(cls: type) -> bool:
    """Return True iff *cls* exposes callable `to_json` and `from_json`."""
    return callable(getattr(cls, "to_json", None)) and callable(
        getattr(cls, "from_json", None)
    )


def _is_compatible(value: Any, expected_type: type) -> bool:
    """Best-effort `isinstance` check that tolerates generic type hints."""
    try:
        return isinstance(value, expected_type)
    except TypeError:
        # typing constructs like `List[int]` aren't valid for isinstance.
        return True
