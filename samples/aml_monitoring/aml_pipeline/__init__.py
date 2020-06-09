import logging,json
import os
import time
from typing import Dict
import requests
import azure.functions as func
from azureml.core.authentication import ServicePrincipalAuthentication

from ..shared.auth_helper import get_access_token


def trigger_aml_endpoint(pipeline_endpoint, experiment_name, parameter_body, retries=3):
    aad_token = get_access_token()
    response = requests.post(
        pipeline_endpoint,
        headers=aad_token,
        json={"ExperimentName": experiment_name,
            "ParameterAssignments": parameter_body})

    if response.status_code == 200:
        success = True

    return json.loads(response.content)

# explicitly typing input_args causes exception
def main(name):
    input_args = json.loads(name)
    try:
        response = trigger_aml_endpoint(input_args["pipeline_endpoint"], input_args["experiment_name"], input_args["params"])
    except Exception as exception:
        logging.error("Got exception: ", exc_info=True)
        return exception
    return response["Id"]
