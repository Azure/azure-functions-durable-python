import typing
import json

class SerializableClass(object):
    """ Example serializable class.

    For a custom class to be serializable in
    Python Durable Functions, we require that
    it include both `to_json` and `from_json`
    a `@staticmethod`s for serializing to JSON
    and back respectively. These get called
    internally by the framework.
    """
    def __init__(self, number: int):
        """ Construct the class
        Parameters
        ----------
        number: int
            A number to encapsulate
        """
        self.number = number

    def show_number(self) -> int:
        """" Returns the number value"""
        return self.number

    @staticmethod
    def to_json(obj: object) -> str:
        """ Serializes a `SerializableClass` instance
        to a JSON string.

        Parameters
        ----------
        obj: SerializableClass
            The object to serialize

        Returns
        -------
        json_str: str
            A JSON-encoding of `obj`
        """
        return str(obj.number)

    @staticmethod
    def from_json(json_str: str) -> object:
        """ De-serializes a JSON string to a
        `SerializableClass` instance. It assumes
        that the JSON string was generated via
        `SerializableClass.to_json`

        Parameters
        ----------
        json_str: str
            The JSON-encoding of a `SerializableClass` instance
        
        Returns
        --------
        obj: SerializableClass
            A SerializableClass instance, de-serialized from `json_str`
        """
        number = int(json_str)
        obj = SerializableClass(number)
        return obj
