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


# When we recieve properties from WebJobs extension originally parsed as
#   TimeSpan objects through Newtonsoft, the format complies with the constant
#   format specifier for TimeSpan in .NET.
#   Python offers no convenient way to parse these back into timedeltas,
#   so we use this regex method instead
def parse_timespan_attrib(from_str: str) -> datetime.timedelta:
    """Convert a string representing TimeSpan.ToString("c") in .NET to a python timedelta.

    Parameters
    ----------
    from_str: The string format of the TimeSpan to convert

    Returns
    -------
    timespan.timedelta
        The TimeSpan expressed as a Python datetime.timedelta

    """
    match = re.match(r"^(?P<negative>-)?(?:(?P<days>[0-9]*)\.)?"
                     r"(?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2})"
                     r":(?P<seconds>[0-9]{2})(?:\.(?P<ticks>[0-9]{7}))?$",
                     from_str)
    if match:
        groups = match.groupdict()
        span = datetime.timedelta(
            days=int(groups['days'] or "0"),
            hours=int(groups['hours']),
            minutes=int(groups['minutes']),
            seconds=int(groups['seconds']),
            microseconds=int(groups['ticks'] or "0") // 10)

        if groups['negative'] == '-':
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
