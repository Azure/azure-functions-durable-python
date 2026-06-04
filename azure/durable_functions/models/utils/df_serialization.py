"""Centralized JSON serialization for Durable Functions payloads.

This module is a thin shim over the Azure Functions SDK serialization
helpers in ``azure.functions._durable_functions``.

When the installed ``azure-functions`` package exposes ``df_dumps`` /
``df_loads`` (the centralized serializers with optional type validation
and strict-typing support), this module re-exports them directly so that
our serialization matches **exactly** what the SDK's
``ActivityTriggerConverter`` uses at the host boundary.

When those symbols are **not** available (older ``azure-functions``
releases), we fall back to the legacy plain pipeline --
``json.dumps(value, default=_serialize_custom_object)`` /
``json.loads(s, object_hook=_deserialize_custom_object)`` -- which is the
same behavior the SDK converter uses in those versions.

We deliberately do **not** substitute a richer local implementation on the
fallback path: if ``df_dumps`` / ``df_loads`` are not available from the
SDK, the SDK's ``ActivityTriggerConverter`` will not use them either, so
emulating the enhanced behavior locally would make our serialization
diverge from the converter that actually encodes and decodes activity
payloads. Using only the ``_serialize_custom_object`` /
``_deserialize_custom_object`` hooks -- which exist in every supported
``azure-functions`` release -- keeps both sides symmetric.

The wire format is **unchanged** -- builtins serialize to plain JSON and
custom objects use the ``{"__class__", "__module__", "__data__"}``
convention that the Durable extension and downstream consumers expect.
"""

from __future__ import annotations

import json
import warnings
from typing import Any, Optional

from azure.functions._durable_functions import (
    _deserialize_custom_object,
    _serialize_custom_object,
)

try:
    # Preferred: the SDK's centralized serializers (type-validation and
    # strict-typing aware). Available in azure-functions >= 2.2.0 (Python
    # >= 3.13) and >= 1.26.0 (Python 3.10-3.12).
    from azure.functions._durable_functions import (  # type: ignore
        df_dumps,
        df_loads,
    )
except ImportError:
    warnings.warn(
        "The installed 'azure-functions' package does not provide the "
        "centralized 'df_dumps' / 'df_loads' serializers. Durable Functions "
        "is falling back to the legacy serialization pipeline; the wire "
        "format is unchanged, but payload type validation (the 'expected_type' "
        "argument and strict typing mode) is unavailable. Upgrade to "
        "azure-functions>=2.2.0 on Python>=3.13, or azure-functions>=1.26.0 "
        "on Python 3.10-3.12, to enable type-validated serialization.",
        stacklevel=2,
    )

    def df_dumps(value: Any) -> str:
        """Serialize *value* to JSON via the legacy custom-object hook."""
        return json.dumps(value, default=_serialize_custom_object)

    def df_loads(s: str, expected_type: Optional[type] = None) -> Any:
        """Deserialize *s* via the legacy custom-object hook.

        ``expected_type`` is accepted for call-site compatibility but is
        ignored on this fallback path; type validation is only performed
        by the SDK's ``df_loads`` when it is available.
        """
        return json.loads(s, object_hook=_deserialize_custom_object)


try:
    from azure.functions._durable_functions import (  # type: ignore
        _get_serialize_default,
    )
except ImportError:
    def _get_serialize_default():
        """Return the ``default`` callback for a standalone ``json.dumps``.

        Used where code builds its own ``json.dumps`` call (e.g.
        ``OrchestratorState.to_json_string``) rather than going through
        ``df_dumps``.
        """
        return _serialize_custom_object


__all__ = ["df_dumps", "df_loads", "_get_serialize_default"]
