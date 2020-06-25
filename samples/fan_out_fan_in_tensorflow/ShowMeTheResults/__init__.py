import json
from typing import List, Dict
def main(results: List[Dict[str,str]]) -> List[Dict[str, int]]:
    """Get a summary of the results of the predictions.

    Parameters
    ----------
    results: List[Dict[str,str]]
        Predictions

    Returns
    -------
    List[Dict[str, int]]
        Summary of predictions
    """
    analysis = {}
    analysis['images_processed'] = len(results)
    dogs = [d for d in results if d['tag'] == 'dog']
    cats = [c for c in results if c['tag'] == 'cat']
    error = [e for e in results if e['tag'] == 'error']
    analysis['number_of_dogs'] = len(dogs)
    analysis['number_of_cats'] = len(cats)
    analysis['number_failed'] = len(error)
    return analysis
