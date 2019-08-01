from .ActionType import ActionType


class CallActivityAction:
    def __init__(self, functionName: str, input=None):
        self.actionType: ActionType = ActionType.CallActivity
        self.functionName: str = functionName
        self.input = input

        if not self.functionName:
            raise ValueError("functionName cannot be empty")
