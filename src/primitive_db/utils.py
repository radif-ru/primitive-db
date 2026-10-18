"""Работа с файловой системой: загрузка и сохранение данных в JSON."""

import json
import os

from primitive_db.constants import (
    DATA_DIR,
    DATA_FILE_EXTENSION,
    FILE_ENCODING,
    JSON_INDENT,
    Metadata,
    TableData,
)


def _read_json[T](filepath: str, default: T) -> T:
    """Читает JSON-файл; если файла нет, возвращает значение по умолчанию."""
    try:
        with open(filepath, encoding=FILE_ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _write_json(filepath: str, data: object) -> None:
    """Записывает данные в JSON-файл в читаемом виде."""
    with open(filepath, "w", encoding=FILE_ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def _table_path(table_name: str) -> str:
    """Возвращает путь к файлу с данными таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}{DATA_FILE_EXTENSION}")


def load_metadata(filepath: str) -> Metadata:
    """Загружает метаданные таблиц; если файла ещё нет, возвращает пустой словарь."""
    return _read_json(filepath, {})


def save_metadata(filepath: str, data: Metadata) -> None:
    """Сохраняет метаданные таблиц в JSON-файл."""
    _write_json(filepath, data)


def load_table_data(table_name: str) -> TableData:
    """Загружает записи таблицы; если файла ещё нет, возвращает пустой список."""
    return _read_json(_table_path(table_name), [])


def save_table_data(table_name: str, data: TableData) -> None:
    """Сохраняет записи таблицы в файл data/<имя_таблицы>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    _write_json(_table_path(table_name), data)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл с записями таблицы, если он есть."""
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
