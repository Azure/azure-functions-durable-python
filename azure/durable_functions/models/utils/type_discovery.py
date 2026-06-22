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

import functools
import inspect
import logging
import typing
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


@functools.lru_cache(maxsize=None)
def _return_annotation(fn: Callable) -> Optional[type]:
    """Resolve *fn*'s return annotation to a concrete ``type``, or ``None``.

    ``typing.get_type_hints`` is tried first so that string annotations
    (``from __future__ import annotations`` / PEP 563) are resolved to the
    real object. Results are memoized per function because this runs on
    every ``call_activity`` / ``call_sub_orchestrator`` (including replay).

    Limitation: generic aliases such as ``list[Order]`` or
    ``Optional[Order]`` are not concrete ``type`` objects, so they resolve
    to ``None`` and the caller falls back to module-only resolution.
    """
    ann: Any = inspect.Signature.empty
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = None
    if hints is not None and "return" in hints:
        ann = hints["return"]
    else:
        # get_type_hints couldn't resolve (e.g. forward ref it can't see);
        # fall back to the raw signature annotation.
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
