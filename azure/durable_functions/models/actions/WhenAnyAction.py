from azure.durable_functions.models.actions.CompoundAction import CompoundAction
from typing import Dict, Union

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib
from typing import List
from ..Task import Task

class WhenAnyAction(CompoundAction):
    """Defines the structure of the WhenAll Action object.

    Provides the information needed by the durable extension to be able to invoke WhenAll tasks.
    """
    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.WHEN_ANY