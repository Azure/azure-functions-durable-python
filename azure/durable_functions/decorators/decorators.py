from .triggers import OrchestrationTrigger, ActivityTrigger, EntityTrigger,\
    EntityClient, OrchestrationClient, DurableClient
from typing import Callable, Optional
from azure.durable_functions.entity import Entity
from azure.durable_functions.orchestrator import Orchestrator
from typing import Union
from azure.functions import FunctionRegister, TriggerApi, BindingApi, AuthLevel


class DurableFunctionApp(FunctionRegister, TriggerApi, BindingApi):
    """Durable Functions (DF) app.

    Exports the decorators required to register DF Function-types.
    """

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Instantiate a Durable Functions app with which to register Functions.

        Parameters
        ----------
        http_auth_level: strUnion[AuthLevel, str]
            Authorization level required for Function invocation.
            Defaults to AuthLevel.Function.

        Returns
        -------
        DurableFunctionApp
            New instance of a Durable Functions app
        """
        super().__init__(auth_level=http_auth_level)

    def _configure_entity_callable(self, wrap) -> Callable:
        """Obtain decorator to construct an Entity class from a user-defined Function.

        In the old programming model, this decorator's logic was unavoidable boilerplate
        in user-code. Now, this is handled internally by the framework.

        Parameters
        ----------
        wrap: Callable
            The next decorator to be applied.

        Returns
        -------
        Callable
            The function to construct an Entity class from the user-defined Function,
            wrapped by the next decorator in the sequence.
        """
        def decorator(entity_func):
            # Construct an entity based on the end-user code
            handle = Entity.create(entity_func)

            # invoke next decorator, with the Entity as input
            handle.__name__ = entity_func.__name__
            return wrap(handle)

        return decorator

    def _configure_orchestrator_callable(self, wrap) -> Callable:
        """Obtain decorator to construct an Orchestrator class from a user-defined Function.

        In the old programming model, this decorator's logic was unavoidable boilerplate
        in user-code. Now, this is handled internally by the framework.

        Parameters
        ----------
        wrap: Callable
            The next decorator to be applied.

        Returns
        -------
        Callable
            The function to construct an Orchestrator class from the user-defined Function,
            wrapped by the next decorator in the sequence.
        """
        def decorator(orchestrator_func):
            # Construct an orchestrator based on the end-user code
            handle = Orchestrator.create(orchestrator_func)

            # invoke next decorator, with the Orchestrator as input
            handle.__name__ = orchestrator_func.__name__
            return wrap(handle)

        return decorator

    def on_orchestration_change(self, name: str,
                                orchestration: Optional[str] = None):
        """Register an Orchestrator Function.

        Parameters
        ----------
        name: str
            Parameter name of the DurableOrchestrationContext object.
        orchestration: Optional[str]
            Name of Orchestrator Function.
            The value is None by default, in which case the name of the method is used.
        """
        @self._configure_orchestrator_callable
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=OrchestrationTrigger(name=name,
                                                 orchestration=orchestration))
                return fb

            return decorator()

        return wrap

    def on_activity_change(self, name: str,
                           activity: Optional[str] = None):
        """Register an Activity Function.

        Parameters
        ----------
        name: str
            Parameter name of the Activity input.
        activity: Optional[str]
            Name of Activity Function.
            The value is None by default, in which case the name of the method is used.
        """
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ActivityTrigger(name=name,
                                            activity=activity))
                return fb

            return decorator()

        return wrap

    def on_entity_change(self, name: str,
                         entity_name: Optional[str] = None):
        """Register an Entity Function.

        Parameters
        ----------
        name: str
            Parameter name of the Entity input.
        entity_name: Optional[str]
            Name of Entity Function.
            The value is None by default, in which case the name of the method is used.
        """
        @self._configure_entity_callable
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EntityTrigger(name=name,
                                          entity_name=entity_name))
                return fb

            return decorator()

        return wrap

    def entity_client(self, name: str, task_hub: Optional[str] = None,
                      connection_name: Optional[str] = None):
        """Register an Entity-client Function.

        Parameters
        ----------
        name: str
            <TODO>- this shouldn't be needed.
        task_hub: Optional[str]
            Used in scenarios where multiple function apps share the same storage account
            but need to be isolated from each other. If not specified, the default value
            from host.json is used.
            This value must match the value used by the target orchestrator functions.
        connection_name: Optional[str]
            The name of an app setting that contains a storage account connection string.
            The storage account represented by this connection string must be the same one
            used by the target orchestrator functions. If not specified, the default storage
            account connection string for the function app is used.
        """
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EntityClient(name=name,
                                         task_hub=task_hub,
                                         connection_name=connection_name))
                return fb

            return decorator()

        return wrap

    def orchestration_client(self,
                             name: str,
                             task_hub: Optional[str] = None,
                             connection_name: Optional[str] = None
                             ):
        """Register an Orchestration-client Function.

        Parameters
        ----------
        name: str
            <TODO>- this shouldn't be needed.
        task_hub: Optional[str]
            Used in scenarios where multiple function apps share the same storage account
            but need to be isolated from each other. If not specified, the default value
            from host.json is used.
            This value must match the value used by the target orchestrator functions.
        connection_name: Optional[str]
            The name of an app setting that contains a storage account connection string.
            The storage account represented by this connection string must be the same one
            used by the target orchestrator functions. If not specified, the default storage
            account connection string for the function app is used.
        """
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=OrchestrationClient(
                        name=name,
                        task_hub=task_hub,
                        connection_name=connection_name))
                return fb

            return decorator()

        return wrap

    def durable_client(self,
                       name: str,
                       task_hub: Optional[str] = None,
                       connection_name: Optional[str] = None
                       ):
        """Register a Durable-client Function.

        Parameters
        ----------
        name: str
            <TODO>- this shouldn't be needed.
        task_hub: Optional[str]
            Used in scenarios where multiple function apps share the same storage account
            but need to be isolated from each other. If not specified, the default value
            from host.json is used.
            This value must match the value used by the target orchestrator functions.
        connection_name: Optional[str]
            The name of an app setting that contains a storage account connection string.
            The storage account represented by this connection string must be the same one
            used by the target orchestrator functions. If not specified, the default storage
            account connection string for the function app is used.
        """
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DurableClient(name=name,
                                          task_hub=task_hub,
                                          connection_name=connection_name))
                return fb

            return decorator()

        return wrap
