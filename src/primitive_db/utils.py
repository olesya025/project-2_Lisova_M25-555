import json
from typing import Any, Dict


def load_metadata(filepath: str = "db_meta.json") -> Dict[str, Any]:
    """
    Load metadata from JSON file.

    Args:
        filepath: Path to metadata file

    Returns:
        Dictionary with metadata or empty dict if file not found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(data: Dict[str, Any], filepath: str = "db_meta.json") -> None:
    """
    Save metadata to JSON file.

    Args:
        data: Dictionary with metadata to save
        filepath: Path to save file
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)