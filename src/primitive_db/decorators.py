"""Декораторы операций с базой данных."""

from primitive_db.constants import MSG_FILE_NOT_FOUND, MSG_UNEXPECTED_ERROR


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
