import logging
import json

def main(args: str) -> str:
    """Activity function to raise an external event to the orchestrator

    Parameters
    ----------
    req: func.HttpRequest
        An HTTP Request object, it can be used to parse URL
        parameters.

    Returns
    -------
    str
        A 'Hello-string' to the argument passed in via args
    """
    logging.warning(f"Activity Triggered: SuccessActions")
    args= json.loads(args)
    return f'Hello {args["name"]}'
