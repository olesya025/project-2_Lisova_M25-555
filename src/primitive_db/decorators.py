import time
from typing import Any, Callable, Dict


def handle_db_errors(func: Callable) -> Callable:
    """Декоратор для обработки ошибок базы данных."""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            msg = "Ошибка: Файл данных не найден. "
            msg += "Возможно, база данных не инициализирована."
            print(msg)
            # Для функций загрузки возвращаем пустые структуры
            if func.__name__ in ['load_metadata', 'load_table_data']:
                if func.__name__ == 'load_metadata':
                    return {}
                else:
                    return []
            return False
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            if func.__name__ in ['load_metadata', 'load_table_data']:
                if func.__name__ == 'load_metadata':
                    return {}
                else:
                    return []
            return False
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return False
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            if func.__name__ in ['load_metadata', 'load_table_data']:
                if func.__name__ == 'load_metadata':
                    return {}
                else:
                    return []
            return False
    return wrapper

def confirm_action(action_name: str) -> Callable:
    """Фабрика декораторов для подтверждения действий."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            response = input(question).strip().lower()
            if response != 'y':
                print("Операция отменена.")
                return False
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func: Callable) -> Callable:
    """Декоратор для замера времени выполнения функции."""
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд.")
        return result
    return wrapper

def create_cacher() -> Callable:
    """Фабрика для создания кэшера с замыканием."""
    cache: Dict[str, Any] = {}
    
    def cache_result(key: str, value_func: Callable) -> Any:
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result