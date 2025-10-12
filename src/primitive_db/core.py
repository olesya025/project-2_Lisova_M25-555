from typing import Any, Dict, List, Tuple


SUPPORTED_TYPES = {"int", "str", "bool"}


def validate_column_definition(column_def: str) -> Tuple[str, str]:
    """
    Validate column definition.

    Args:
        column_def: String in "name:type" format

    Returns:
        Tuple of (column_name, type)

    Raises:
        ValueError: If definition is invalid
    """
    if ":" not in column_def:
        raise ValueError(f"Invalid column definition: {column_def}")

    name, col_type = column_def.split(":", 1)
    name = name.strip()
    col_type = col_type.strip().lower()

    if not name:
        raise ValueError(f"Column name cannot be empty: {column_def}")

    if col_type not in SUPPORTED_TYPES:
        supported = ", ".join(SUPPORTED_TYPES)
        msg = f"Unsupported type: {col_type}. Supported: {supported}"
        raise ValueError(msg)

    return name, col_type


def create_table(
    metadata: Dict[str, Any], table_name: str, columns: List[str]
) -> Dict[str, Any]:
    """
    Create new table in metadata.

    Args:
        metadata: Current database metadata
        table_name: Table name
        columns: List of column definitions

    Returns:
        Updated metadata

    Raises:
        ValueError: If table already exists or column definitions are invalid
    """
    if table_name in metadata:
        raise ValueError(f'Table "{table_name}" already exists.')

    # Add automatic ID column
    table_columns = ["ID:int"]

    # Process user columns
    for column_def in columns:
        name, col_type = validate_column_definition(column_def)
        table_columns.append(f"{name}:{col_type}")

    # Save table structure
    metadata[table_name] = {
        "columns": table_columns,
        "data": [],  # For future data
    }

    return metadata


def drop_table(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Delete table from metadata.

    Args:
        metadata: Current database metadata
        table_name: Table name to delete

    Returns:
        Updated metadata

    Raises:
        ValueError: If table doesn't exist
    """
    if table_name not in metadata:
        raise ValueError(f'Table "{table_name}" doesn\'t exist.')

    del metadata[table_name]
    return metadata


def list_tables(metadata: Dict[str, Any]) -> List[str]:
    """
    Get list of all tables.

    Args:
        metadata: Database metadata

    Returns:
        List of table names
    """
    return list(metadata.keys())


def get_table_columns(metadata: Dict[str, Any], table_name: str) -> List[str]:
    """
    Get table columns list.

    Args:
        metadata: Database metadata
        table_name: Table name

    Returns:
        List of columns in "name:type" format

    Raises:
        ValueError: If table doesn't exist
    """
    if table_name not in metadata:
        raise ValueError(f'Table "{table_name}" doesn\'t exist.')

    return metadata[table_name]["columns"]