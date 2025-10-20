# src/primitive_db/parser.py

from typing import Any, Dict


def parse_where_condition(condition: str) -> Dict[str, Any]:
    """
    Парсит условие WHERE в пару столбец-значение.

    Args:
        condition: Строка в формате "column = value" или "column > value" и т.д.

    Returns:
        Словарь с именем столбца и разобранным значением

    Raises:
        ValueError: Если формат условия неверный
    """
    # Поддерживаемые операторы сравнения 
    # (в порядке убывания длины для правильного парсинга)
    operators = [">=", "<=", "!=", ">", "<", "="]
    
    # Находим оператор в условии
    operator = None
    for op in operators:
        if op in condition:
            operator = op
            break
    
    if operator is None:
        error_msg = (
            f"Неверный формат условия WHERE: {condition}. "
            f"Поддерживаемые операторы: {', '.join(operators)}"
        )
        raise ValueError(error_msg)

    parts = condition.split(operator, 1)
    if len(parts) != 2:
        raise ValueError(f"Неверный формат условия WHERE: {condition}")

    column = parts[0].strip()
    value_str = parts[1].strip()

    # Парсим значение на основе кавычек и типа
    value = parse_value(value_str)

    # Для операторов сравнения возвращаем специальную структуру
    if operator != "=":
        return {column: {"operator": operator, "value": value}}
    else:
        return {column: value}

def parse_set_clause(clause: str) -> Dict[str, Any]:
    """
    Парсит SET clause в пары столбец-значение.

    Args:
        clause: Строка в формате "column1 = value1, column2 = value2"

    Returns:
        Словарь с именами столбцов и разобранными значениями

    Raises:
        ValueError: Если формат clause неверный
    """
    result = {}
    assignments = clause.split(",")

    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError(f"Неверный формат SET присваивания: {assignment}")

        parts = assignment.split("=", 1)
        if len(parts) != 2:
            raise ValueError(f"Неверный формат SET присваивания: {assignment}")

        column = parts[0].strip()
        value_str = parts[1].strip()

        # Парсим значение на основе кавычек и типа
        value = parse_value(value_str)
        result[column] = value

    return result

def parse_value(value_str: str) -> Any:
    """
    Парсит строковое значение в соответствующий тип Python.

    Args:
        value_str: Строковое представление значения

    Returns:
        Разобранное значение с соответствующим типом
    """
    value_str = value_str.strip()

    # Проверяем строки в кавычках
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # Проверяем булевые значения
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False

    # Проверяем целые числа
    try:
        return int(value_str)
    except ValueError:
        pass

    # Возвращаем как строку, если другие типы не подошли
    return value_str

def parse_insert_values(values_str: str) -> list:
    """
    Парсит VALUES clause для команды INSERT.

    Args:
        values_str: Строка в формате "(value1, value2, ...)"

    Returns:
        Список разобранных значений

    Raises:
        ValueError: Если формат неверный
    """
    if not values_str.startswith("(") or not values_str.endswith(")"):
        raise ValueError("VALUES должны быть заключены в круглые скобки")

    # Убираем скобки и разделяем по запятым
    content = values_str[1:-1].strip()
    if not content:
        return []

    # Простое разделение по запятым (наивный метод, но работает для базовых случаев)
    parts = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in content:
        if char in ['"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            current += char
        elif char == ',' and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        parts.append(current.strip())

    # Парсим каждое значение
    return [parse_value(part) for part in parts]