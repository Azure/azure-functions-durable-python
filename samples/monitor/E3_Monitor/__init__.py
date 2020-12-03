import azure.durable_functions as df
from datetime import timedelta
from typing import Dict

def orchestrator_function(context: df.DurableOrchestrationContext):

    monitoring_request: Dict[str, str] = context.get_input()
    repo_url: str = monitoring_request["repo"]
    phone: str = monitoring_request["phone"]

    # Expiration of the repo monitoring
    expiry_time = context.current_utc_datetime + timedelta(minutes=5)
    while context.current_utc_datetime < expiry_time:
        # Count the number of issues in the repo (the GitHub API caps at 30 issues per page)
        too_many_issues = yield context.call_activity("E3_TooManyOpenIssues", repo_url)

        # If we detect too many issues, we text the provided phone number
        if too_many_issues:
            # Extract URLs of GitHub issues, and return them
            yield context.call_activity("E3_SendAlert", phone)
            break
        else:

            # Reporting the number of statuses found
            status = f"The repository does not have too many issues, for now ..."
            context.set_custom_status(status)
        
            # Schedule a new "wake up" signal
            next_check = context.current_utc_datetime + timedelta(minutes=1)
            yield context.create_timer(next_check)

    return "Monitor completed!"

main = df.Orchestrator.create(orchestrator_function)