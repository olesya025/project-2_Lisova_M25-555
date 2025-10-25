import shlex
from typing import List

from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    format_table_output,
    get_column_types,
    get_table_info,
    insert,
    list_tables,
    select,
    update,
)
from src.primitive_db.decorators import create_cacher
from src.primitive_db.parser import (
    parse_insert_values,
    parse_set_clause,
    parse_where_condition,
)
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
)

# Добавим глобальную переменную для кэшера
cacher = create_cacher()

# Добавим функцию для очистки кэша
def clear_cache():
    """Очищает кэш запросов."""
    global cacher
    cacher = create_cacher()  # Создаем новый кэшер


def print_help():
    """Выводит справочную информацию для режима работы с таблицами."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ..")
    print(" - создать таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...)")
    print(" - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение>")
    print(" - прочитать записи по условию")
    print("<command> select from <имя_таблицы>")
    print(" - прочитать все записи")
    print("<command> update <table> set <col>=<val> where <col>=<val>")
    print(" - обновить запись")
    print("<command> delete from <table> where <condition>")
    print(" - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_welcome():
    """Выводит приветственное сообщение."""
    print("***Операции с данными***")
    print("Функции:")
    print("<command> insert into <table> values (<value1>, ...)")
    print(" - создать запись")
    print("<command> select from <table> where <column> = <value>")
    print(" - прочитать записи по условию")
    print("<command> select from <table> - прочитать все записи")
    print("<command> update <table> set <col>=<val> where <col>=<val>")
    print(" - обновить запись")
    print("<command> delete from <table> where <condition>")
    print(" - удалить запись")
    print("<command> info <table> - вывести информацию о таблице")
    print("<command> create_table <table> <col1:type> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <table> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def handle_create_table(args: List[str]) -> bool:
    """
    Обрабатывает команду создания таблицы.

    Args:
        args: Аргументы команды

    Returns:
        True если нужно сохранить метаданные, иначе False
    """
    if len(args) < 2:
        msg = "Ошибка: Недостаточно аргументов. "
        msg += "Используйте: create_table <имя_таблицы> <столбец1:тип> ..."
        print(msg)
        return False

    table_name = args[0]
    columns = args[1:]
    
    try:
        metadata = load_metadata()
        
        # ВАЖНО: Проверяем, что metadata - это словарь
        if not isinstance(metadata, dict):
            print("Ошибка: Неверный формат метаданных. Пересоздаем...")
            metadata = {}  # Создаем новый словарь
        
        success = create_table(metadata, table_name, columns)
        
        if success:
            print(f'Таблица "{table_name}" успешно создана')
            # Показываем созданные столбцы
            metadata = load_metadata()  # Перезагружаем
            if isinstance(metadata, dict) and table_name in metadata:
                table_columns = metadata[table_name]["columns"]
                columns_str = ", ".join(table_columns)
                print(f"Столбцы: {columns_str}")
        else:
            print(f'Не удалось создать таблицу "{table_name}"')
        
        return False
        
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")
        return False


def handle_drop_table(args: List[str]) -> bool:
    """Обрабатывает команду удаления таблицы."""
    if len(args) != 1:
        msg = "Ошибка: Неверное количество аргументов. "
        msg += "Используйте: drop_table <имя_таблицы>"
        print(msg)
        return False

    table_name = args[0]
    
    try:
        metadata = load_metadata()
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False

        success = drop_table(metadata, table_name)
        if success:
            # ✅ ВАЖНО: Сохраняем обновленные метаданные
            from src.primitive_db.utils import save_metadata
            save_metadata(metadata)
            print(f'Таблица "{table_name}" успешно удалена.')
        else:
            print(f'Не удалось удалить таблицу "{table_name}"')
            return False
            
    except Exception as e:
        print(f"Ошибка при удалении таблицы: {e}")
        return False


def handle_list_tables(args: List[str]) -> bool:
    """
    Обрабатывает команду списка таблиц.

    Args:
        args: Аргументы команды

    Returns:
        False (не требует сохранения метаданных)
    """
    if args:
        print("Ошибка: Команда list_tables не принимает аргументов")
        return False

    metadata = load_metadata()
    
    # Проверяем тип
    if not isinstance(metadata, dict):
        print("Нет созданных таблиц")
        return False
        
    tables = list_tables(metadata)
    
    if not tables:
        print("Нет созданных таблиц")
    else:
        for table in tables:
            print(f"- {table}")
    
    return False



def handle_insert(args: List[str]) -> bool:
    """Обрабатывает команду INSERT."""
    if len(args) < 4 or args[0].lower() != "into" or args[2].lower() != "values":
        msg = "Ошибка: Неверный формат команды. "
        msg += "Используйте: insert into <table> values (...)"
        print(msg)
        return False

    table_name = args[1]
    values_str = " ".join(args[3:])
    
    try:
        values = parse_insert_values(values_str)
        metadata = load_metadata()
        
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False
            
        success = insert(metadata, table_name, values)
        
        if success:
            # Очищаем кэш при успешном добавлении
            clear_cache()
            # Загружаем данные таблицы чтобы найти новый ID
            table_data = load_table_data(table_name)
            if table_data:
                new_id = max(record["ID"] for record in table_data)
            else:
                new_id = 1
            print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
        else:
            print(f'Не удалось добавить запись в таблицу "{table_name}"')
            
        return False
        
    except Exception as e:
        print(f"Ошибка при добавлении записи: {e}")
        return False


def handle_select(args: List[str]) -> bool:
    """Обрабатывает команду SELECT."""
    if len(args) < 2 or args[0].lower() != "from":
        msg = "Ошибка: Неверный формат команды. "
        msg += "Используйте: select from <table> [where ...]"
        print(msg)
        return False

    table_name = args[1]
    where_clause = None
    
    # Парсим условие WHERE, если оно указано
    if len(args) > 3 and args[2].lower() == "where":
        where_condition = " ".join(args[3:])
        where_clause = parse_where_condition(where_condition)
    
    try:
        metadata = load_metadata()
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False
            
        # Используем кэширование
        cache_key = f"{table_name}_{str(where_clause)}"
        
        def get_data():
            return select(metadata, table_name, where_clause)
        
        filtered_data = cacher(cache_key, get_data)
        
        if not filtered_data:
            print("Записей не найдено")
            return False
        
        # Получаем названия столбцов из метаданных
        column_types = get_column_types(metadata, table_name)
        columns = list(column_types.keys())
        
        # Форматируем и выводим таблицу
        table_output = format_table_output(columns, filtered_data)
        print(table_output)
        
    except Exception as e:
        print(f"Ошибка при выборке данных: {e}")
    
    return False


def handle_update(args: List[str]) -> bool:
    """Обрабатывает команду UPDATE."""
    if (len(args) < 6 or args[1].lower() != "set" or
        "where" not in [arg.lower() for arg in args]):
        msg = "Ошибка: Неверный формат команды. "
        msg += "Используйте: update <table> set <col>=<val> where <col>=<val>"
        print(msg)
        return False

    table_name = args[0]
    
    # Определяем границы SET и WHERE условий
    where_index = None
    for i, arg in enumerate(args):
        if arg.lower() == "where":
            where_index = i
            break
    
    if where_index is None:
        print("Ошибка: Отсутствует условие WHERE")
        return False
    
    set_clause_str = " ".join(args[2:where_index])
    where_condition = " ".join(args[where_index + 1:])
    
    try:
        set_clause = parse_set_clause(set_clause_str)
        where_clause = parse_where_condition(where_condition)
        
        metadata = load_metadata()
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False
            
        success = update(metadata, table_name, set_clause, where_clause)
        
        if success:
            # Очищаем кэш при успешном обновлении
            clear_cache()
            print(f'Записи в таблице "{table_name}" успешно обновлены.')
        else:
            print(f'Не удалось обновить записи в таблице "{table_name}"')
            
    except Exception as e:
        print(f"Ошибка при обновлении данных: {e}")
    
    return False


def handle_delete(args: List[str]) -> bool:
    """Обрабатывает команду DELETE."""
    if len(args) < 4 or args[0].lower() != "from" or args[2].lower() != "where":
        msg = "Ошибка: Неверный формат команды. "
        msg += "Используйте: delete from <table> where <condition>"
        print(msg)
        return False

    table_name = args[1]
    where_condition = " ".join(args[3:])
    
    try:
        where_clause = parse_where_condition(where_condition)
        
        metadata = load_metadata()
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False
            
        success = delete(metadata, table_name, where_clause)
        
        if success:
            # Очищаем кэш при успешном удалении
            clear_cache()
            print(f'Записи из таблицы "{table_name}" успешно удалены.')
        else:
            print(f'Не удалось удалить записи из таблицы "{table_name}"')
            
    except Exception as e:
        print(f"Ошибка при удалении данных: {e}")
    
    return False

def handle_info(args: List[str]) -> bool:
    """Обрабатывает команду INFO."""
    if len(args) != 1:
        print("Ошибка: Используйте: info <имя_таблицы>")
        return False

    table_name = args[0]
    
    try:
        metadata = load_metadata()
        if not isinstance(metadata, dict):
            print("Ошибка: Метаданные повреждены")
            return False
            
        info = get_table_info(metadata, table_name)
        print(info)
        
    except Exception as e:
        print(f"Ошибка при получении информации о таблице: {e}")
    
    return False


def run():
    """Основная функция запуска базы данных."""
    print_welcome()
    
    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue
            
            # Разбиваем ввод на команду и аргументы
            parts = shlex.split(user_input)
            command = parts[0].lower()
            args = parts[1:]
            
            if command == "exit":
                print("Выход из программы...")
                break
            elif command == "help":
                print_help()
            elif command == "create_table":
                handle_create_table(args)
            elif command == "drop_table":
                handle_drop_table(args)
            elif command == "list_tables":
                handle_list_tables(args)
            elif command == "insert":
                handle_insert(args)
            elif command == "select":
                handle_select(args)
            elif command == "update":
                handle_update(args)
            elif command == "delete":
                handle_delete(args)
            elif command == "info":
                handle_info(args)
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                
        except Exception as e:
            print(f"Ошибка: {e}. Попробуйте снова.")