from functools import wraps
import inspect
import sys
import azure.functions as func
from agents.run import set_default_agent_runner
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from .runner import DurableOpenAIRunner
from .exceptions import YieldException
from .context import DurableAIAgentContext
from .event_loop import ensure_event_loop
from .model_invocation_activity import create_invoke_model_activity


# Global registry to track which apps have been set up
_registered_apps = set()


def _setup_durable_openai_agent(app: func.FunctionApp):
    """Set up the Durable OpenAI Agent framework for the given FunctionApp.

    This is automatically called when using the framework decorators.
    """
    app_id = id(app)
    if app_id not in _registered_apps:
        create_invoke_model_activity(app)
        _registered_apps.add(app_id)


def _find_function_app_in_module(module):
    """Find a FunctionApp instance in the given module.

    Returns the first FunctionApp instance found, or None if none found.
    """
    if not hasattr(module, '__dict__'):
        return None

    for name, obj in module.__dict__.items():
        if isinstance(obj, func.FunctionApp):
            return obj
    return None


def _auto_setup_durable_openai_agent(decorated_func):
    """Automatically detect and setup the FunctionApp for Durable OpenAI Agents.

    This finds the FunctionApp in the same module as the decorated function.
    """
    try:
        # Get the module where the decorated function is defined
        func_module = sys.modules.get(decorated_func.__module__)
        if func_module is None:
            return

        # Find the FunctionApp instance in that module
        app = _find_function_app_in_module(func_module)
        if app is not None:
            _setup_durable_openai_agent(app)
    except Exception:
        # Silently fail if auto-setup doesn't work
        # The user can still manually call create_invoke_model_activity if needed
        pass


def durable_openai_agent_orchestrator(func):
    """Decorate Azure Durable Functions orchestrators that use OpenAI Agents."""
    # Auto-setup: Find and configure the FunctionApp when decorator is applied
    _auto_setup_durable_openai_agent(func)

    @wraps(func)
    def wrapper(durable_orchestration_context: DurableOrchestrationContext):
        ensure_event_loop()
        durable_ai_agent_context = DurableAIAgentContext(durable_orchestration_context)
        durable_openai_runner = DurableOpenAIRunner(context=durable_ai_agent_context)
        set_default_agent_runner(durable_openai_runner)

        if inspect.isgeneratorfunction(func):
            gen = iter(func(durable_ai_agent_context))
            try:
                # prime the subiterator
                value = next(gen)
                yield from durable_ai_agent_context._yield_and_clear_tasks()
                while True:
                    try:
                        # send whatever was sent into us down to the subgenerator
                        yield from durable_ai_agent_context._yield_and_clear_tasks()
                        sent = yield value
                    except GeneratorExit:
                        # ensure the subgenerator is closed
                        if hasattr(gen, "close"):
                            gen.close()
                        raise
                    except BaseException as exc:
                        # forward thrown exceptions if possible
                        if hasattr(gen, "throw"):
                            value = gen.throw(type(exc), exc, exc.__traceback__)
                        else:
                            raise
                    else:
                        # normal path: forward .send (or .__next__)
                        if hasattr(gen, "send"):
                            value = gen.send(sent)
                        else:
                            value = next(gen)
            except StopIteration as e:
                yield from durable_ai_agent_context._yield_and_clear_tasks()
                return e.value
            except YieldException as e:
                yield from durable_ai_agent_context._yield_and_clear_tasks()
                yield e.task
        else:
            try:
                result = func(durable_ai_agent_context)
                return result
            except YieldException as e:
                yield from durable_ai_agent_context._yield_and_clear_tasks()
                yield e.task
            finally:
                yield from durable_ai_agent_context._yield_and_clear_tasks()

    return wrapper
