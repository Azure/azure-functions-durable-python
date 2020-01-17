"""Interface for the Orchestration object exposed to the generator function."""
from ..models import DurableOrchestrationContext


class IFunctionContext:
    """Orchestration object exposed to the generator function."""

    def __init__(self, df=None):
        """Create a new orchestration context."""
        self.df: DurableOrchestrationContext = df
