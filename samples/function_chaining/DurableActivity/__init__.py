import logging

def main(name: str) -> str:
    logging.warning(f"Activity Triggered: {name}")
    return f'Hello Activity: {name}!'