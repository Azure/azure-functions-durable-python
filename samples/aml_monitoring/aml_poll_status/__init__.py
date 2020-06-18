import logging,json
import os
import time
from typing import Dict
import azure.functions as func
import requests
from azureml.core import Experiment, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.pipeline.core import PipelineRun

from ..shared.aml_helper import get_run_url_from_env, get_run_logs
from ..shared.auth_helper import get_service_principal_auth

_SUBSCRIPTION_ID_ENV_NAME = "SubscriptionId"
_RESOURCE_GROUP_NAME_ENV_NAME = "ResourceGroupName"
_AML_WORKSPACE_NAME_ENV_NAME = "AMLWorkspaceName"


def get_aml_pipeline_run_status(run_id, experiment_name, retries=3):
    
    svc_pr = get_service_principal_auth()
    workspace = Workspace(
        subscription_id=os.environ[_SUBSCRIPTION_ID_ENV_NAME],
        resource_group=os.environ[_RESOURCE_GROUP_NAME_ENV_NAME],
        workspace_name=os.environ[_AML_WORKSPACE_NAME_ENV_NAME],
        auth=svc_pr)

    experiment = Experiment(workspace, experiment_name)
    pipeline_run = PipelineRun(experiment, run_id)

    response = pipeline_run.get_status()
    return response


def main(name):
    input_args = json.loads(name)
    run_id = input_args["run_id"]
    experiment_name = input_args["experiment_name"]
    status = get_aml_pipeline_run_status(run_id,experiment_name)
    run_url = get_run_url_from_env(run_id,experiment_name)
    run_logs = get_run_logs(run_id,experiment_name)
    status_code_map = {"Finished":200,"Failed":500,"Cancelled":500}
    
    response_obj = {
        "status" : status,
        "url" : run_url,
        "logs" : run_logs,
        "status_code": status_code_map[status] if status in status_code_map else 202
    }
    return json.dumps(response_obj)
