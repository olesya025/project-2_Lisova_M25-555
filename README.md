markdown
# Primitive Database

Простая база данных с поддержкой CRUD-операций, реализованная на Python.

## Установка

```bash
# Установка через pipx
pipx install project-2-lisova-m25-555

# Или локальная установка
make install
make build
make package-install
Запуск
bash
# После глобальной установки
database

# Или в режиме разработки
make database
Управление таблицами
Создание таблицы
bash
create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...
Поддерживаемые типы: int, str, bool

Пример:

bash
create_table users name:str age:int is_active:bool
Просмотр таблиц
bash
list_tables
Удаление таблицы
bash
drop_table <имя_таблицы>
CRUD-операции
Добавление записи (CREATE)
bash
insert into <имя_таблицы> values (<значение1>, <значение2>, ...)
Примечание: ID генерируется автоматически, не включайте его в значения.

Пример:

bash
insert into users values ("Sergei", 28, true)
Чтение записей (READ)
Все записи:

bash
select from <имя_таблицы>
С условием:

bash
select from <имя_таблицы> where <столбец> = <значение>
Примеры:

bash
select from users
select from users where age = 28
select from users where name = "Sergei"
Обновление записей (UPDATE)
bash
update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия>
Пример:

bash
update users set age = 29 where name = "Sergei"
Удаление записей (DELETE)
bash
delete from <имя_таблицы> where <столбец> = <значение>
Пример:

bash
delete from users where ID = 1
Информация о таблице
bash
info <имя_таблицы>
Выводит:

Название таблицы

Столбцы с типами

Количество записей

Пример сессии работы
bash
>>> create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>> insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>> select from users
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+

>>> update users set age = 29 where name = "Sergei"
Записи в таблице "users" успешно обновлены.

>>> info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 1
Структура проекта
text
project-2_Lisova_M25-555/
├── data/                    # Данные таблиц
├── src/primitive_db/
│   ├── main.py             # Точка входа
│   ├── engine.py           # Обработчик команд
│   ├── core.py             # Логика CRUD операций
│   ├── utils.py            # Работа с файлами
│   └── parser.py           # Парсер условий
├── db_meta.json            # Метаданные БД
└── pyproject.toml          # Конфигурация
Разработка
bash
make install      # Установка зависимостей
make database     # Запуск в режиме разработки
make build        # Сборка пакета
make lint         # Проверка кода
Особенности
Автоматическая генерация ID для записей

Валидация типов данных

Раздельное хранение метаданных и данных

Красивый табличный вывод через PrettyTable

Поддержка условий WHERE в запросах