import json
import os
from azure.cognitiveservices.search.imagesearch import ImageSearchClient
from msrest.authentication import CognitiveServicesCredentials


def main(value):
    subscription_key = os.environ.get('COGNITIVE_KEY')
    subscription_endpoint = os.environ.get('COGNITIVE_ENDPOINT')
    search_term = "dog OR cat"
    client = ImageSearchClient(endpoint=subscription_endpoint,
                               credentials=CognitiveServicesCredentials(subscription_key))

    volume_of_images = int(value)
    increment = volume_of_images if volume_of_images < 100 else 100
    image_urls = []
    offset = 0

    while len(image_urls) < volume_of_images:
        search_results = client.images.search(
            query=search_term, count=increment, offset=offset)
        image_urls.extend(
            [image.content_url for image in search_results.value])
        offset += increment
        increment = increment if offset + \
            increment < volume_of_images else volume_of_images - offset

    return json.dumps(image_urls)
