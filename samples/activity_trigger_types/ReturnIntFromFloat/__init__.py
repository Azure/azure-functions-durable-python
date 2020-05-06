import math
import logging

logger = logging.getLogger('activity')


def main(value: float):
    logger.warn(f'ReturnIntFromFloat is called with {value}')
    return math.floor(value)
