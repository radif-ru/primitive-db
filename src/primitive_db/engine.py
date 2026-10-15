"""Цикл работы приложения: приветствие и обработка команд пользователя."""

import prompt

HELP_MESSAGE = (
    "<command> exit - выйти из программы\n<command> help - справочная информация"
)


def print_help() -> None:
    """Выводит список доступных команд."""
    print(HELP_MESSAGE)


def welcome() -> None:
    """Приветствует пользователя и обрабатывает команды до ввода exit."""
    print("Первая попытка запустить проект!\n\n***")
    print_help()
    while True:
        command = prompt.string("Введите команду: ").strip()
        match command:
            case "exit":
                break
            case "help":
                print()
                print_help()
            case _:
                print(f"Неизвестная команда: {command}")
