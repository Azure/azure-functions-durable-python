import azure.functions as func
import azure.durable_functions as df
import unittest.main as unitmain
from unittest import IsolatedAsyncioTestCase,mock
from unittest.mock import AsyncMock, MagicMock, patch
from ..CreateEnvironmentHTTPStart import main

"""
Test class for CreateEnvironmentHTTPStart Durable HTTP Starter Function that kicks off orchestrations
Mocks the HTTP Request and expected HTTP Response from the Durable HTTP start method and tests
- no header authorization
- header with invalid client principal

Also tests Authorization decorator.
"""
class DurableFunctionsHttpStartTestCaseInvalidAuth(IsolatedAsyncioTestCase):

    async def test_durablefunctionsorchestrator_trigger_noheader(self):
        function_name = 'DurableFunctionsOrchestrator'
        instance_id = 'f86a9f49-ae1c-4c66-a60e-991c4c764fe5'
        starter = MagicMock()

        mock_request = func.HttpRequest(
            method='GET',
            body=None,
            url=f'http://localhost:7071/api/orchestrators{function_name}',
            route_params={'functionName': function_name},
        )

        mock_response = func.HttpResponse(
            body = None,
            status_code= 200,
            headers={
                "Retry-After": 10
            }
        )
        
        with patch('azure.durable_functions.DurableOrchestrationClient',spec=df.DurableOrchestrationClient) as a_mock:
            a_mock.start_new = AsyncMock()
            a_mock().start_new.return_value = instance_id
            a_mock().create_check_status_response.return_value = mock_response
            response = await main(req=mock_request, starter=starter)
            self.assertEqual(403,response.status_code)
    
    async def test_durablefunctionsorchestrator_trigger_no_allowed_groups(self):
        function_name = 'DurableFunctionsOrchestrator'
        instance_id = 'f86a9f49-ae1c-4c66-a60e-991c4c764fe5'
        starter = MagicMock()

        mock_request = func.HttpRequest(
            method='GET',
            body=None,
            url=f'http://localhost:7071/api/orchestrators{function_name}',
            route_params={'functionName': function_name},
            headers={"X-MS-CLIENT-PRINCIPAL": "ICAgICAgICB7CiAgICAgICAgICAgICJhdXRoX3R5cCI6ICJhYWQiLAogICAgICAgICAgICAiY2xhaW1zIjogW3sKICAgICAgICAgICAgICAgICJ0eXAiOiAiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSIsCiAgICAgICAgICAgICAgICAidmFsIjogIlVzZXIiCiAgICAgICAgICAgIH0sIHsKICAgICAgICAgICAgICAgICJ0eXAiOiAiZ3JvdXBzIiwKICAgICAgICAgICAgICAgICJ2YWwiOiAiZWY2ZDJkMWEtNzhlYi00YmIxLTk3YzctYmI4YThlNTA5ZTljIgogICAgICAgICAgICB9LCB7CiAgICAgICAgICAgICAgICAidHlwIjogImdyb3VwcyIsCiAgICAgICAgICAgICAgICAidmFsIjogIjNiMjMxY2UxLTI5YzEtNDQxZS1iZGRiLTAzM2Y5NjQwMTg4OCIKICAgICAgICAgICAgfSwgewogICAgICAgICAgICAgICAgInR5cCI6ICJuYW1lIiwKICAgICAgICAgICAgICAgICJ2YWwiOiAiVGVzdCBVc2VyIgogICAgICAgICAgICB9XSwKICAgICAgICAgICAgIm5hbWVfdHlwIjogImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiLAogICAgICAgICAgICAicm9sZV90eXAiOiAiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIgogICAgICAgIH0="}
        )

        mock_response = func.HttpResponse(
            body = None,
            status_code= 200,
            headers={
                "Retry-After": 10
            }
        )
        
        with patch('azure.durable_functions.DurableOrchestrationClient',spec=df.DurableOrchestrationClient) as a_mock:
            a_mock.start_new = AsyncMock()
            a_mock().start_new.return_value = instance_id
            a_mock().create_check_status_response.return_value = mock_response
            
            response = await main(req=mock_request, starter=starter)
            self.assertEqual(403,response.status_code)

if __name__ == "__main__":
    unitmain()