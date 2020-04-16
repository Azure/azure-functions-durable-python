import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnBool is called with {value}')
    if value == "1":
        return True
    else:
        return False
