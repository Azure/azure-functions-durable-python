import os

# The imports below are only needed when the logic in get_run_logs
# is reapplied.
# from azureml.core import Experiment, Workspace
# from azureml.pipeline.core import PipelineRun

# from ..shared.auth_helper import get_service_principal_auth

_SUBSCRIPTION_ID_ENV_NAME = "SubscriptionId"
_RESOURCE_GROUP_NAME_ENV_NAME = "ResourceGroupName"
_AML_WORKSPACE_NAME_ENV_NAME = "AMLWorkspaceName"

_RUN_URL_TEMPLATE = (
    "https://mlworkspace.azure.ai/portal/subscriptions/{0}"
    "/resourceGroups/{1}/providers/Microsoft.MachineLearningServices"
    "/workspaces/{2}/experiments/{3}/runs/{4}"
)

def get_run_url_from_env(run_id: str, experiment_name: str):
    """Retrieves the appropriate environment variables.
       Uses an run url template and formats that string with the appropriate parameters.
       Return a string containing an run url based on
       function params and environment variables.

    Arguments:
        run_id string -- The string representation of the experiments run id
        experiment_name string -- The string representation of the experiments name

    Returns:
        string -- The url string that points to the current run params.
    """
    if not run_id or not experiment_name:
        raise ValueError("Missing required param")
    subscription_id = os.environ.get(_SUBSCRIPTION_ID_ENV_NAME)
    resource_group_name = os.environ.get(_RESOURCE_GROUP_NAME_ENV_NAME)
    aml_workspace_name = os.environ.get(_AML_WORKSPACE_NAME_ENV_NAME)

    return _RUN_URL_TEMPLATE.format(subscription_id, resource_group_name, \
        aml_workspace_name, experiment_name, run_id)


def get_run_logs(run_id: str, experiment_name: str):
    """Retrieves the appropriate environment variables.
       Retrieves steps for the experiments pipeline run.
       Builds a dictionary of logs for each step by the steps id.

    Arguments:
        run_id string -- The string representation of the experiments run id
        experiment_name string -- The string representation of the experiments name

    Returns:
        dictionary -- A dictionary containing logs for pipeline run
        steps keyed by the steps run id.
    """

    if not run_id or not experiment_name:
        raise ValueError("Missing required param")

    # Commenting out code due to a bug in the adf pipeline that doesn't allow
    # us to properly set the aml sdk version. This bug is results in the
    # PipelineRun to return Run objects instead of StepRun objects when
    # the get_steps object is called. Since Run objects don't have the
    # get_job_log method, the code errors out when running via adf, but not
    # when testing locally. When this bug is resolved, this code can be un
    # commented and redeployed.

    # svc_pr = get_service_principal_auth()
    # workspace = Workspace(
    #     subscription_id=os.environ[_SUBSCRIPTION_ID_ENV_NAME],
    #     resource_group=os.environ[_RESOURCE_GROUP_NAME_ENV_NAME],
    #     workspace_name=os.environ[_AML_WORKSPACE_NAME_ENV_NAME],
    #     auth=svc_pr)

    # experiment = Experiment(workspace, experiment_name)
    # pipeline_run = PipelineRun(experiment, run_id)
    # run_steps = list(pipeline_run.get_steps())

    # iterate over steps to get logs
    run_log_dict = dict()
    # for step in run_steps:
    #     j_log = step.get_job_log()
    #     run_log_dict[str(step.id)] = j_log

    return run_log_dict
