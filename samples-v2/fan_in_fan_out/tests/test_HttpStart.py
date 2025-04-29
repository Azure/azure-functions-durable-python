import asyncio
import unittest
import azure.functions as func
from unittest.mock import AsyncMock, Mock, patch

# This path manipulation allows the test to run in the Functions pipelines, and can be removed
# if this code is used as a sample for a different project.
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from function_app import HttpStart

class TestFunction(unittest.TestCase):
  @patch('azure.durable_functions.DurableOrchestrationClient')
  def test_HttpStart(self, client):
    # Get the original method definition as seen in the function_app.py file
    # func_call = chaining_orchestrator.build().get_user_function_unmodified()
    func_call = HttpStart.build().get_user_function().client_function

    req = func.HttpRequest(method='GET',
                           body=b'{}',
                           url='/api/my_second_function',
                           route_params={"functionName": "E2_BackupSiteContent"})

    client.start_new = AsyncMock(return_value="instance_id")
    client.create_check_status_response = Mock(return_value="check_status_response")

    # Create a generator using the method and mocked context
    result = asyncio.run(func_call(req, client))

    client.start_new.assert_called_once_with("E2_BackupSiteContent", client_input={})
    client.create_check_status_response.assert_called_once_with(req, "instance_id")
    self.assertEqual(result, "check_status_response")
