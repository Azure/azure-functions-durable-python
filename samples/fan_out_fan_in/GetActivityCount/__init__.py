import json

def main(value):
    activity_values = [*range(int(value))]
    return json.dumps(activity_values)
