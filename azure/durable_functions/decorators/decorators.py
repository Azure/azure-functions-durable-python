from triggers import OrchestrationTrigger, ActivityTrigger, EntityTrigger, EntityClient, OrchestrationClient, DurableClient
from typing import Callable, Dict, List, Optional
from azure.durable_functions.entity import Entity
from azure.durable_functions.orchestrator import Orchestrator

class FunctionApp: # TODO: this doesn't seem right

    def _configure_entity_callable(self, wrap) -> Callable:
        """Decorator function on user defined function to create and return
            :class:`FunctionBuilder` object from :class:`Callable` func.
        """

        def decorator(entity_func):
            handle = Entity.create(entity_func)
            handle.__name__ = entity_func.__name__

            return wrap(handle)

        return decorator

    def _configure_orchestrator_callable(self, wrap) -> Callable:
        """Decorator function on user defined function to create and return
            :class:`FunctionBuilder` object from :class:`Callable` func.
        """

        def decorator(orchestrator_func):
            handle = Orchestrator.create(orchestrator_func)
            handle.__name__ = orchestrator_func.__name__

            return wrap(handle)

        return decorator

    def on_orchestration_change(self, name: str,
                                orchestration: Optional[str] = None):
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