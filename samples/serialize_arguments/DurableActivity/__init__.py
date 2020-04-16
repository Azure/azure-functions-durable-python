import logging

def main(name: str) -> str:
    """Activity function performing a specific step in the chain
    
    Parameters
    ----------
    name : str
        Name of the item to be hello'ed at 
    
    Returns
    -------
    str
        Returns a welcome string
    """
    logging.warning(f"Activity Triggered: {name}")
    return f'Hello Activity: {name}!'

    