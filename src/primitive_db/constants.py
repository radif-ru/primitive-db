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
COMMANDS = frozenset({"create_table", "drop_table", "list_tables", "help", "exit"})

# --- Интерфейс ---
PROMPT_MESSAGE = ">>>Введите команду: "
WELCOME_MESSAGE = "***База данных***"
HELP_MESSAGE = """
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация"""

# --- Сообщения ---
MSG_TABLE_CREATED = 'Таблица "{table}" успешно создана со столбцами: {columns}'
MSG_TABLE_DROPPED = 'Таблица "{table}" успешно удалена.'
MSG_TABLE_ITEM = "- {table}"
MSG_NO_TABLES = "Таблиц пока нет."
MSG_TABLE_EXISTS = 'Ошибка: Таблица "{table}" уже существует.'
MSG_TABLE_NOT_FOUND = 'Ошибка: Таблица "{table}" не существует.'
MSG_DUPLICATE_COLUMN = 'Ошибка: Столбец "{column}" указан несколько раз.'
MSG_UNKNOWN_COMMAND = "Функции {command} нет. Попробуйте снова."
MSG_INVALID_VALUE = "Некорректное значение: {value}. Попробуйте снова."
