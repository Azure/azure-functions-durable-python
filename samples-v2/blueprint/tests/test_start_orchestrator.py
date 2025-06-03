import asyncio
import unittest
import azure.functions as func
from unittest.mock import AsyncMock, Mock, patch

from durable_blueprints import start_orchestrator

class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationClient')
  def test_HttpStart(self, client):
    # Get the original method definition as seen in the function_app.py file
    func_call = start_orchestrator.build().get_user_function().client_function

    req = func.HttpRequest(method='GET',
                           body=b'{}',
                           url='/api/my_second_function')

    client.start_new = AsyncMock(return_value="instance_id")
    client.create_check_status_response = Mock(return_value="check_status_response")

    # Execute the function code
    result = asyncio.run(func_call(req, client))

    client.start_new.assert_called_once_with("my_orchestrator")
    client.create_check_status_response.assert_called_once_with(req, "instance_id")
    self.assertEqual(result, "check_status_response")
