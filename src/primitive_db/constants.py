# src/primitive_db/constants.py

# Пути к файлам
META_FILE = "db_meta.json"
DATA_DIR = "data"

# Поддерживаемые типы данных
SUPPORTED_TYPES = {"int", "str", "bool"}

# Сообщения
ERROR_TABLE_NOT_FOUND = 'Таблица "{}" не существует.'
ERROR_COLUMN_DEFINITION = "Неверное определение столбца: {}"
ERROR_UNSUPPORTED_TYPE = "Неподдерживаемый тип: {}. Поддерживаемые типы: {}"