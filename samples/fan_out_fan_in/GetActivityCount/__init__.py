import json

def main(value: int):
    activity_values = [*range(int(value))]
    return json.dumps(activity_values)
