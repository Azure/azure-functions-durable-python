class ResponseMessage:
    def __init__(self, result: str):
        self.result = result
        # TODO: JS has an additional exceptionType field, but does not use it