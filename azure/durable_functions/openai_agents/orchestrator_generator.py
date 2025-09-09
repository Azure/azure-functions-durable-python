import inspect
from agents import ModelProvider, ModelResponse
from agents.run import set_default_agent_runner
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.openai_agents.model_invocation_activity\
    import ActivityModelInput, ModelInvoker
from .runner import DurableOpenAIRunner
from .exceptions import YieldException
from .context import DurableAIAgentContext
from .event_loop import ensure_event_loop


async def durable_openai_agent_activity(input: str, model_provider: ModelProvider):
    """Activity logic that handles OpenAI model invocations."""
    activity_input = ActivityModelInput.from_json(input)

    model_invoker = ModelInvoker(model_provider=model_provider)
    result = await model_invoker.invoke_model_activity(activity_input)

    json_obj = ModelResponse.__pydantic_serializer__.to_json(result)
    return json_obj.decode()


def durable_openai_agent_orchestrator_generator(
        func,
        durable_orchestration_context: DurableOrchestrationContext):
    """Adapts the synchronous OpenAI Agents function to an Durable orchestrator generator."""
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
