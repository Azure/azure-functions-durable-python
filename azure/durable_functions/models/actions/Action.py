from typing import Dict, Any
from abc import ABC, abstractmethod


class Action(ABC):
    """Defines the base abstract class for Actions that need to be implemented."""

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass
