# primitive-db

Консольная СУБД на JSON-файлах с SQL-подобными командами.

## Установка и запуск

Нужен [uv](https://docs.astral.sh/uv/):

```bash
make install    # uv sync
make run        # uv run database
```

Установка как самостоятельной консольной команды:

```bash
make package-install    # uv build && uv tool install dist/*.whl
database
```

## Управление таблицами

| Команда | Действие |
|---------|----------|
| `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` | создать таблицу |
| `list_tables` | показать список всех таблиц |
| `drop_table <имя_таблицы>` | удалить таблицу |
| `help` | справочная информация |
| `exit` | выход из программы |

Поддерживаемые типы столбцов: `int`, `str`, `bool`. Столбец `ID:int` добавляется
автоматически первым. Структура таблиц хранится в `db_meta.json` в текущем каталоге.

```text
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```
