import json
import os
from typing import List
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


def main(volume: int) -> List[str]:
    """Get a list of image URLs from Bing Search to run predictions against.

    Parameters
    ----------
    volume: int
        The number of images to get

    Returns
    -------
    List[str]
        List of image URLs to run the prediction against
    """
    client = _get_cognitive_services_client()

    increment = volume if volume < 100 else 100
    image_urls = []
    offset = 0
    search_term = "dog OR cat"

    # search cognitive services until we have the volume of image URLs requested
    while len(image_urls) < volume:
        search_results = client.images.search(
            query=search_term, count=increment, offset=offset)
        image_urls.extend(
            [image.content_url for image in search_results.value])
        offset += increment
        increment = increment if offset + \
            increment < volume else volume - offset

    return image_urls
