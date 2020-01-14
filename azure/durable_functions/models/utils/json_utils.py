from typing import Dict, Any


def add_attrib(json_dict: Dict[str, Any], object_, attribute_name: str, alt_name: str = None):
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = getattr(object_, attribute_name)


def add_json_attrib(json_dict: Dict[str, Any], object_, attribute_name: str, alt_name: str = None):
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = getattr(object_, attribute_name).to_json()