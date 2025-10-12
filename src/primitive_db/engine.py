import shlex
from typing import List

import prompt

from src.primitive_db.core import create_table, drop_table, get_table_columns, list_tables
from src.primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Выводит справочную информацию для режима работы с таблицами."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_welcome():
    """Выводит приветственное сообщение."""
    print("***База данных***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
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
        metadata = create_table(metadata, table_name, columns)
        save_metadata(metadata)
        
        # Показываем созданные столбцы
        table_columns = get_table_columns(metadata, table_name)
        columns_str = ", ".join(table_columns)
        print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
        return False
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False


def handle_drop_table(args: List[str]) -> bool:
    """
    Обрабатывает команду удаления таблицы.
    
    Args:
        args: Аргументы команды
        
    Returns:
        True если нужно сохранить метаданные, иначе False
    """
    if len(args) != 1:
        msg = "Ошибка: Неверное количество аргументов. "
        msg += "Используйте: drop_table <имя_таблицы>"
        print(msg)
        return False
    
    table_name = args[0]
    
    try:
        metadata = load_metadata()
        metadata = drop_table(metadata, table_name)
        save_metadata(metadata)
        print(f'Таблица "{table_name}" успешно удалена.')
        return False
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
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
    tables = list_tables(metadata)
    
    if not tables:
        print("Нет созданных таблиц")
    else:
        for table in tables:
            print(f"- {table}")
    
    return False


def run():
    """Основная функция запуска базы данных."""
    print_welcome()
    
    while True:
        try:
            user_input = prompt.string(">>>Введите команду: ").strip()
            
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
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                
        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}. Попробуйте снова.")
            