class FunctionContext:
    def __init__(self, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)
