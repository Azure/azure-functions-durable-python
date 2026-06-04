from typing import Optional, Any, Dict, Tuple, List, Callable
from .utils.df_serialization import df_loads
import json


class DurableEntityContext:
    """Context of the durable entity context.

    Describes the API used to specify durable entity user code.
    """

    def __init__(self,
                 name: str,
                 key: str,
                 exists: bool,
                 state: Any):
        """Context of the durable entity context.

        Describes the API used to specify durable entity user code.

        Parameters
        ----------
        name: str
            The name of the Durable Entity
        key: str
            The key of the Durable Entity
        exists: bool
            Flag to determine if the entity exists
        state: Any
            The internal state of the Durable Entity
        """
        self._entity_name: str = name
        self._entity_key: str = key

        self._exists: bool = exists
        self._is_newly_constructed: bool = False

        self._state: Any = state
        self._state_is_raw: bool = False
        self._input: Any = None
        self._operation: Optional[str] = None
        self._result: Any = None

    @property
    def entity_name(self) -> str:
        """Get the name of the Entity.

        Returns
        -------
        str
            The name of the entity
        """
        return self._entity_name

    @property
    def entity_key(self) -> str:
        """Get the Entity key.

        Returns
        -------
        str
            The entity key
        """
        return self._entity_key

    @property
    def operation_name(self) -> Optional[str]:
        """Get the current operation name.

        Returns
        -------
        Optional[str]
            The current operation name
        """
        if self._operation is None:
            raise Exception("Entity operation is unassigned")
        return self._operation

    @property
    def is_newly_constructed(self) -> bool:
        """Determine if the Entity was newly constructed.

        Returns
        -------
        bool
            True if the Entity was newly constructed. False otherwise.
        """
        # This is not updated at the moment, as its semantics are unclear
        return self._is_newly_constructed

    @classmethod
    def from_json(cls, json_str: str) -> Tuple['DurableEntityContext', List[Dict[str, Any]]]:
        """Instantiate a DurableEntityContext from a JSON-formatted string.

        Parameters
        ----------
        json_string: str
            A JSON-formatted string, returned by the durable-extension,
            which represents the entity context

        Returns
        -------
        DurableEntityContext
            The DurableEntityContext originated from the input string
        """
        json_dict = json.loads(json_str)
        json_dict["name"] = json_dict["self"]["name"]
        json_dict["key"] = json_dict["self"]["key"]
        json_dict.pop("self")

        # Keep the raw serialized state (a JSON string) so get_state() can
        # deserialize lazily with an expected_type supplied by the user.
        serialized_state = json_dict["state"]

        batch = json_dict.pop("batch")
        ctx = cls(**json_dict)
        if serialized_state is not None:
            ctx._state_is_raw = True
        return ctx, batch

    def set_state(self, state: Any) -> None:
        """Set the state of the entity.

        Parameter
        ---------
        state: Any
            The new state of the entity
        """
        self._exists = True

        # should only serialize the state at the end of the batch
        self._state = state
        # The new state is a live Python value, not the raw JSON string
        # loaded from the payload. Clear the raw flag so a subsequent
        # get_state() in the same batch does not try to re-decode it.
        self._state_is_raw = False

    def get_state(self, initializer: Optional[Callable[[], Any]] = None,
                  expected_type: Optional[type] = None) -> Any:
        """Get the current state of this entity.

        Parameters
        ----------
        initializer: Optional[Callable[[], Any]]
            A 0-argument function to provide an initial state. Defaults to None.
        expected_type: Optional[type]
            The type to decode the state as. When set, the codec uses
            this type directly without consulting ``sys.modules``. Note that
            the persisted state is decoded lazily on the **first** get_state
            call within a batch; an ``expected_type`` supplied on a later
            call (after the state has already been decoded or replaced via
            set_state) has no effect.

        Returns
        -------
        Any
            The current state of the entity
        """
        if self._state is not None and self._state_is_raw:
            self._state = from_json_util(self._state, expected_type=expected_type)
            self._state_is_raw = False
        state = self._state
        if state is not None:
            return state
        elif initializer:
            if not callable(initializer):
                raise Exception("initializer argument needs to be a callable function")
            state = initializer()
        return state

    def get_input(self, expected_type: Optional[type] = None) -> Any:
        """Get the input for this operation.

        Parameters
        ----------
        expected_type: Optional[type]
            The type to decode the input as. When set, the codec uses
            this type directly without consulting ``sys.modules``.

        Returns
        -------
        Any
            The input for the current operation
        """
        input_ = None
        req_input = self._input
        req_input = json.loads(req_input)
        input_ = None if req_input is None else df_loads(req_input, expected_type=expected_type)
        return input_

    def set_result(self, result: Any) -> None:
        """Set the result (return value) of the entity.

        Paramaters
        ----------
        result: Any
            The result / return value for the entity
        """
        self._exists = True
        self._result = result

    def destruct_on_exit(self) -> None:
        """Delete this entity after the operation completes."""
        self._exists = False
        self._state = None
        self._state_is_raw = False


def from_json_util(json_str: str, expected_type: Optional[type] = None) -> Any:
    """Load an arbitrary datatype from its JSON representation.

    The Out-of-proc SDK has a special JSON encoding strategy
    to enable arbitrary datatypes to be serialized. This utility
    loads a JSON with the assumption that it follows that encoding
    method.

    Parameters
    ----------
    json_str: str
        A JSON-formatted string, from durable-extension
    expected_type: Optional[type]
        The type to decode the value as.

    Returns
    -------
    Any:
        The original datatype that was serialized
    """
    return df_loads(json_str, expected_type=expected_type)
