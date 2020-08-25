"""Utility classes used by the Durable Function python library for dealing with entities.

_Internal Only_
"""

from .RequestMessage import RequestMessage
from .OperationResult import OperationResult
from .EntityState import EntityState
from .Signal import Signal
# TODO: this is very boilerplate-y, can we do better?

__all__ = [
    'RequestMessage',
    'OperationResult',
    'Signal',
    'EntityState'
]
