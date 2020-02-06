schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "isDone": {"type": "boolean"},
        "output": {"type": "string"},
        "error": {"type": "string"},
        "customStatus": {"type": "object"},
        "actions": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "functionName": {"type": "string"},
                        "actionType": {"type": "number"},
                        "input": {"oneOf": [
                            {"type": "object"},
                            {"type": "null"}
                        ]
                        },
                        "retryOptions": {
                            "type": "object",
                            "properties": {
                                "firstRetryIntervalInMilliseconds": {
                                    "type": "number",
                                    "minimum": 1},
                                "maxNumberOfAttempts": {"type": "number"}
                            },
                            "required":
                                ["firstRetryIntervalInMilliseconds", "maxNumberOfAttempts"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["functionName", "actionType"],
                    "additionalProperties": False
                }
            }
        }
    },
    "required": ["isDone"],
    "additionalProperties": False
}
