import logging,json
import azure.durable_functions as df
from datetime import datetime,timedelta

def orchestrator_fn(context: df.DurableOrchestrationContext):
    pipeline_endpoint = ""
    experiment_name = ""

    # Step 1:  Kickoff the AML pipeline
    input_args= {}
    input_args["pipeline_endpoint"] = pipeline_endpoint
    input_args["experiment_name"] = experiment_name
    input_args["params"] = None
    run_id = yield context.call_activity("aml_pipeline",input_args)
    polling_interval = 60
    expiry_time = context.current_utc_datetime + timedelta(minutes=30)

    # Consider continueAsNew - use this in the samples
    # while loop explodes the history table on high scale
    while context.current_utc_datetime < expiry_time:

    # Step 2: Poll the status of the pipeline
        poll_args = {}
        poll_args["run_id"] = run_id
        poll_args["experiment_name"] = experiment_name
        job_status = yield context.call_activity("aml_poll_status",poll_args)

        # Use native Dictionary fix the generic binding conversion in worker. Can it return a Dict?
        activity_status = json.loads(job_status)
        if activity_status["status_code"] == 202:
            next_check = context.current_utc_datetime + timedelta(minutes=1)

            # Set intermediate status for anyone who wants to poll this durable function
            context.set_custom_status(activity_status)

            yield context.create_timer(next_check)

        elif activity_status["status_code"] == 500:
            job_completed = True
            raise Exception("AML Job Failed/Cancelled...")
        else:
            job_completed = True
    return activity_status

main = df.Orchestrator.create(orchestrator_fn)
