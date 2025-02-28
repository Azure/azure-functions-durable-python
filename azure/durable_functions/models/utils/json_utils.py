import datetime
import re
from typing import Dict, Any

from ...constants import DATETIME_STRING_FORMAT


def add_attrib(json_dict: Dict[str, Any], object_,
               attribute_name: str, alt_name: str = None):
    """Add the value of the attribute from the object to the dictionary.

    Used to dynamically add the value of the attribute if the value is present.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = \
            getattr(object_, attribute_name)


def add_datetime_attrib(json_dict: Dict[str, Any], object_,
                        attribute_name: str, alt_name: str = None):
    """Add the value of the attribute from the object to the dictionary converted into a string.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = \
            getattr(object_, attribute_name).strftime(DATETIME_STRING_FORMAT)

# When we recieve properties from WebJobs extension originally parsed as TimeSpan objects through Newtonsoft, 
#   the format complies with the constant format specifier for TimeSpan in .NET. 
#   See https://learn.microsoft.com/en-us/dotnet/standard/base-types/standard-timespan-format-strings#the-constant-c-format-specifier
#   Python offers no convenient way to parse these back into timedeltas, so we use this regex method instead
def parse_datetime_attrib_timespan(from_str: str) -> datetime.timedelta:
    """Converts a string originally produced by TimeSpan.ToString("c") in .NET into python's timespan.timedelta

    Parameters
    ----------
    from_str: The string format of the TimeSpan to convert

    Returns
    -------
    timespan.timedelta
        The TimeSpan expressed as a Python datetime.timedelta

    """
    match = re.match(r"^(-)?(?:([0-9]*)\.)?([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{7}))?$", from_str)
    if match:
        span = datetime.timedelta(days=int(match.group(2) or "0"), hours=int(match.group(3)), minutes=int(match.group(4)), seconds=int(match.group(5)), microseconds=int(match.group(6) or "0") // 10)
        if match.group(1):
            span = -span
        return span
    else:
        raise Exception(f"Format of TimeSpan failed attempted conversion to timedelta: {from_str}")


def add_json_attrib(json_dict: Dict[str, Any], object_,
                    attribute_name: str, alt_name: str = None):
    """Add the results of the to_json() function call of the attribute from the object to the dict.

    Used to dynamically add the JSON converted value of the attribute if the value is present.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        attribute_value = getattr(object_, attribute_name)
        if attribute_value:
            json_dict[alt_name or attribute_name] = attribute_value.to_json()
