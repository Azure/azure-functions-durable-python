import json
import os
from azure.cognitiveservices.search.imagesearch import ImageSearchClient
from msrest.authentication import CognitiveServicesCredentials


def _get_cognitive_services_client() -> ImageSearchClient:
    """Get the cognitive service client to run the searches against.

    Ensure there is a COGNITIVE_KEY and COGNITIVE_ENDPOINT configured in your
    app setting for the function, or your local.settings.json file when running
    locally.

    Returns
    -------
    client: ImageSearchClient
        Cognitive service client
    """
    subscription_key = os.environ.get('COGNITIVE_KEY')
    subscription_endpoint = os.environ.get('COGNITIVE_ENDPOINT')
    client = ImageSearchClient(endpoint=subscription_endpoint,
                               credentials=CognitiveServicesCredentials(subscription_key))
    return client


def main(value: str) -> str:
    """Get a list of image URLs from Bing Search to run predictions against.

    Parameters
    ----------
    value: str
        The number of images to get

    Returns
    -------
    str
        List of image URLs to run the prediction against
    """
    client = _get_cognitive_services_client()

    volume_of_images = int(value)
    increment = volume_of_images if volume_of_images < 100 else 100
    image_urls = []
    offset = 0
    search_term = "dog OR cat"

    # search cognitive services until we have the volume of image URLs requested
    while len(image_urls) < volume_of_images:
        search_results = client.images.search(
            query=search_term, count=increment, offset=offset)
        image_urls.extend(
            [image.content_url for image in search_results.value])
        offset += increment
        increment = increment if offset + \
            increment < volume_of_images else volume_of_images - offset

    return json.dumps(image_urls)
