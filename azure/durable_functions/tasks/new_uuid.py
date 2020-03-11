from uuid import uuid5, NAMESPACE_OID

from azure.durable_functions.models import DurableOrchestrationContext
from azure.durable_functions.constants import DATETIME_STRING_FORMAT

URL_NAMESPACE: str = "9e952958-5e33-4daf-827f-2fa12937b875"


def _create_deterministic_uuid(namespace_value: str, name: str) -> str:
    namespace_uuid = uuid5(NAMESPACE_OID, namespace_value)
    return str(uuid5(namespace_uuid, name))


def new_uuid(context: DurableOrchestrationContext) -> str:
    """Create a new UUID that is safe for replay within an orchestration or operation.

    The default implementation of this method creates a name-based UUID
    using the algorithm from RFC 4122 §4.3. The name input used to generate
    this value is a combination of the orchestration instance ID and an
    internally managed sequence number.

    Parameters
    ----------
    context : DurableOrchestrationContext
        Provides reference to the instance id, current_utc_datetime and a new_uuid_counter
        attribute that is combined together to form that name that is used for the V5 UUID.

    Returns
    -------
    str
        New UUID that is safe for replay within an orchestration or operation.
    """
    uuid_name_value = \
        f"{context.instance_id}" \
        f"_{context.current_utc_datetime.strftime(DATETIME_STRING_FORMAT)}" \
        f"_{context._new_uuid_counter}"
    context._new_uuid_counter += 1
    return _create_deterministic_uuid(URL_NAMESPACE, uuid_name_value)
