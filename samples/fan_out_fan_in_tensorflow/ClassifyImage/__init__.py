from datetime import datetime, timedelta
import json

from .predict import predict_image_from_url


def main(value):
    """Classify the list of images based on whether they are a dog or cat
    
    Arguments:
        value list of image URLs to predict
    
    Returns:
        List of the of the results of the predictions
    """
    images = json.loads(value)

    prediction_results = []
    for image_url in images:
        results = predict_image_from_url(image_url)
        if results is not None:
            prediction_results.append({"tag": results["predictedTagName"], "url": image_url})
        else:
            prediction_results.append({"tag": "error", "url": image_url})

    return json.dumps(prediction_results)
