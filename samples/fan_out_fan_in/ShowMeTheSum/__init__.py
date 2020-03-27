import json

def main(theSum: int) -> str:
    """Activity function to raise an external event to the orchestrator

    Parameters
    ----------
    theSum: int
        The sum of numbers passed to each "ParrotValue" activity function

    Returns
    -------
    str
        A string indicating the sum
    """
    return f"Well that's nice {sum(json.loads(theSum))}"