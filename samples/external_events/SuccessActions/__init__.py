import logging
import json


def main(args: str) -> str:
    logging.info(f"Activity Triggered: SuccessActions")

    args= json.loads(args)
    logging.info("Activity arguments: {}".format(args))
    return f'Hello {args["name"]}'
