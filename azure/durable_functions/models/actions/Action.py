from typing import Dict, Any
from abc import ABC, abstractmethod


class Action(ABC):
    """Defines the base abstract class for Actions that need to be implemented."""

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        pass
