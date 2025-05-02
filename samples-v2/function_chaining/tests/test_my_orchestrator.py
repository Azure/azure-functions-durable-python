from datetime import timedelta
import unittest
from unittest.mock import Mock, call, patch

from function_app import my_orchestrator

# A way to wrap an orchestrator generator to simplify calling it and getting the results.
# Because orchestrators in Durable Functions always accept the result of the previous activity for the next send() call, 
# we can simplify the orchestrator like this to also simplify per-test code. 
def orchestrator_generator_wrapper(generator):
  previous =  next(generator)
  yield previous
  while True:
    try:
      previous_result = None
      try:
        previous_result = previous.result
      except Exception as e: # Simulated activity exceptions, timer interrupted exceptions, anytime a task would throw. 
        previous = generator.throw(e)
      else:
        previous = generator.send(previous_result)      
      yield previous
    except StopIteration as e:
      yield e.value
      return


class MockTask():
  def __init__(self, result=None):
    self.result = result


def mock_activity(activity_name, input):
  if activity_name == "say_hello":
    return MockTask(f"Hello {input}!")
  raise Exception("Activity not found")


class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationContext')
  def test_chaining_orchestrator(self, context):
    # Get the original method definition as seen in the function_app.py file
    func_call = my_orchestrator.build().get_user_function().orchestrator_function

    context.call_activity = Mock(side_effect=mock_activity)
    # Create a generator using the method and mocked context
    user_orchestrator = func_call(context)

    # Use a method defined above to get the values from the generator. Quick unwrap for easy access
    values = [val for val in orchestrator_generator_wrapper(user_orchestrator)]

    expected_activity_calls = [call('say_hello', 'Tokyo'),
                               call('say_hello', 'Seattle'),
                               call('say_hello', 'London')]
    
    self.assertEqual(context.call_activity.call_count, 3)
    self.assertEqual(context.call_activity.call_args_list, expected_activity_calls)
    self.assertEqual(values[3], ["Hello Tokyo!", "Hello Seattle!", "Hello London!"])
