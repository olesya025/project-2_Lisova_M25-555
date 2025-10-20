from typing import Any, Dict, List, Optional, Tuple

from prettytable import PrettyTable

from src.primitive_db.constants import (
    ERROR_COLUMN_DEFINITION,
    ERROR_TABLE_NOT_FOUND,
    ERROR_UNSUPPORTED_TYPE,
    SUPPORTED_TYPES,
)
from src.primitive_db.decorators import confirm_action, handle_db_errors, log_time
from src.primitive_db.utils import load_table_data, save_metadata, save_table_data


@handle_db_errors
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
        raise ValueError(ERROR_COLUMN_DEFINITION.format(column_def))

    name, col_type = column_def.split(":", 1)
    name = name.strip()
    col_type = col_type.strip().lower()

    if not name:
        raise ValueError(ERROR_COLUMN_DEFINITION.format(column_def))

    if col_type not in SUPPORTED_TYPES:
        supported = ", ".join(SUPPORTED_TYPES)
        raise ValueError(ERROR_UNSUPPORTED_TYPE.format(col_type, supported))

    return name, col_type

@handle_db_errors
def create_table(
    metadata: Dict[str, Any],
    table_name: str,
    columns: List[str]
) -> bool:
    """
    Create new table in metadata.

    Args:
        metadata: Current database metadata
        table_name: Table name
        columns: List of column definitions

    Returns:
        True if successful, False otherwise
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
    }

    # Сохраняем метаданные и возвращаем результат
    result = save_metadata(metadata)
    print(f"DEBUG create_table: save_metadata returned {result}, type: {type(result)}")
    return result

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: Dict[str, Any], table_name: str) -> bool:
    """
    Delete table from metadata.

    Args:
        metadata: Current database metadata
        table_name: Table name to delete

    Returns:
        True if successful, False otherwise
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    del metadata[table_name]
    return save_metadata(metadata)

@handle_db_errors
def list_tables(metadata: Dict[str, Any]) -> List[str]:
    """
    Get list of all tables.

    Args:
        metadata: Database metadata

    Returns:
        List of table names
    """
    return list(metadata.keys())

@handle_db_errors
def get_table_columns(metadata: Dict[str, Any], table_name: str) -> List[str]:
    """
    Get table columns list.

    Args:
        metadata: Database metadata
        table_name: Table name

    Returns:
        List of columns in "name:type" format
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    return metadata[table_name]["columns"]

@handle_db_errors
def get_column_types(metadata: Dict[str, Any], table_name: str) -> Dict[str, str]:
    """
    Get column types mapping.

    Args:
        metadata: Database metadata
        table_name: Table name

    Returns:
        Dictionary mapping column names to types
    """
    columns = get_table_columns(metadata, table_name)
    types = {}
    for col_def in columns:
        name, col_type = col_def.split(":")
        types[name] = col_type
    return types

@handle_db_errors
def validate_value_type(value: Any, expected_type: str) -> Any:
    """
    Validate and convert value to expected type.

    Args:
        value: Input value
        expected_type: Expected type name

    Returns:
        Converted value

    Raises:
        ValueError: If value cannot be converted to expected type
    """
    if expected_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Value '{value}' cannot be converted to int")
    elif expected_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ["true", "1", "yes"]:
                return True
            elif value.lower() in ["false", "0", "no"]:
                return False
        raise ValueError(f"Value '{value}' cannot be converted to bool")
    elif expected_type == "str":
        return str(value)
    else:
        raise ValueError(f"Unsupported type: {expected_type}")

@handle_db_errors
@log_time
def insert(
    metadata: Dict[str, Any],
    table_name: str,
    values: List[Any]
) -> bool:
    """
    Insert new record into table.

    Args:
        metadata: Database metadata
        table_name: Table name
        values: List of values for columns (excluding ID)

    Returns:
        True if successful, False otherwise
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    column_types = get_column_types(metadata, table_name)
    user_columns = [col for col in column_types.keys() if col != "ID"]

    if len(values) != len(user_columns):
        expected = len(user_columns)
        raise ValueError(f"Expected {expected} values, got {len(values)}")

    # Load existing data
    table_data = load_table_data(table_name)

    # Generate new ID
    new_id = 1
    if table_data:
        new_id = max(record.get("ID", 0) for record in table_data) + 1

    # Create new record
    new_record = {"ID": new_id}

    # Validate and add user values
    for i, column in enumerate(user_columns):
        expected_type = column_types[column]
        try:
            validated_value = validate_value_type(values[i], expected_type)
            new_record[column] = validated_value
        except ValueError as e:
            raise ValueError(f"Column '{column}': {e}")

    # Add record and save
    table_data.append(new_record)
    return save_table_data(table_name, table_data)

@handle_db_errors
@log_time
def select(
    metadata: Dict[str, Any],
    table_name: str,
    where_clause: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Select records from table.

    Args:
        metadata: Database metadata
        table_name: Table name
        where_clause: Optional filter conditions

    Returns:
        Filtered records
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    table_data = load_table_data(table_name)

    if where_clause is None:
        return table_data

    filtered_data = []
    for record in table_data:
        match = True
        for column, condition in where_clause.items():
            if column not in record:
                match = False
                break
                
            # Проверяем, является ли условие простым сравнением или сложным с оператором
            if isinstance(condition, dict) and "operator" in condition:
                # Обрабатываем операторы сравнения
                operator = condition["operator"]
                expected_value = condition["value"]
                actual_value = record[column]
                
                if operator == ">":
                    if not (actual_value > expected_value):
                        match = False
                        break
                elif operator == "<":
                    if not (actual_value < expected_value):
                        match = False
                        break
                elif operator == ">=":
                    if not (actual_value >= expected_value):
                        match = False
                        break
                elif operator == "<=":
                    if not (actual_value <= expected_value):
                        match = False
                        break
                elif operator == "!=":
                    if not (actual_value != expected_value):
                        match = False
                        break
            else:
                # Простое сравнение на равенство
                if record[column] != condition:
                    match = False
                    break
                    
        if match:
            filtered_data.append(record)

    return filtered_data

@handle_db_errors
def update(
    metadata: Dict[str, Any],
    table_name: str,
    set_clause: Dict[str, Any],
    where_clause: Dict[str, Any]
) -> bool:
    """
    Update records in table.

    Args:
        metadata: Database metadata
        table_name: Table name
        set_clause: Columns and values to update
        where_clause: Filter conditions

    Returns:
        True if successful, False otherwise
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    table_data = load_table_data(table_name)
    updated = False

    for record in table_data:
        match = True
        for column, expected_value in where_clause.items():
            if column not in record or record[column] != expected_value:
                match = False
                break
        if match:
            for column, new_value in set_clause.items():
                if column in record and column != "ID":  # Don't allow updating ID
                    record[column] = new_value
            updated = True

    if not updated:
        raise ValueError("No records match the WHERE condition")

    return save_table_data(table_name, table_data)

@handle_db_errors
@confirm_action("удаление записей")
def delete(
    metadata: Dict[str, Any],
    table_name: str,
    where_clause: Dict[str, Any]
) -> bool:
    """
    Delete records from table.

    Args:
        metadata: Database metadata
        table_name: Table name
        where_clause: Filter conditions

    Returns:
        True if successful, False otherwise
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    table_data = load_table_data(table_name)
    new_data = []
    deleted_count = 0

    for record in table_data:
        match = True
        for column, expected_value in where_clause.items():
            if column not in record or record[column] != expected_value:
                match = False
                break
        if not match:
            new_data.append(record)
        else:
            deleted_count += 1

    if deleted_count == 0:
        raise ValueError("No records match the WHERE condition")

    return save_table_data(table_name, new_data)

@handle_db_errors
def format_table_output(columns: List[str], data: List[Dict[str, Any]]) -> str:
    """
    Format table data as pretty table.

    Args:
        columns: List of column names
        data: Table records

    Returns:
        Formatted table string
    """
    if not data:
        return "No records found"

    table = PrettyTable()
    table.field_names = columns

    for record in data:
        row = []
        for column in columns:
            row.append(record.get(column, ""))
        table.add_row(row)

    return str(table)

@handle_db_errors
def get_table_info(
    metadata: Dict[str, Any],
    table_name: str
) -> str:
    """
    Get table information.

    Args:
        metadata: Database metadata
        table_name: Table name

    Returns:
        Formatted table info
    """
    if table_name not in metadata:
        raise ValueError(ERROR_TABLE_NOT_FOUND.format(table_name))

    table_data = load_table_data(table_name)
    columns = get_table_columns(metadata, table_name)
    columns_str = ", ".join(columns)
    record_count = len(table_data)

    info = f"Таблица: {table_name}\n"
    info += f"Столбцы: {columns_str}\n"
    info += f"Количество записей: {record_count}"

    return info