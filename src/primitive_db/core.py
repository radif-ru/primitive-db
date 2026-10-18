"""Бизнес-логика базы данных: управление таблицами и CRUD-операции."""

from primitive_db.constants import (
    ID_COLUMN,
    ID_TYPE,
    MSG_COLUMN_NOT_FOUND,
    MSG_DUPLICATE_COLUMN,
    MSG_ID_READONLY,
    MSG_INVALID_VALUE,
    MSG_TABLE_EXISTS,
    MSG_TABLE_NOT_FOUND,
    MSG_VALUES_COUNT,
    PYTHON_TYPES,
    VALID_TYPES,
    Clause,
    Columns,
    Metadata,
    Row,
    TableData,
    Value,
)
from primitive_db.utils import load_table_data

# --- Управление таблицами ---


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


# --- CRUD-операции ---


def _check_value(column_type: str, value: Value) -> None:
    """Проверяет, что значение соответствует типу столбца (bool не считается int).

    >>> _check_value("int", True)
    Traceback (most recent call last):
    ValueError: Некорректное значение: True. Попробуйте снова.
    >>> _check_value("int", "28")
    Traceback (most recent call last):
    ValueError: Некорректное значение: "28". Попробуйте снова.
    """
    if type(value) is not PYTHON_TYPES[column_type]:
        shown = f'"{value}"' if isinstance(value, str) else value
        raise ValueError(MSG_INVALID_VALUE.format(value=shown))


def validate_clause(metadata: Metadata, table_name: str, clause: Clause | None) -> None:
    """Проверяет, что столбцы условия существуют и значения подходят по типу."""
    columns = get_table_columns(metadata, table_name)
    for column, value in (clause or {}).items():
        if column not in columns:
            raise KeyError(MSG_COLUMN_NOT_FOUND.format(column=column, table=table_name))
        _check_value(columns[column], value)


def validate_assignments(metadata: Metadata, table_name: str, clause: Clause) -> None:
    """Проверяет присваивания: как условие, но столбец ID менять нельзя."""
    if ID_COLUMN in clause:
        raise ValueError(MSG_ID_READONLY.format(column=ID_COLUMN))
    validate_clause(metadata, table_name, clause)


def _matches(row: Row, where_clause: Clause) -> bool:
    """Проверяет, что запись удовлетворяет всем условиям."""
    return all(row.get(column) == value for column, value in where_clause.items())


def find_ids(table_data: TableData, where_clause: Clause) -> list[int]:
    """Возвращает ID записей, подходящих под условие.

    >>> find_ids([{"ID": 1, "age": 28}, {"ID": 2, "age": 30}], {"age": 30})
    [2]
    """
    return [row[ID_COLUMN] for row in table_data if _matches(row, where_clause)]


def insert(metadata: Metadata, table_name: str, values: list[Value]) -> TableData:
    """Проверяет значения, добавляет запись с новым ID и возвращает данные таблицы."""
    columns = get_table_columns(metadata, table_name)
    data_columns = [column for column in columns if column != ID_COLUMN]
    if len(values) != len(data_columns):
        raise ValueError(
            MSG_VALUES_COUNT.format(expected=len(data_columns), actual=len(values))
        )
    for column, value in zip(data_columns, values):
        _check_value(columns[column], value)
    table_data = load_table_data(table_name)
    new_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    table_data.append({ID_COLUMN: new_id} | dict(zip(data_columns, values)))
    return table_data


def select(table_data: TableData, where_clause: Clause | None = None) -> TableData:
    """Возвращает все записи или только подходящие под условие.

    >>> rows = [{"ID": 1, "age": 28}, {"ID": 2, "age": 30}]
    >>> select(rows, {"age": 28})
    [{'ID': 1, 'age': 28}]
    """
    if where_clause is None:
        return list(table_data)
    return [row for row in table_data if _matches(row, where_clause)]


def update(
    table_data: TableData, set_clause: Clause, where_clause: Clause
) -> TableData:
    """Обновляет поля подходящих под условие записей и возвращает данные.

    >>> update([{"ID": 1, "age": 28}], {"age": 29}, {"ID": 1})
    [{'ID': 1, 'age': 29}]
    """
    return [
        row | set_clause if _matches(row, where_clause) else row for row in table_data
    ]


def delete(table_data: TableData, where_clause: Clause) -> TableData:
    """Удаляет подходящие под условие записи и возвращает оставшиеся.

    >>> delete([{"ID": 1}, {"ID": 2}], {"ID": 1})
    [{'ID': 2}]
    """
    return [row for row in table_data if not _matches(row, where_clause)]
