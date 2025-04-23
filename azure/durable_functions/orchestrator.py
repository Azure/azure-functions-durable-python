"""Durable Orchestrator.

Responsible for orchestrating the execution of the user defined generator
function.
"""
from azure.durable_functions.models.TaskOrchestrationExecutor import TaskOrchestrationExecutor
from typing import Callable, Any, Generator

from .models import DurableOrchestrationContext

import azure.functions as func


class OrchestrationHandler(Callable):
    """Durable Orchestration Handler.

    A callable class that wraps the user defined generator function for execution by the Python worker
    and also allows access to the original method for unit testing
    """

    def __init__(self, func: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]):
        """
        Create a new orchestrator handler for the user defined orchestrator function.

        Parameters
        ----------
        func: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]
            The user defined orchestrator function.
        """
        self.orchestrator_function = func

    def __call__(self, context: func.OrchestrationContext) -> str:
        """Handle the execution of the user defined orchestrator function.

        Serializes a DurableOrchestrationContext object from the input context and
        passes it to the entity function.

        Parameters
        ----------
        context : func.OrchestrationContext
            The DF orchestration context"""
        context_body = getattr(context, "body", None)
        if context_body is None:
            context_body = context
        return Orchestrator(self.orchestrator_function).handle(
            DurableOrchestrationContext.from_json(context_body)
        )


class Orchestrator:
    """Durable Orchestration Class.

    Responsible for orchestrating the execution of the user defined generator
    function.
    """

    def __init__(self,
                 activity_func: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]):
        """Create a new orchestrator for the user defined generator.

        Responsible for orchestrating the execution of the user defined
        generator function.
        :param activity_func: Generator function to orchestrate.
        """
        self.fn: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]] = activity_func
        self.task_orchestration_executor = TaskOrchestrationExecutor()

    def handle(self, context: DurableOrchestrationContext) -> str:
        """Handle the orchestration of the user defined generator function.

        Parameters
        ----------
        context : DurableOrchestrationContext
            The DF orchestration context

        Returns
        -------
        str
            The JSON-formatted string representing the user's orchestration
            state after this invocation
        """
        self.durable_context = context
        return self.task_orchestration_executor.execute(context, context.histories, self.fn)

    @classmethod
    def create(cls, fn: Callable[[DurableOrchestrationContext], Generator[Any, Any, Any]]) \
            -> Callable[[Any], str]:
        """Create an instance of the orchestration class.

        Parameters
        ----------
        fn: Callable[[DurableOrchestrationContext], Iterator[Any]]
            Generator function that needs orchestration

        Returns
        -------
        OrchestrationHandler
            Orchestration handler callable class for the newly created orchestration client
        """
        return OrchestrationHandler(fn)
