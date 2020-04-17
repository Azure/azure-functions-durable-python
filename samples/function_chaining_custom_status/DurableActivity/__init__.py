import logging

def main(name: str) -> str:
    """Activity function performing a specific step in the chain
    
    Parameters
    ----------
    name : str
        key to a dictionary that advances the chain
    
    Returns
    -------
    [int]
        value in the dictionary as a result
    """

    logging.warning(f"Activity Triggered: {name}")
    switch_statement = {}
    switch_statement["One"] = "Two"
    switch_statement["Two"] = "Three"
    try:
        if switch_statement[name]:
            return f'{switch_statement[name]}'
    except KeyError as e:
        return f'One'

    
