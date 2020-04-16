import json
import logging

logger = logging.getLogger('activity')


def main(value: int):
	logger.warn(f'ReturnSetOfInt is called with {value}')
	result = set()
	result.add(value)
	result.add(value + 1)
	result.add(value + 2)
	return result
