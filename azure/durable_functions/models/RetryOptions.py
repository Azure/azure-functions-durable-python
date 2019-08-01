class RetryOptions:
    def __init__(self, firstRetry: int, maxNumber: int):
        self.backoffCoefficient: int
        self.maxRetryIntervalInMilliseconds: int
        self.retryTimeoutInMilliseconds: int

        self.firstRetryIntervalInMilliseconds: int = firstRetry
        self.maxNumberOfAttempts: int = maxNumber

        if self.firstRetryIntervalInMilliseconds <= 0:
            raise ValueError("firstRetryIntervalInMilliseconds value"
                             "must be greater than 0.")
