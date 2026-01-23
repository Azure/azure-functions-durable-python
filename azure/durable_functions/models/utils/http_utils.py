from typing import Any, List, Union, Optional
import asyncio

import aiohttp


# Global session and lock for thread-safe initialization
_client_session: Optional[aiohttp.ClientSession] = None
_session_lock: asyncio.Lock = asyncio.Lock()


async def _get_session() -> aiohttp.ClientSession:
    """Get or create the shared ClientSession.

    Returns
    -------
    aiohttp.ClientSession
        The shared client session with configured timeout and connection pooling.
    """
    global _client_session

    # Double-check locking pattern for async
    if _client_session is None or _client_session.closed:
        async with _session_lock:
            # Check again after acquiring lock
            if _client_session is None or _client_session.closed:
                # Configure timeout and connection pooling
                timeout = aiohttp.ClientTimeout(
                    total=60,  # Total timeout for entire request
                    connect=30,  # Timeout for connection establishment
                    sock_connect=30,  # Socket connection timeout
                    sock_read=30  # Socket read timeout
                )

                # Configure TCP connector with connection pooling
                connector = aiohttp.TCPConnector(
                    limit=100,  # Maximum number of connections
                    limit_per_host=30,  # Maximum connections per host
                    ttl_dns_cache=300,  # DNS cache TTL in seconds
                    enable_cleanup_closed=True  # Enable cleanup of closed connections
                )

                _client_session = aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                )

    return _client_session


async def _close_session() -> None:
    """Close the shared ClientSession if it exists.

    This function should be called during worker shutdown.
    """
    global _client_session

    if _client_session is not None and not _client_session.closed:
        await _client_session.close()
        _client_session = None


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
    session = await _get_session()
    headers = {}
    if trace_parent:
        headers["traceparent"] = trace_parent
    if trace_state:
        headers["tracestate"] = trace_state

    try:
        async with session.post(url, json=data, headers=headers) as response:
            # We disable aiohttp's input type validation
            # as the server may respond with alternative
            # data encodings. This is potentially unsafe.
            # More here: https://docs.aiohttp.org/en/stable/client_advanced.html
            data = await response.json(content_type=None)
            return [response.status, data]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        # On connection errors, close and recreate session for next request
        # This handles cases where the remote host process recycles
        global _client_session
        if _client_session is not None and not _client_session.closed:
            await _client_session.close()
            _client_session = None
        raise


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
    session = await _get_session()

    try:
        async with session.get(url) as response:
            data = await response.json(content_type=None)
            if data is None:
                data = ""
            return [response.status, data]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        # On connection errors, close and recreate session for next request
        # This handles cases where the remote host process recycles
        global _client_session
        if _client_session is not None and not _client_session.closed:
            await _client_session.close()
            _client_session = None
        raise


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
    session = await _get_session()

    try:
        async with session.delete(url) as response:
            data = await response.json(content_type=None)
            return [response.status, data]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        # On connection errors, close and recreate session for next request
        # This handles cases where the remote host process recycles
        global _client_session
        if _client_session is not None and not _client_session.closed:
            await _client_session.close()
            _client_session = None
        raise
