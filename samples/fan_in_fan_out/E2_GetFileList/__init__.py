import os
from typing import List

def main(rootDirectory: str) -> List[str]:

    all_file_paths = []
    # We walk the file system, looking for all files
    # below "rootDirectory"
    for path, _, files in os.walk(rootDirectory):
        # For each file, we add their full-path to the list
        for name in files:
            file_path = os.path.join(path, name)
            all_file_paths.append(file_path)
    return all_file_paths
