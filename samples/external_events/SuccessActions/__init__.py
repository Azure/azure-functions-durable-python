import logging
import json


def main(args: str) -> str:
    logging.warning(f"Activity Triggered: SuccessActions")
    args = json.loads(args)
    return f'Hello {args["name"]}'
