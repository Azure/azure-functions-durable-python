import os
from os.path import dirname
from typing import List

def main(rootDirectory: str) -> List[str]:

    all_file_paths = []
    # We walk the file system
    for path, _, files in os.walk(rootDirectory):
        # We copy the code for activities and orchestrators
        if "E2_" in path:
            # For each file, we add their full-path to the list
            for name in files:
                if name == "__init__.py" or name == "function.json":
                    file_path = os.path.join(path, name)
                    all_file_paths.append(file_path)
    
    return all_file_paths
