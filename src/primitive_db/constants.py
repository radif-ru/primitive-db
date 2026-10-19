"""Константы приложения: хранилище, схема таблиц, типы и тексты сообщений."""

# --- Хранилище ---
META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_EXTENSION = ".json"
FILE_ENCODING = "utf-8"
JSON_INDENT = 4

# --- Схема таблиц ---
ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")
PYTHON_TYPES = {"int": int, "str": str, "bool": bool}
COLUMN_TYPE_SEPARATOR = ":"

# --- Типы ---
type Columns = dict[str, str]
type Metadata = dict[str, Columns]
type Value = int | str | bool
type Row = dict[str, Value]
type TableData = list[Row]
type Clause = dict[str, Value]

# --- Синтаксис команд ---
PUNCTUATION_CHARS = "=(),"
ASSIGNMENT = "="
LIST_SEPARATOR = ","
OPEN_PARENTHESIS = "("
CLOSE_PARENTHESIS = ")"
QUOTE_CHARS = ('"', "'")
BOOL_LITERALS = {"true": True, "false": False}
KEYWORD_INTO = "into"
KEYWORD_VALUES = "values"
KEYWORD_FROM = "from"
KEYWORD_SET = "set"
KEYWORD_WHERE = "where"

# --- Команды ---
EXIT_COMMAND = "exit"
COMMANDS = frozenset(
    {
        "create_table",
        "drop_table",
        "list_tables",
        "insert",
        "select",
        "update",
        "delete",
        "info",
        "help",
        "exit",
    }
)

# --- Интерфейс ---
PROMPT_MESSAGE = ">>>Введите команду: "
CONFIRM_MESSAGE = 'Вы уверены, что хотите выполнить "{action}"? [y/n]: '
CONFIRM_ANSWER = "y"
ACTION_DROP_TABLE = "удаление таблицы"
ACTION_DELETE_ROWS = "удаление записи"
WELCOME_MESSAGE = "***База данных***"
HELP_MESSAGE = """
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***
Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация"""  # noqa: E501

# --- Сообщения ---
MSG_TABLE_CREATED = 'Таблица "{table}" успешно создана со столбцами: {columns}'
MSG_TABLE_DROPPED = 'Таблица "{table}" успешно удалена.'
MSG_TABLE_ITEM = "- {table}"
MSG_ACTION_CANCELLED = "Операция отменена."
MSG_NO_TABLES = "Таблиц пока нет."
MSG_TABLE_INFO = "Таблица: {table}\nСтолбцы: {columns}\nКоличество записей: {count}"
MSG_ROW_INSERTED = 'Запись с ID={id} успешно добавлена в таблицу "{table}".'
MSG_ROW_UPDATED = 'Запись с ID={id} в таблице "{table}" успешно обновлена.'
MSG_ROW_DELETED = 'Запись с ID={id} успешно удалена из таблицы "{table}".'
MSG_ROWS_NOT_FOUND = "Записи, удовлетворяющие условию, не найдены."
MSG_TABLE_EXISTS = 'Ошибка: Таблица "{table}" уже существует.'
MSG_TABLE_NOT_FOUND = 'Ошибка: Таблица "{table}" не существует.'
MSG_DUPLICATE_COLUMN = 'Ошибка: Столбец "{column}" указан несколько раз.'
MSG_COLUMN_NOT_FOUND = 'Ошибка: Столбец "{column}" не существует в таблице "{table}".'
MSG_ID_READONLY = 'Ошибка: Значение столбца "{column}" нельзя изменить.'
MSG_VALUES_COUNT = "Ошибка: Ожидалось значений: {expected}, передано: {actual}."
MSG_FILE_NOT_FOUND = (
    "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
)
MSG_UNEXPECTED_ERROR = "Произошла непредвиденная ошибка: {error}"
MSG_UNKNOWN_COMMAND = "Функции {command} нет. Попробуйте снова."
MSG_INVALID_VALUE = "Некорректное значение: {value}. Попробуйте снова."
