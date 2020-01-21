from typing import Any, Dict

from .utils.json_utils import add_attrib


class RetryOptions:
    def __init__(self, first_retry_interval_in_milliseconds: int, max_number_of_attempts: int):
        self.first_retry_interval_in_milliseconds: int = first_retry_interval_in_milliseconds
        self.max_number_of_attempts: int = max_number_of_attempts

        if self.first_retry_interval_in_milliseconds <= 0:
            raise ValueError("first_retry_interval_in_milliseconds value"
                             "must be greater than 0.")

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'first_retry_interval_in_milliseconds',
                   'firstRetryIntervalInMilliseconds')
        add_attrib(json_dict, self, 'max_number_of_attempts', 'maxNumberOfAttempts')
        return json_dict
