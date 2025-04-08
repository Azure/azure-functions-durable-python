from typing import Any, List, Union

import aiohttp


async def post_async_request(url: str,
                             data: Any = None,
                             trace_parent: str = None,
                             trace_state: str = None) -> List[Union[int, Any]]:
    """Post request with the data provided to the url provided.

    Parameters
    ----------
    url: str
        url to make the post to
    data: Any
        object to post
    trace_parent: str
        traceparent header to send with the request
    trace_state: str
        tracestate header to send with the request

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with aiohttp.ClientSession() as session:
        headers = {}
        if trace_parent:
            headers["traceparent"] = trace_parent
        if trace_state:
            headers["tracestate"] = trace_state
        async with session.post(url, json=data, headers=headers) as response:
            # We disable aiohttp's input type validation
            # as the server may respond with alternative
            # data encodings. This is potentially unsafe.
            # More here: https://docs.aiohttp.org/en/stable/client_advanced.html
            data = await response.json(content_type=None)
            return [response.status, data]


async def get_async_request(url: str) -> List[Any]:
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
            data = await response.json(content_type=None)
            if data is None:
                data = ""
            return [response.status, data]


async def delete_async_request(url: str) -> List[Union[int, Any]]:
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
            data = await response.json(content_type=None)
            return [response.status, data]
