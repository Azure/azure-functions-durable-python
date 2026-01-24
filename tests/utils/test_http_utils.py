"""Tests for http_utils module to verify ClientSession reuse."""
import pytest
from unittest.mock import AsyncMock, patch, Mock
from azure.durable_functions.models.utils import http_utils


@pytest.mark.asyncio
async def test_session_is_reused_across_requests():
    """Test that the same session is reused for multiple requests."""
    # Reset the session to start fresh
    http_utils._client_session = None

    # Make first request to create session
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        # Create a proper async context manager
        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        mock_post_context.__aexit__.return_value = None
        mock_session.post.return_value = mock_post_context
        mock_session.closed = False
        mock_session_class.return_value = mock_session

        # First request
        await http_utils.post_async_request("http://test.com",
                                            {"data": "test1"})

        # Verify session was created once
        assert mock_session_class.call_count == 1
        first_session = http_utils._client_session

        # Second request - should reuse same session
        await http_utils.post_async_request("http://test.com",
                                            {"data": "test2"})

        # Verify session was NOT created again
        assert mock_session_class.call_count == 1
        assert http_utils._client_session is first_session


@pytest.mark.asyncio
async def test_session_recreated_after_close():
    """Test that a new session is created if the previous one was closed."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session1 = Mock()
        mock_session1.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        mock_post_context.__aexit__.return_value = None
        mock_session1.post.return_value = mock_post_context

        mock_session2 = Mock()
        mock_session2.closed = False
        mock_session2.post.return_value = mock_post_context

        mock_session_class.side_effect = [mock_session1, mock_session2]

        # First request creates session
        await http_utils.post_async_request("http://test.com",
                                            {"data": "test1"})
        assert mock_session_class.call_count == 1

        # Simulate session being closed
        mock_session1.closed = True

        # Second request should create new session
        await http_utils.post_async_request("http://test.com",
                                            {"data": "test2"})
        assert mock_session_class.call_count == 2


@pytest.mark.asyncio
async def test_session_closed_on_connection_error():
    """Test that session is closed and reset on connection errors."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session.closed = False
        mock_session.close = AsyncMock()

        # First request succeeds
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_post_context_success = AsyncMock()
        mock_post_context_success.__aenter__.return_value = mock_response
        mock_post_context_success.__aexit__.return_value = None

        mock_session.post.return_value = mock_post_context_success
        mock_session_class.return_value = mock_session

        await http_utils.post_async_request("http://test.com",
                                            {"data": "test1"})
        assert http_utils._client_session is not None

        # Second request raises connection error
        from aiohttp import ClientError
        mock_post_context_error = AsyncMock()
        mock_post_context_error.__aenter__.side_effect = \
            ClientError("Connection failed")
        mock_session.post.return_value = mock_post_context_error

        with pytest.raises(ClientError):
            await http_utils.post_async_request("http://test.com",
                                                {"data": "test2"})

        # Verify close was called
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_request_uses_shared_session():
    """Test that GET requests use the shared session."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "data"})

        mock_get_context = AsyncMock()
        mock_get_context.__aenter__.return_value = mock_response
        mock_get_context.__aexit__.return_value = None
        mock_session.get.return_value = mock_get_context
        mock_session_class.return_value = mock_session

        # Make GET request
        await http_utils.get_async_request("http://test.com")

        # Make another GET request
        await http_utils.get_async_request("http://test.com")

        # Verify session was created only once
        assert mock_session_class.call_count == 1


@pytest.mark.asyncio
async def test_delete_request_uses_shared_session():
    """Test that DELETE requests use the shared session."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "deleted"})

        mock_delete_context = AsyncMock()
        mock_delete_context.__aenter__.return_value = mock_response
        mock_delete_context.__aexit__.return_value = None
        mock_session.delete.return_value = mock_delete_context
        mock_session_class.return_value = mock_session

        # Make DELETE request
        await http_utils.delete_async_request("http://test.com")

        # Make another DELETE request
        await http_utils.delete_async_request("http://test.com")

        # Verify session was created only once
        assert mock_session_class.call_count == 1


@pytest.mark.asyncio
async def test_session_configured_with_timeouts():
    """Test that session is configured with appropriate timeouts."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class, \
            patch('aiohttp.ClientTimeout') as mock_timeout_class, \
            patch('aiohttp.TCPConnector') as mock_connector_class:

        mock_session = Mock()
        mock_session.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        mock_post_context.__aexit__.return_value = None
        mock_session.post.return_value = mock_post_context
        mock_session_class.return_value = mock_session

        await http_utils.post_async_request("http://test.com",
                                            {"data": "test"})

        # Verify timeout was configured for localhost IPC
        mock_timeout_class.assert_called_once()
        timeout_call = mock_timeout_class.call_args
        assert timeout_call.kwargs['total'] == 240
        assert timeout_call.kwargs['sock_connect'] == 10
        assert timeout_call.kwargs['sock_read'] is None

        # Verify connector was configured for localhost IPC
        mock_connector_class.assert_called_once()
        connector_call = mock_connector_class.call_args
        assert connector_call.kwargs['limit'] == 30
        assert connector_call.kwargs['limit_per_host'] == 30


@pytest.mark.asyncio
async def test_close_session():
    """Test the _close_session function."""
    # Reset and create a session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        mock_post_context.__aexit__.return_value = None
        mock_session.post.return_value = mock_post_context
        mock_session_class.return_value = mock_session

        # Create session
        await http_utils.post_async_request("http://test.com",
                                            {"data": "test"})
        assert http_utils._client_session is not None

        # Close session
        await http_utils._close_session()

        # Verify close was called and session is None
        mock_session.close.assert_called_once()
        assert http_utils._client_session is None


@pytest.mark.asyncio
async def test_trace_headers_are_passed():
    """Test that trace headers are properly passed in requests."""
    # Reset the session
    http_utils._client_session = None

    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        mock_post_context.__aexit__.return_value = None
        mock_session.post.return_value = mock_post_context
        mock_session_class.return_value = mock_session

        trace_parent = "00-trace-id-parent"
        trace_state = "state=value"

        await http_utils.post_async_request(
            "http://test.com",
            {"data": "test"},
            trace_parent=trace_parent,
            trace_state=trace_state
        )

        # Verify headers were passed
        call_args = mock_session.post.call_args
        assert call_args.kwargs['headers']['traceparent'] == trace_parent
        assert call_args.kwargs['headers']['tracestate'] == trace_state
