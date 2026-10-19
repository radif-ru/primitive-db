"""Декораторы операций с базой данных и кэширование на замыкании."""

import time

import prompt

from primitive_db.constants import (
    CONFIRM_ANSWER,
    CONFIRM_MESSAGE,
    MSG_ACTION_CANCELLED,
    MSG_EXECUTION_TIME,
    MSG_FILE_NOT_FOUND,
    MSG_UNEXPECTED_ERROR,
)


def _copy_metadata(wrapper, func):
    """Переносит в обёртку имя, докстринг и ссылку на исходную функцию."""
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func):
    """Перехватывает ошибки операции, выводит сообщение и возвращает None.

    Тексты KeyError и ValueError уже сформулированы для пользователя
    по шаблонам из constants, поэтому выводятся как есть.

    >>> @handle_db_errors
    ... def find(table_name):
    ...     raise KeyError(f'Ошибка: Таблица "{table_name}" не существует.')
    >>> find("users")
    Ошибка: Таблица "users" не существует.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(MSG_FILE_NOT_FOUND)
        except (KeyError, ValueError) as error:
            print(error.args[0] if error.args else error)
        except Exception as error:
            print(MSG_UNEXPECTED_ERROR.format(error=error))
        return None

    return _copy_metadata(wrapper, func)


def confirm_action(action_name: str):
    """Фабрика декораторов: запрашивает подтверждение опасной операции.

    При любом ответе, кроме «y», операция отменяется и обёртка возвращает None.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(CONFIRM_MESSAGE.format(action=action_name))
            if answer.strip().lower() != CONFIRM_ANSWER:
                print(MSG_ACTION_CANCELLED)
                return None
            return func(*args, **kwargs)

        return _copy_metadata(wrapper, func)

    return decorator


def log_time(func):
    """Замеряет время выполнения функции и выводит его в консоль.

    >>> @log_time
    ... def noop():
    ...     return 42
    >>> noop()  # doctest: +ELLIPSIS
    Функция noop выполнилась за ... секунд.
    42
    """

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(MSG_EXECUTION_TIME.format(name=func.__name__, elapsed=elapsed))
        return result

    return _copy_metadata(wrapper, func)


def create_cacher():
    """Создаёт функцию кэширования, хранящую результаты в своём замыкании.

    >>> cache_result = create_cacher()
    >>> cache_result("users", lambda: print("вычисляем") or 42)
    вычисляем
    42
    >>> cache_result("users", lambda: print("вычисляем") or 42)
    42
    """
    cache: dict[object, object] = {}

    def cache_result(key: object, value_func):
        """Возвращает результат из кэша, а при промахе вычисляет и запоминает его."""
        if key in cache:
            return cache[key]
        value = value_func()
        if value is not None:
            cache[key] = value
        return value

    return cache_result
