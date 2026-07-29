from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.models.actions.ActionType import ActionType


def _action_schema(action_type, properties, required):
    return {
        "type": "object",
        "properties": {
            "actionType": {"const": action_type.value},
            **properties
        },
        "required": ["actionType", *required],
        "additionalProperties": False
    }


_retry_options = {
    "type": "object",
    "properties": {
        "firstRetryIntervalInMilliseconds": {
            "type": "integer",
            "minimum": 1
        },
        "maxNumberOfAttempts": {"type": "integer"}
    },
    "required": [
        "firstRetryIntervalInMilliseconds",
        "maxNumberOfAttempts"
    ],
    "additionalProperties": False
}

_entity_action_properties = {
    "instanceId": {"type": "string"},
    "operation": {"type": "string"},
    "input": {"type": "string"}
}

_sub_orchestrator_properties = {
    "functionName": {"type": "string"},
    "input": {"type": "string"},
    "instanceId": {"type": ["string", "null"]},
    "version": {"type": ["string", "null"]}
}

_http_request = {
    "type": "object",
    "properties": {
        "method": {"type": "string"},
        "uri": {"type": "string"},
        "content": {"type": ["string", "null"]},
        "headers": {
            "type": ["object", "null"],
            "additionalProperties": {"type": "string"}
        },
        "tokenSource": {
            "type": "object",
            "properties": {
                "kind": {"const": "AzureManagedIdentity"},
                "resource": {"type": "string"}
            },
            "required": ["kind", "resource"],
            "additionalProperties": False
        }
    },
    "required": ["method", "uri"],
    "additionalProperties": False
}

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "definitions": {
        "action": {
            "oneOf": [
                _action_schema(
                    ActionType.CALL_ACTIVITY,
                    {
                        "functionName": {"type": "string"},
                        "input": {"type": "string"}
                    },
                    ["functionName", "input"]
                ),
                _action_schema(
                    ActionType.CALL_ACTIVITY_WITH_RETRY,
                    {
                        "functionName": {"type": "string"},
                        "input": {"type": "string"},
                        "retryOptions": _retry_options
                    },
                    ["functionName", "input", "retryOptions"]
                ),
                _action_schema(
                    ActionType.CALL_SUB_ORCHESTRATOR,
                    _sub_orchestrator_properties,
                    ["functionName", "input"]
                ),
                _action_schema(
                    ActionType.CALL_SUB_ORCHESTRATOR_WITH_RETRY,
                    {
                        **_sub_orchestrator_properties,
                        "retryOptions": _retry_options
                    },
                    ["functionName", "input", "retryOptions"]
                ),
                _action_schema(
                    ActionType.CONTINUE_AS_NEW,
                    {"input": {"type": "string"}},
                    ["input"]
                ),
                _action_schema(
                    ActionType.CREATE_TIMER,
                    {
                        "fireAt": {
                            "type": "string",
                            "format": "date-time"
                        },
                        "isCanceled": {"type": "boolean"}
                    },
                    ["fireAt", "isCanceled"]
                ),
                _action_schema(
                    ActionType.WAIT_FOR_EXTERNAL_EVENT,
                    {
                        "externalEventName": {"type": "string"},
                        "reason": {"const": "ExternalEvent"}
                    },
                    ["externalEventName", "reason"]
                ),
                _action_schema(
                    ActionType.CALL_ENTITY,
                    _entity_action_properties,
                    ["instanceId", "operation", "input"]
                ),
                _action_schema(
                    ActionType.CALL_HTTP,
                    {"httpRequest": _http_request},
                    ["httpRequest"]
                ),
                _action_schema(
                    ActionType.SIGNAL_ENTITY,
                    _entity_action_properties,
                    ["instanceId", "operation", "input"]
                ),
                _action_schema(
                    ActionType.WHEN_ANY,
                    {
                        "compoundActions": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/action"}
                        }
                    },
                    ["compoundActions"]
                ),
                _action_schema(
                    ActionType.WHEN_ALL,
                    {
                        "compoundActions": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/action"}
                        }
                    },
                    ["compoundActions"]
                )
            ]
        }
    },
    "properties": {
        "isDone": {"type": "boolean"},
        "schemaVersion": {
            "type": "integer",
            "enum": [ReplaySchema.V2.value, ReplaySchema.V3.value]
        },
        "output": {},
        "error": {"type": "string"},
        "customStatus": {},
        "actions": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"$ref": "#/definitions/action"}
            }
        }
    },
    "required": ["isDone", "actions"],
    "additionalProperties": False
}
