import os
from pathlib import Path


def get_ext(path):
    return os.path.splitext(path)[1]


def get_path_from_root(path):
    base_path = Path(__file__).resolve().parent
    full_path = base_path / path

    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)

    return str(full_path)


def get_files_recursive(path):
    file_paths = []
    if os.path.isfile(path):
        file_paths.append(path)
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                file_paths.append(full_path)
    return file_paths
