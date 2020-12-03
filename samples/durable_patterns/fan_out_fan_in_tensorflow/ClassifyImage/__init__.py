from datetime import datetime, timedelta
from typing import List, Dict
import json
from .predict import predict_image_from_url


def main(images: List[str]) -> List[Dict[str, str]]:
    """Classify the list of images based on whether they are a dog or cat
    
    Parameters
    ----------
    images: List[str]
        List of image URLs to predict
    
    Returns
    -------
    List[Dict[str]]
        JSON-formatted string of the prediction results
    """

    prediction_results = []
    for image_url in images:
        results = predict_image_from_url(image_url)
        if results is not None:
            prediction_results.append({
                'tag': results['predictedTagName'],
                'url': image_url
            })
        else:
            prediction_results.append({
                'tag': 'error',
                'url': image_url
            })

    return prediction_results
