import azure.durable_functions as df
from datetime import timedelta

def orchestrator_function(context: df.DurableOrchestrationContext):

    repo_url: str = context.get_input()

    issues = []
    # Expiration of the repo monitoring
    expiry_time = context.current_utc_datetime + timedelta(minutes=5)
    while context.current_utc_datetime < expiry_time:
        # Count the number of issues in the repo (the GitHub API caps at 30 issues per page)
        issues = yield context.call_activity("E3_CountIssues", repo_url)

        # IF we detect 3 or more issues, we return
        num_issues = len(issues)
        if num_issues >= 3:
            break

        # Reporting the number of statuses found
        status = f"Found {num_issues} out of 3 issues"
        context.set_custom_status(status)
        
        # Schedule a new "wake up" signal
        next_check = context.current_utc_datetime + timedelta(minutes=1)
        yield context.create_timer(next_check)

    # Extract URLs of GitHub issues, and return them
    urls = yield context.call_activity("E3_ExtractURLs", issues)
    return urls

main = df.Orchestrator.create(orchestrator_function)