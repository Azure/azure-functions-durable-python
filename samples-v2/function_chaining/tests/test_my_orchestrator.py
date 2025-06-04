import unittest
from unittest.mock import Mock, call, patch
from azure.durable_functions.testing import orchestrator_generator_wrapper

from function_app import my_orchestrator


@patch('azure.durable_functions.models.TaskBase')
def mock_activity(activity_name, input, task):
  if activity_name == "say_hello":
    task.result = f"Hello {input}!"
    return task
  raise Exception("Activity not found")


class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationContext')
  def test_chaining_orchestrator(self, context):
    # Get the original method definition as seen in the function_app.py file
    func_call = my_orchestrator.build().get_user_function().orchestrator_function

    context.call_activity = Mock(side_effect=mock_activity)

    # Create a generator using the method and mocked context
    user_orchestrator = func_call(context)

    # Use orchestrator_generator_wrapper to get the values from the generator.
    # Processes the orchestrator in a way that is equivalent to the Durable replay logic
    values = [val for val in orchestrator_generator_wrapper(user_orchestrator)]

    expected_activity_calls = [call('say_hello', 'Tokyo'),
                               call('say_hello', 'Seattle'),
                               call('say_hello', 'London')]

    self.assertEqual(context.call_activity.call_count, 3)
    self.assertEqual(context.call_activity.call_args_list, expected_activity_calls)
    self.assertEqual(values[3], ["Hello Tokyo!", "Hello Seattle!", "Hello London!"])
