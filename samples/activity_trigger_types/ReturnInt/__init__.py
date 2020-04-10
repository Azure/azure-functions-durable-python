import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnInt is called with {value}')
    return int(value)
