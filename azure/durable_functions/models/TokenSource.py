from abc import ABC
from typing import Dict, Any

from azure.durable_functions.models.utils.json_utils import add_attrib


class TokenSource(ABC):
    """Token Source implementation for [Azure Managed Identities].

    https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview.

    @example Get a list of Azure Subscriptions by calling the Azure Resource Manager HTTP API.
     ```python
    import azure.durable_functions as df

    def generator_function(context):
        return yield context.callHttp(
            "GET",
            "https://management.azure.com/subscriptions?api-version=2019-06-01",
            None,
            None,
            df.ManagedIdentityTokenSource("https://management.core.windows.net"))
    """

    def __init__(self):
        super().__init__()


class ManagedIdentityTokenSource(TokenSource):
    """Returns a `ManagedIdentityTokenSource` object."""

    def __init__(self, resource: str):
        super().__init__()
        self._resource: str = resource

    @property
    def resource(self) -> str:
        """Get the Azure Active Directory resource identifier of the web API being invoked.

        For example, `https://management.core.windows.net/` or `https://graph.microsoft.com/`.
        """
        return self._resource

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict = {}
        add_attrib(json_dict, self, 'resource')
        return json_dict
