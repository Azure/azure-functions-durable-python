import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnFloat is called with {value}')
    return float(value)
