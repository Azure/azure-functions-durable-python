import azure.durable_functions as df
from datetime import timedelta

def is_valid_phone_number(phone_number: str):
    has_area_code = phone_number[0] == "+"
    is_positive_num = phone_number[1:].isdigit()
    return has_area_code and is_positive_num

def orchestrator_function(context: df.DurableOrchestrationContext):

    phone_number = context.get_input()

    if (not phone_number) or (not is_valid_phone_number(phone_number)):
        msg = "Please provide a phone number beginning with an international dialing prefix"+\
            "(+) followed by the country code, and then rest of the phone number. Example:"\
            "'+1425XXXXXXX'"
        raise Exception(msg)

    challenge_code = yield context.call_activity("SendSMSChallenge", phone_number)

    expiration = context.current_utc_datetime + timedelta(seconds=180)
    timeout_task = context.create_timer(expiration)

    authorized = False
    for _ in range(3):
        challenge_response_task = context.wait_for_external_event("SmsChallengeResponse")
        winner = yield context.task_any([challenge_response_task, timeout_task])

        if (winner == challenge_response_task):
            # We got back a response! Compare it to the challenge code
            if (challenge_response_task.result == challenge_code):
                authorized = True
                break
        else:
            # Timeout expired
            break
    
    if not timeout_task.is_completed:
        # All pending timers must be complete or canceled before the function exits.
        timeout_task.cancel()

    return authorized

main = df.Orchestrator.create(orchestrator_function)