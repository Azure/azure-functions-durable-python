from uuid import uuid5, NAMESPACE_OID

from azure.durable_functions.models import DurableOrchestrationContext
from azure.durable_functions.constants import DATETIME_STRING_FORMAT

URL_NAMESPACE: str = "9e952958-5e33-4daf-827f-2fa12937b875"


def _create_deterministic_guid(namespace_value: str, name: str) -> str:
    namespace_uuid = uuid5(NAMESPACE_OID, namespace_value)
    return str(uuid5(namespace_uuid, name))


# noinspection PyProtectedMember
def new_guid(context: DurableOrchestrationContext) -> str:
    guid_name_value = \
        f"{context.instance_id}" \
        f"_{context.current_utc_datetime.strftime(DATETIME_STRING_FORMAT)}" \
        f"_{context._new_guid_counter}"
    context._new_guid_counter += 1
    return _create_deterministic_guid(URL_NAMESPACE, guid_name_value)
