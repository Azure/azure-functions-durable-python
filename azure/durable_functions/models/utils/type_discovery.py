"""Best-effort type-hint discovery for Durable Functions call sites.

These helpers feed the ``expected_type`` argument of
``df_serialization.df_loads`` so that custom-class instances can be
re-instantiated without consulting ``sys.modules`` / ``importlib``.

All public helpers swallow exceptions and return ``None`` on failure --
the caller treats ``None`` as "no type information available" and falls
back to module-only resolution (and, ultimately, the legacy decoder
with a warning).
"""

from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def _unwrap_function_builder(name_or_callable: Any) -> Optional[Callable]:
    """Return the underlying user function from a V2 ``FunctionBuilder``.

    Returns ``None`` for plain strings, plain callables, or anything we
    don't recognize.
    """
    # Avoid a hard dependency on the FunctionBuilder symbol (it lives in
    # the azure-functions package and may move).
    func = getattr(getattr(name_or_callable, "_function", None), "_func", None)
    if callable(func):
        return func
    return None


def _return_annotation(fn: Callable) -> Optional[type]:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return None
    ann = sig.return_annotation
    if ann is inspect.Signature.empty:
        return None
    return ann if isinstance(ann, type) else None


def activity_output_type(name_or_callable: Any) -> Optional[type]:
    """Discover the return-annotation type of a V2 activity function.

    Returns ``None`` if ``name_or_callable`` is a plain string (V1 model
    or hand-written name) or if the annotation isn't a concrete type.
    """
    fn = _unwrap_function_builder(name_or_callable)
    if fn is None:
        return None
    return _return_annotation(fn)


def sub_orchestrator_output_type(name_or_callable: Any) -> Optional[type]:
    """Discover the return-annotation type of a V2 sub-orchestrator function."""
    fn = _unwrap_function_builder(name_or_callable)
    if fn is None:
        return None
    return _return_annotation(fn)


def entity_operation_input_type(entity_user_fn: Optional[Callable],
                                operation_name: str) -> Optional[type]:
    """Best-effort discovery of an entity operation's input type.

    Entities in the V2 model are typically a single function that
    dispatches on ``context.operation_name``. There is no general way to
    statically associate an operation name with a parameter type; this
    helper currently returns ``None`` for all such functions and exists
    as the extension point for richer entity-dispatch patterns we may
    add in the future (e.g. class-based entities with one method per
    operation).
    """
    if entity_user_fn is None or not operation_name:
        return None
    # Future work: inspect class-based entity dispatch tables. For now,
    # signal "unknown" so the codec falls back to module-only resolution.
    return None
