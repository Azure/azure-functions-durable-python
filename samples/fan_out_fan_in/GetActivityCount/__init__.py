import json

def main(value: int) -> str:
    """Activity function to generate a range of numbers

    Parameters
    ----------
    value: str
        The exclusive upper-bound of the generated range of numbers

    Returns
    -------
    str
        A JSON-formatted string representing the range of values:
        [0-(value -1)]
    """
    activity_values = list(range(value))
    return activity_values
