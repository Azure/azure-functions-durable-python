from typing import Generator, Any, Union

from azure.durable_functions.models import TaskBase


def orchestrator_generator_wrapper(
        generator: Generator[TaskBase, Any, Any]) -> Generator[Union[TaskBase, Any], None, None]:
    """Wrap a user-defined orchestrator function in a way that simulates the Durable replay logic.

    Parameters
    ----------
    generator: Generator[TaskBase, Any, Any]
        Generator orchestrator as defined in the user function app. This generator is expected
        to yield a series of TaskBase objects and receive the results of these tasks until
        returning the result of the orchestrator.

    Returns
    -------
    Generator[Union[TaskBase, Any], None, None]
        A simplified version of the orchestrator which takes no inputs. This generator will
        yield back the TaskBase objects that are yielded from the user orchestrator as well
        as the final result of the orchestrator. Exception handling is also simulated here
        in the same way as replay, where tasks returning exceptions are thrown back into the
        orchestrator.
    """
    previous = next(generator)
    yield previous
    while True:
        try:
            previous_result = None
            try:
                previous_result = previous.result
            except Exception as e:
                # Simulated activity exceptions, timer interrupted exceptions,
                # or anytime a task would throw.
                previous = generator.throw(e)
            else:
                previous = generator.send(previous_result)
            yield previous
        except StopIteration as e:
            yield e.value
            return
