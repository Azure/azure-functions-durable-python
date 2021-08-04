import os
import azure.functions as func
import azure.durable_functions as df
import unittest.main as unitmain
from unittest import IsolatedAsyncioTestCase,mock
from unittest.mock import AsyncMock, MagicMock, patch

# Patch any required environment variable for the Auth decorator (authorization.py) just before importing
# for the patch to take effect
with patch.dict(os.environ,{"SecurityGroups_SUBSCRIPTION_MANAGERS":"ef6d2d1a-78eb-4bb1-97c7-bb8a8e509e9c"}):
    from ..CreateEnvironmentHTTPStart import main

"""
Test class for CreateEnvironmentHTTPStart Durable HTTP Starter Function that kicks off orchestrations
Mocks the HTTP Request and expected HTTP Response from the Durable HTTP start method and tests
- invalid route params
"""
class DurableFunctionsHttpStartTestCaseInvalidRouteParams(IsolatedAsyncioTestCase):

    async def test_durablefunctionsorchestrator_trigger_invalid_client_name(self):
        function_name = 'DurableFunctionsOrchestrator'
        instance_id = 'f86a9f49-ae1c-4c66-a60e-991c4c764fe5'
        productName = 'test_product'
        clientName = 'microsoft'
        environmentName = 'production'
        starter = MagicMock()

        mock_request = func.HttpRequest(
            method='POST',
            body=b'{"sub_product":"test"}',
            url=f'http://localhost:7071/api/orchestrators/product/{productName}/clients/{clientName}/environments/{environmentName}/',
            route_params={
                'clientName' : None                
            },
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
            self.assertEqual(400,response.status_code)

if __name__ == "__main__":
    unitmain()