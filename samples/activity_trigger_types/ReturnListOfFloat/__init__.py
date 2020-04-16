import json
import logging

logger = logging.getLogger('activity')


def main(value: str):
	logger.warn(f'ReturnListOfFloat is called with {value}')
	float_value = float(value)
	result = []
	result.append(float_value)
	result.append(float_value + 1.0)
	result.append(float_value + 2.0)
	return result
