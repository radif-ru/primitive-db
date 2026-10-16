"""Разбор пользовательского ввода: аргументы команд и описания столбцов."""

import shlex

from primitive_db.constants import COLUMN_TYPE_SEPARATOR, MSG_INVALID_VALUE


def split_args(user_input: str) -> list[str]:
    """Делит строку команды на аргументы с учётом кавычек.

    >>> split_args("create_table users name:str age:int")
    ['create_table', 'users', 'name:str', 'age:int']
    """
    try:
        return shlex.split(user_input)
    except ValueError:
        raise ValueError(MSG_INVALID_VALUE.format(value=user_input)) from None


def parse_column(definition: str) -> tuple[str, str]:
    """Разбирает описание столбца вида «имя:тип».

    >>> parse_column("age:int")
    ('age', 'int')
    """
    name, separator, column_type = definition.partition(COLUMN_TYPE_SEPARATOR)
    if not separator or not name.isidentifier() or not column_type:
        raise ValueError(MSG_INVALID_VALUE.format(value=definition))
    return name, column_type


def parse_columns(definitions: list[str]) -> list[tuple[str, str]]:
    """Разбирает список описаний столбцов.

    >>> parse_columns(["name:str", "is_active:bool"])
    [('name', 'str'), ('is_active', 'bool')]
    """
    return [parse_column(definition) for definition in definitions]
