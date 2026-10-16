"""Работа с файловой системой: загрузка и сохранение данных в JSON."""

import json

from primitive_db.constants import FILE_ENCODING, JSON_INDENT, Metadata


def load_metadata(filepath: str) -> Metadata:
    """Загружает метаданные таблиц; если файла ещё нет, возвращает пустой словарь."""
    try:
        with open(filepath, encoding=FILE_ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: Metadata) -> None:
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(filepath, "w", encoding=FILE_ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)
