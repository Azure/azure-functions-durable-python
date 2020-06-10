import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnBytes is called with {value}')
    return value.encode('utf-8')
