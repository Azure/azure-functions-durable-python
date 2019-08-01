from ..models import DurableOrchestrationContext


class IFunctionContext:
    def __init__(self, df=None):
        self.df: DurableOrchestrationContext = df
