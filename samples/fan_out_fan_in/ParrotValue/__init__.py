def main(value: str) -> str:
    """Activity function to validate that a number is within range

    Parameters
    ----------
    value: str
        A number value, expected to be lesser than 6

    Returns
    -------
    value: str
        The input value, assuming it was lesser than 6
    """
    int_value = int(value)
    if int_value >= 6:
      raise Exception('Bad Request')

    return value