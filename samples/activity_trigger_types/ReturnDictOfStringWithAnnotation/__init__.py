from typing import Dict
import json
import logging

logger = logging.getLogger('activity')


def main(value: str) -> Dict[str, str]:
    logger.warn(f'ReturnDictOfStringWithAnnotation is called with {value}')
    result = {}
    result[value] = value
    return result
