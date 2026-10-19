"""Цикл работы приложения: чтение команд, их разбор и вызов операций."""

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    COMMANDS,
    EXIT_COMMAND,
    HELP_MESSAGE,
    ID_COLUMN,
    META_FILE,
    MSG_INVALID_VALUE,
    MSG_NO_TABLES,
    MSG_ROW_DELETED,
    MSG_ROW_INSERTED,
    MSG_ROW_UPDATED,
    MSG_ROWS_NOT_FOUND,
    MSG_TABLE_CREATED,
    MSG_TABLE_DROPPED,
    MSG_TABLE_INFO,
    MSG_TABLE_ITEM,
    MSG_UNKNOWN_COMMAND,
    PROMPT_MESSAGE,
    WELCOME_MESSAGE,
    Columns,
    Metadata,
    TableData,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    find_ids,
    get_table_columns,
    insert,
    list_tables,
    select,
    update,
    validate_assignments,
    validate_clause,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import (
    parse_columns,
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
    split_args,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

# --- Вывод ---


def print_help() -> None:
    """Выводит справку по командам."""
    print(HELP_MESSAGE)


def format_columns(columns: Columns) -> str:
    """Форматирует схему таблицы в строку вида «ID:int, name:str»."""
    return ", ".join(f"{name}:{column_type}" for name, column_type in columns.items())


def print_rows(columns: Columns, rows: TableData) -> None:
    """Выводит записи таблицей PrettyTable."""
    table = PrettyTable(list(columns))
    table.add_rows([[row.get(column) for column in columns] for row in rows])
    print(table)


# --- Управление таблицами ---


def handle_create_table(
    metadata: Metadata, table_name: str, definitions: list[str]
) -> None:
    """Создаёт таблицу и сохраняет обновлённые метаданные."""
    metadata = create_table(metadata, table_name, parse_columns(definitions))
    if metadata is None:
        return
    save_metadata(META_FILE, metadata)
    columns = format_columns(metadata[table_name])
    print(MSG_TABLE_CREATED.format(table=table_name, columns=columns))


def handle_drop_table(metadata: Metadata, table_name: str) -> None:
    """Удаляет таблицу вместе с её данными."""
    metadata = drop_table(metadata, table_name)
    if metadata is None:
        return
    save_metadata(META_FILE, metadata)
    delete_table_data(table_name)
    print(MSG_TABLE_DROPPED.format(table=table_name))


def handle_list_tables(metadata: Metadata) -> None:
    """Выводит список таблиц."""
    tables = list_tables(metadata)
    if not tables:
        print(MSG_NO_TABLES)
    for table_name in tables:
        print(MSG_TABLE_ITEM.format(table=table_name))


def handle_info(metadata: Metadata, table_name: str) -> None:
    """Выводит схему таблицы и количество записей."""
    columns = format_columns(get_table_columns(metadata, table_name))
    count = len(load_table_data(table_name))
    print(MSG_TABLE_INFO.format(table=table_name, columns=columns, count=count))


# --- Операции с данными ---


def handle_insert(metadata: Metadata, user_input: str) -> None:
    """Добавляет запись в таблицу и сохраняет данные."""
    table_name, values = parse_insert(user_input)
    table_data = insert(metadata, table_name, values)
    if table_data is None:
        return
    save_table_data(table_name, table_data)
    print(MSG_ROW_INSERTED.format(id=table_data[-1][ID_COLUMN], table=table_name))


def handle_select(metadata: Metadata, user_input: str) -> None:
    """Выводит все записи таблицы или только подходящие под условие."""
    table_name, where_clause = parse_select(user_input)
    validate_clause(metadata, table_name, where_clause)
    rows = select(load_table_data(table_name), where_clause)
    if rows is None:
        return
    print_rows(get_table_columns(metadata, table_name), rows)


def handle_update(metadata: Metadata, user_input: str) -> None:
    """Обновляет подходящие под условие записи и сохраняет данные."""
    table_name, set_clause, where_clause = parse_update(user_input)
    validate_assignments(metadata, table_name, set_clause)
    validate_clause(metadata, table_name, where_clause)
    table_data = load_table_data(table_name)
    row_ids = find_ids(table_data, where_clause)
    if not row_ids:
        print(MSG_ROWS_NOT_FOUND)
        return
    table_data = update(table_data, set_clause, where_clause)
    if table_data is None:
        return
    save_table_data(table_name, table_data)
    for row_id in row_ids:
        print(MSG_ROW_UPDATED.format(id=row_id, table=table_name))


def handle_delete(metadata: Metadata, user_input: str) -> None:
    """Удаляет подходящие под условие записи и сохраняет данные."""
    table_name, where_clause = parse_delete(user_input)
    validate_clause(metadata, table_name, where_clause)
    table_data = load_table_data(table_name)
    row_ids = find_ids(table_data, where_clause)
    if not row_ids:
        print(MSG_ROWS_NOT_FOUND)
        return
    table_data = delete(table_data, where_clause)
    if table_data is None:
        return
    save_table_data(table_name, table_data)
    for row_id in row_ids:
        print(MSG_ROW_DELETED.format(id=row_id, table=table_name))


# --- Основной цикл ---


@handle_db_errors
def handle_command(metadata: Metadata, user_input: str) -> None:
    """Разбирает введённую строку и выполняет соответствующую команду."""
    match split_args(user_input):
        case ["help"]:
            print_help()
        case ["list_tables"]:
            handle_list_tables(metadata)
        case ["create_table", table_name, *definitions] if definitions:
            handle_create_table(metadata, table_name, definitions)
        case ["drop_table", table_name]:
            handle_drop_table(metadata, table_name)
        case ["info", table_name]:
            handle_info(metadata, table_name)
        case ["insert", *_]:
            handle_insert(metadata, user_input)
        case ["select", *_]:
            handle_select(metadata, user_input)
        case ["update", *_]:
            handle_update(metadata, user_input)
        case ["delete", *_]:
            handle_delete(metadata, user_input)
        case [command, *_] if command in COMMANDS:
            print(MSG_INVALID_VALUE.format(value=user_input.strip()))
        case [command, *_]:
            print(MSG_UNKNOWN_COMMAND.format(command=command))


def run() -> None:
    """Запускает основной цикл программы и работает до команды exit."""
    print(WELCOME_MESSAGE)
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        print()
        try:
            user_input = prompt.string(PROMPT_MESSAGE)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.strip() == EXIT_COMMAND:
            break
        handle_command(metadata, user_input)
