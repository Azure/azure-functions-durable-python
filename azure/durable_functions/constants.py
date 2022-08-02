"""Constants used to determine the local running context."""
DEFAULT_LOCAL_HOST: str = 'localhost:7071'
DEFAULT_LOCAL_ORIGIN: str = f'http://{DEFAULT_LOCAL_HOST}'
DATETIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
HTTP_ACTION_NAME = 'BuiltIn::HttpActivity'
ORCHESTRATION_TRIGGER = "orchestrationTrigger"
ORCHESTRATION_CLIENT = "orchestrationClient"
ACTIVITY_TRIGGER = "activityTrigger"
ENTITY_TRIGGER = "entityTrigger"
ENTITY_CLIENT = "entityClient"
DURABLE_CLIENT = "durableClient"
