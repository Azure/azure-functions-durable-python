import json


def main(value):
    """Get a summary of the results of the predictions.

    Arguments:
        value List of the predictions

    Returns:
        JSON serializable string representing the summary of the predictions
    """
    results = json.loads(value)
    analysis = {}
    analysis['images_processed'] = len(results)
    dogs = [d for d in results if d['tag'] == 'dog']
    cats = [c for c in results if c['tag'] == 'cat']
    error = [e for e in results if e['tag'] == 'error']
    analysis['number_of_dogs'] = len(dogs)
    analysis['number_of_cats'] = len(cats)
    analysis['number_failed'] = len(error)
    return json.dumps(analysis)
