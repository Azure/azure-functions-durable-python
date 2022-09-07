#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.durable_functions.constants import ORCHESTRATION_TRIGGER, \
    ACTIVITY_TRIGGER, ORCHESTRATION_CLIENT, ENTITY_TRIGGER, ENTITY_CLIENT, \
    DURABLE_CLIENT
from azure.functions.decorators.core import Trigger, Binding


class OrchestrationTrigger(Trigger):
    """OrchestrationTrigger.

    Trigger representing an Orchestration Function.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return ORCHESTRATION_TRIGGER

    def __init__(self,
                 name: str,
                 orchestration: Optional[str] = None,
                 ) -> None:
        self.orchestration = orchestration
        super().__init__(name=name, data_type=None)


class ActivityTrigger(Trigger):
    """ActivityTrigger.

    Trigger representing a Durable Functions Activity.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return ACTIVITY_TRIGGER

    def __init__(self,
                 name: str,
                 activity: Optional[str] = None,
                 ) -> None:
        self.activity = activity
        super().__init__(name=name, data_type=None)


class EntityTrigger(Trigger):
    """EntityTrigger.

    Trigger representing an Entity Function.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return ENTITY_TRIGGER

    def __init__(self,
                 name: str,
                 entity_name: Optional[str] = None,
                 ) -> None:
        self.entity_name = entity_name
        super().__init__(name=name, data_type=None)


class EntityClient(Binding):
    """EntityClient.

    Binding representing an Entity-client object.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return ENTITY_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None,
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)


class OrchestrationClient(Binding):
    """OrchestrationClient.

    Binding representing an Orchestration-client object.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return ORCHESTRATION_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)


class DurableClient(Binding):
    """DurableClient.

    Binding representing a Durable-client object.
    """

    @staticmethod
    def get_binding_name() -> str:
        """Get the name of this Trigger, as a string.

        Returns
        -------
        str
            The string representation of this trigger.
        """
        return DURABLE_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)
