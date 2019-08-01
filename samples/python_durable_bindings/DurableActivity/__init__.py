import logging

def main(name: str) -> str:
    logging.warn(f"Activity Triggered: {name}")
    return f'Hello Activity: {name}!'