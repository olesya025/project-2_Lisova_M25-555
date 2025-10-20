import json
import os
from typing import Any, Dict, List

from src.primitive_db.constants import DATA_DIR, META_FILE
from src.primitive_db.decorators import handle_db_errors


@handle_db_errors
def load_metadata(filepath: str = META_FILE) -> Dict[str, Any]:
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

@handle_db_errors
def save_metadata(data: Dict[str, Any], filepath: str = META_FILE) -> bool:
    """
    Save metadata to JSON file.

    Args:
        data: Dictionary with metadata to save
        filepath: Path to save file

    Returns:
        True if successful
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return True

def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def get_table_data_path(table_name: str) -> str:
    """
    Get path for table data file.

    Args:
        table_name: Name of the table

    Returns:
        Path to table data file
    """
    return f"{DATA_DIR}/{table_name}.json"

@handle_db_errors
def load_table_data(table_name: str) -> List[Dict[str, Any]]:
    """
    Load table data from JSON file.

    Args:
        table_name: Name of the table

    Returns:
        List of table records or empty list if file not found
    """
    ensure_data_dir()
    filepath = get_table_data_path(table_name)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@handle_db_errors
def save_table_data(table_name: str, data: List[Dict[str, Any]]) -> bool:
    """
    Save table data to JSON file.

    Args:
        table_name: Name of the table
        data: List of records to save

    Returns:
        True if successful
    """
    ensure_data_dir()
    filepath = get_table_data_path(table_name)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return True