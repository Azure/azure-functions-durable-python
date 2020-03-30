import json

def main(value: str) -> str:
    """Get a summary of the results of the predictions.

    Parameters
    ----------
    value: str
        List-formatted string of the predictions

    Returns
    -------
    str
        JSON-formatted string representing the summary of predictions
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
