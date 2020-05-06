import json
import logging

logger = logging.getLogger('activity')


def main(value: str) -> int:
    logger.warn(f'ReturnIntWithAnnotation is called with {value}')
    return int(value)
