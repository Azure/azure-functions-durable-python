import logging

def main(num: int) -> int:
    """Activity function performing a specific step in the chain
    
    Parameters
    ----------
    num : int
        number whose value to increase by one
    
    Returns
    -------
    int
        the input, plus one
    """

    logging.info(f"Activity Triggered: {num}")
    return num + 1

    
