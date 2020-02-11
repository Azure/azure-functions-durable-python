from datetime import datetime, timedelta
import json

from .predict import predict_image_from_url


def main(value):
    run_info = json.loads(value)
    instance_info = run_info['instance_info']
    images = run_info['images']

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

    output = {"instance_info": instance_info,
              "prediction_results": prediction_results}

    return json.dumps(output)
