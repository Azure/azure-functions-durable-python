import unittest
from unittest.mock import Mock, call, patch

from function_app import E2_BackupSiteContent

# A way to wrap an orchestrator generator to simplify calling it and getting the results.
# Because orchestrators in Durable Functions always accept the result of the previous activity for the next send() call, 
# we can unwrap the orchestrator generator using this method to simplify per-test code. 
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
  if activity_name == "E2_GetFileList":
    return MockTask(["C:/test/E2_Activity.py", "C:/test/E2_Orchestrator.py"])
  return MockTask(input)


class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationContext')
  def test_E2_BackupSiteContent(self, context):
    # Get the original method definition as seen in the function_app.py file
    func_call = E2_BackupSiteContent.build().get_user_function().orchestrator_function

    context.get_input = Mock(return_value="C:/test")
    context.call_activity = Mock(side_effect=mock_activity)
    context.task_all = Mock(return_value=MockTask([100, 200, 300]))

    # Execute the function code
    user_orchestrator = func_call(context)

    # Use a method defined above to get the values from the generator. Quick unwrap for easy access
    values = [val for val in orchestrator_generator_wrapper(user_orchestrator)]

    expected_activity_calls = [call('E2_GetFileList', 'C:/test'),
                               call('E2_CopyFileToBlob', 'C:/test/E2_Activity.py'),
                               call('E2_CopyFileToBlob', 'C:/test/E2_Orchestrator.py')]
    
    self.assertEqual(context.call_activity.call_count, 3)
    self.assertEqual(context.call_activity.call_args_list, expected_activity_calls)

    context.task_all.assert_called_once()
    # Sums the result of task_all
    self.assertEqual(values[2], 600)
