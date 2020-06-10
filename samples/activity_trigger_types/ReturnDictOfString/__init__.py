import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
    logger.warn(f'ReturnDictOfString is called with {value}')
    result = {}
    result[value] = value
    return result
