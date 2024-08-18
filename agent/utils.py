from pathlib import Path
from typing import List, Union


def get_ext(path: Union[str, Path]) -> str:
    return Path(path).suffix


def get_path_from_root(path: Union[str, Path]) -> Path:
    base_path = Path(__file__).resolve().parent
    full_path = base_path / path
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def get_files_recursive(path: Union[str, Path]) -> List[Path]:
    path = Path(path)
    if path.is_file():
        return [path]
    return [file for file in path.rglob('*') if file.is_file()]
