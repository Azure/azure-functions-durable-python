from ..models import DurableOrchestrationContext


class IFunctionContext:
    """Interface for the Orchestration object exposed to the generator function."""

    def __init__(self, df=None):
        self.df: DurableOrchestrationContext = df
