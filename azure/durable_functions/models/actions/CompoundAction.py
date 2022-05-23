from typing import Dict, Union

from .Action import Action
from ..utils.json_utils import add_attrib
from typing import List
from abc import abstractmethod


class CompoundAction(Action):
    """Defines the structure of the WhenAll Action object.

    Provides the information needed by the durable extension to be able to invoke WhenAll tasks.
    """

    def __init__(self, compound_tasks: List[Action]):
        self.compound_tasks = compound_tasks

    @property
    @abstractmethod
    def action_type(self) -> int:
        """Get this object's action type as an integer."""
        ...

    def to_json(self) -> Dict[str, Union[str, int]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Union[str, int]]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        json_dict['compoundActions'] = list(map(lambda x: x.to_json(), self.compound_tasks))
        return json_dict
