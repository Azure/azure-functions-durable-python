from typing import Dict, Any

from azure.durable_functions.models import TokenSource
from azure.durable_functions.models.utils.json_utils import add_attrib, add_json_attrib


class DurableHttpRequest:
    """Data structure representing a durable HTTP request."""

    def __init__(self, method: str, uri: str, content: str = None, headers: Dict[str, str] = None,
                 token_source: TokenSource = None):
        self._method: str = method
        self._uri: str = uri
        self._content: str = content
        self._headers: Dict[str, str] = headers
        self._token_source: TokenSource = token_source

    @property
    def method(self) -> str:
        """Get the HTTP request method."""
        return self._method

    @property
    def uri(self) -> str:
        """Get the HTTP request uri."""
        return self._uri

    @property
    def content(self) -> str:
        """Get the HTTP request content."""
        return self._content

    @property
    def headers(self) -> Dict[str, str]:
        """Get the HTTP request headers."""
        return self._headers

    @property
    def token_source(self) -> TokenSource:
        """Get the source of OAuth token to add to the request."""
        return self._token_source

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'method')
        add_attrib(json_dict, self, 'uri')
        add_attrib(json_dict, self, 'content')
        add_attrib(json_dict, self, 'headers')
        add_json_attrib(json_dict, self, 'token_source', 'tokenSource')
        return json_dict
