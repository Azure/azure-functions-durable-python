import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnString is called with {value}')
    return value
