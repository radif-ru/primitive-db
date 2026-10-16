"""Цикл работы приложения: чтение команд, их разбор и вызов операций."""

import prompt

from primitive_db.constants import (
    COMMANDS,
    EXIT_COMMAND,
    HELP_MESSAGE,
    META_FILE,
    MSG_INVALID_VALUE,
    MSG_NO_TABLES,
    MSG_TABLE_CREATED,
    MSG_TABLE_DROPPED,
    MSG_TABLE_ITEM,
    MSG_UNKNOWN_COMMAND,
    PROMPT_MESSAGE,
    WELCOME_MESSAGE,
    Columns,
    Metadata,
)
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.parser import parse_columns, split_args
from primitive_db.utils import load_metadata, save_metadata


def print_help() -> None:
    """Выводит справку по командам."""
    print(HELP_MESSAGE)


def format_columns(columns: Columns) -> str:
    """Форматирует схему таблицы в строку вида «ID:int, name:str»."""
    return ", ".join(f"{name}:{column_type}" for name, column_type in columns.items())


def handle_create_table(
    metadata: Metadata, table_name: str, definitions: list[str]
) -> None:
    """Создаёт таблицу и сохраняет обновлённые метаданные."""
    metadata = create_table(metadata, table_name, parse_columns(definitions))
    save_metadata(META_FILE, metadata)
    columns = format_columns(metadata[table_name])
    print(MSG_TABLE_CREATED.format(table=table_name, columns=columns))


def handle_drop_table(metadata: Metadata, table_name: str) -> None:
    """Удаляет таблицу и сохраняет обновлённые метаданные."""
    save_metadata(META_FILE, drop_table(metadata, table_name))
    print(MSG_TABLE_DROPPED.format(table=table_name))


def handle_list_tables(metadata: Metadata) -> None:
    """Выводит список таблиц."""
    tables = list_tables(metadata)
    if not tables:
        print(MSG_NO_TABLES)
    for table_name in tables:
        print(MSG_TABLE_ITEM.format(table=table_name))


def handle_command(metadata: Metadata, user_input: str) -> None:
    """Разбирает введённую строку и выполняет соответствующую команду."""
    try:
        match split_args(user_input):
            case ["help"]:
                print_help()
            case ["list_tables"]:
                handle_list_tables(metadata)
            case ["create_table", table_name, *definitions] if definitions:
                handle_create_table(metadata, table_name, definitions)
            case ["drop_table", table_name]:
                handle_drop_table(metadata, table_name)
            case [command, *_] if command in COMMANDS:
                print(MSG_INVALID_VALUE.format(value=user_input.strip()))
            case [command, *_]:
                print(MSG_UNKNOWN_COMMAND.format(command=command))
    except (KeyError, ValueError) as error:
        print(error.args[0])


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
