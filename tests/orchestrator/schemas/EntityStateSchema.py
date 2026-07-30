schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "entityExists": {"type": "boolean"},
        "entityState": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "isError": {"type": "boolean"},
                    "duration": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "startTime": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "result": {"type": "string"}
                },
                "required": [
                    "isError",
                    "duration",
                    "startTime",
                    "result"
                ],
                "additionalProperties": False
            }
        },
        "signals": {
            "type": "array"
        }
    },
    "required": [
        "entityExists",
        "entityState",
        "results",
        "signals"
    ],
    "additionalProperties": False
}
