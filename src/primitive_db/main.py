#!/usr/bin/env python3
"""Точка входа консольного приложения primitive_db."""

from primitive_db.engine import welcome


def main() -> None:
    """Запускает приложение."""
    welcome()


if __name__ == "__main__":
    main()
