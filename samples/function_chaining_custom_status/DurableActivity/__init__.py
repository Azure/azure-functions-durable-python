import logging

def main(key: str) -> str:
    """Activity function performing a specific step in the chain
    
    Parameters
    ----------
    key : str
        key to a dictionary that advances the chain
    
    Returns
    -------
    [int]
        value in the dictionary as a result
    """

    logging.warning(f"Activity Triggered: {key}")
    switch_statement = {}
    switch_statement["One"] = "Two"
    switch_statement["Two"] = "Three"
    try:
        if switch_statement[key]:
            return f'{switch_statement[key]}'
    except KeyError as e:
        return f'One'

    
