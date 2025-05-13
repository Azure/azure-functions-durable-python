import unittest
from unittest.mock import Mock, call, patch
from azure.durable_functions.testing import orchestrator_generator_wrapper

from function_app import E2_BackupSiteContent


@patch('azure.durable_functions.models.TaskBase')
def create_mock_task(result, task):
  task.result = result
  return task


def mock_activity(activity_name, input):
  if activity_name == "E2_GetFileList":
    return create_mock_task(["C:/test/E2_Activity.py", "C:/test/E2_Orchestrator.py"])
  elif activity_name == "E2_CopyFileToBlob":
    return create_mock_task(1)
  raise Exception("Activity not found")


def mock_task_all(tasks):
  return create_mock_task([t.result for t in tasks])


class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationContext')
  def test_E2_BackupSiteContent(self, context):
    # Get the original method definition as seen in the function_app.py file
    func_call = E2_BackupSiteContent.build().get_user_function().orchestrator_function

    context.get_input = Mock(return_value="C:/test")
    context.call_activity = Mock(side_effect=mock_activity)
    context.task_all = Mock(side_effect=mock_task_all)

    # Execute the function code
    user_orchestrator = func_call(context)

    # Use orchestrator_generator_wrapper to get the values from the generator.
    # Processes the orchestrator in a way that is equivalent to the Durable replay logic
    values = [val for val in orchestrator_generator_wrapper(user_orchestrator)]

    expected_activity_calls = [call('E2_GetFileList', 'C:/test'),
                               call('E2_CopyFileToBlob', 'C:/test/E2_Activity.py'),
                               call('E2_CopyFileToBlob', 'C:/test/E2_Orchestrator.py')]
    
    self.assertEqual(context.call_activity.call_count, 3)
    self.assertEqual(context.call_activity.call_args_list, expected_activity_calls)

    context.task_all.assert_called_once()
    # Sums the result of task_all
    self.assertEqual(values[2], 2)
