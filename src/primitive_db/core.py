"""Бизнес-логика базы данных: управление таблицами."""

from primitive_db.constants import (
    ID_COLUMN,
    ID_TYPE,
    MSG_DUPLICATE_COLUMN,
    MSG_INVALID_VALUE,
    MSG_TABLE_EXISTS,
    MSG_TABLE_NOT_FOUND,
    VALID_TYPES,
    Columns,
    Metadata,
)


def get_table_columns(metadata: Metadata, table_name: str) -> Columns:
    """Возвращает схему таблицы или сообщает, что такой таблицы нет.

    >>> get_table_columns({"users": {"ID": "int"}}, "users")
    {'ID': 'int'}
    """
    if table_name not in metadata:
        raise KeyError(MSG_TABLE_NOT_FOUND.format(table=table_name))
    return metadata[table_name]


def create_table(
    metadata: Metadata, table_name: str, columns: list[tuple[str, str]]
) -> Metadata:
    """Добавляет в метаданные таблицу со столбцом ID и указанными столбцами.

    >>> create_table({}, "users", [("name", "str"), ("age", "int")])
    {'users': {'ID': 'int', 'name': 'str', 'age': 'int'}}
    """
    if not table_name.isidentifier():
        raise ValueError(MSG_INVALID_VALUE.format(value=table_name))
    if table_name in metadata:
        raise ValueError(MSG_TABLE_EXISTS.format(table=table_name))
    schema: Columns = {ID_COLUMN: ID_TYPE}
    for name, column_type in columns:
        if column_type not in VALID_TYPES:
            raise ValueError(MSG_INVALID_VALUE.format(value=column_type))
        if name in schema:
            raise ValueError(MSG_DUPLICATE_COLUMN.format(column=name))
        schema[name] = column_type
    metadata[table_name] = schema
    return metadata


def drop_table(metadata: Metadata, table_name: str) -> Metadata:
    """Удаляет таблицу из метаданных.

    >>> drop_table({"users": {"ID": "int"}}, "users")
    {}
    """
    get_table_columns(metadata, table_name)
    del metadata[table_name]
    return metadata


def list_tables(metadata: Metadata) -> list[str]:
    """Возвращает имена всех таблиц в порядке создания.

    >>> list_tables({"users": {"ID": "int"}, "orders": {"ID": "int"}})
    ['users', 'orders']
    """
    return list(metadata)
