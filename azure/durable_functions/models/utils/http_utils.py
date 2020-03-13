from typing import Any

import aiohttp


async def post_async_request(url: str, data: Any = None) -> [int, Any]:
    """Post request with the data provided to the url provided.

    Parameters
    ----------
    url: str
        url to make the post to
    data: Any
        object to post

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                json=data) as response:
            data = await response.json()
            return [response.status, data]


async def get_async_request(url: str) -> [int, Any]:
    """Get the data from the url provided.

    Parameters
    ----------
    url: str
        url to get the data from

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return [response.status, data]


async def delete_async_request(url: str) -> [int, Any]:
    """Delete the data from the url provided.

    Parameters
    ----------
    url: str
        url to delete the data from

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as response:
            data = await response.json()
            return [response.status, data]
