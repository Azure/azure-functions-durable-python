import json
import random


def main(value):
    value_generation = json.loads(value)
    random.seed(value_generation['seed'])
    config = value_generation['config']
    activity_values = [{"index": v}
                       for v in range(int(config['instances']))]
    return json.dumps(activity_values)
