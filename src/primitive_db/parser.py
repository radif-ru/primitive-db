"""Разбор пользовательского ввода: аргументы команд, столбцы, значения и условия."""

import shlex

from primitive_db.constants import (
    ASSIGNMENT,
    BOOL_LITERALS,
    CLOSE_PARENTHESIS,
    COLUMN_TYPE_SEPARATOR,
    KEYWORD_FROM,
    KEYWORD_INTO,
    KEYWORD_SET,
    KEYWORD_VALUES,
    KEYWORD_WHERE,
    LIST_SEPARATOR,
    MSG_INVALID_VALUE,
    OPEN_PARENTHESIS,
    PUNCTUATION_CHARS,
    QUOTE_CHARS,
    Clause,
    Value,
)


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


def tokenize(text: str) -> list[str]:
    """Делит строку на слова, литералы в кавычках и знаки «=», «(», «)», «,».

    >>> tokenize('values ("Sergei Ivanov", 28)')
    ['values', '(', '"Sergei Ivanov"', ',', '28', ')']
    >>> tokenize('update users set name="A, B" where ID=1')
    ['update', 'users', 'set', 'name', '=', '"A, B"', 'where', 'ID', '=', '1']
    """
    lexer = shlex.shlex(text, posix=False, punctuation_chars=PUNCTUATION_CHARS)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        raise ValueError(MSG_INVALID_VALUE.format(value=text.strip())) from None
    # shlex склеивает подряд идущие знаки («()», «),») — разделяем их.
    return [
        part
        for token in tokens
        for part in (token if set(token) <= set(PUNCTUATION_CHARS) else [token])
    ]


def parse_literal(token: str) -> Value:
    """Превращает литерал в значение: строку в кавычках, true/false или целое.

    >>> parse_literal('"Sergei"'), parse_literal("28"), parse_literal("True")
    ('Sergei', 28, True)
    >>> parse_literal("Sergei")
    Traceback (most recent call last):
    ValueError: Некорректное значение: Sergei. Попробуйте снова.
    """
    if len(token) >= 2 and token[0] == token[-1] and token[0] in QUOTE_CHARS:
        return token[1:-1]
    if token.lower() in BOOL_LITERALS:
        return BOOL_LITERALS[token.lower()]
    try:
        return int(token)
    except ValueError:
        raise ValueError(MSG_INVALID_VALUE.format(value=token)) from None


def _split_list(tokens: list[str]) -> list[list[str]]:
    """Делит токены на группы по запятым."""
    groups: list[list[str]] = [[]]
    for token in tokens:
        if token == LIST_SEPARATOR:
            groups.append([])
        else:
            groups[-1].append(token)
    return groups


def _is_keyword(token: str, keyword: str) -> bool:
    """Проверяет, что токен — ключевое слово (без учёта регистра)."""
    return token.lower() == keyword


def parse_values(tokens: list[str]) -> list[Value]:
    """Разбирает список значений вида «( значение1 , значение2 , ... )».

    >>> parse_values(tokenize('("Sergei", 28, true)'))
    ['Sergei', 28, True]
    """
    if tokens[:1] != [OPEN_PARENTHESIS] or tokens[-1:] != [CLOSE_PARENTHESIS]:
        raise ValueError(MSG_INVALID_VALUE.format(value=" ".join(tokens)))
    inner = tokens[1:-1]
    if not inner:
        return []
    values = []
    for group in _split_list(inner):
        if len(group) != 1:
            raise ValueError(MSG_INVALID_VALUE.format(value=" ".join(tokens)))
        values.append(parse_literal(group[0]))
    return values


def parse_condition(tokens: list[str]) -> Clause:
    """Разбирает условие вида «столбец = значение» в словарь.

    >>> parse_condition(tokenize("age = 28"))
    {'age': 28}
    >>> parse_condition(tokenize('name="Sergei"'))
    {'name': 'Sergei'}
    """
    match tokens:
        case [column, operator, literal] if (
            operator == ASSIGNMENT and column.isidentifier()
        ):
            return {column: parse_literal(literal)}
    raise ValueError(MSG_INVALID_VALUE.format(value=" ".join(tokens)))


def parse_assignments(tokens: list[str]) -> Clause:
    """Разбирает присваивания вида «столбец1 = значение1, столбец2 = значение2».

    >>> parse_assignments(tokenize('age = 29, name = "Ivan"'))
    {'age': 29, 'name': 'Ivan'}
    """
    clause: Clause = {}
    for group in _split_list(tokens):
        clause |= parse_condition(group)
    return clause


def parse_insert(text: str) -> tuple[str, list[Value]]:
    """Разбирает «insert into <таблица> values (...)».

    >>> parse_insert('insert into users values ("Sergei", 28, true)')
    ('users', ['Sergei', 28, True])
    """
    match tokenize(text):
        case [_, into, table_name, values, *rest] if _is_keyword(
            into, KEYWORD_INTO
        ) and _is_keyword(values, KEYWORD_VALUES):
            return table_name, parse_values(rest)
    raise ValueError(MSG_INVALID_VALUE.format(value=text.strip()))


def parse_select(text: str) -> tuple[str, Clause | None]:
    """Разбирает «select from <таблица> [where <столбец> = <значение>]».

    >>> parse_select("select from users")
    ('users', None)
    >>> parse_select("select from users where age = 28")
    ('users', {'age': 28})
    """
    match tokenize(text):
        case [_, from_, table_name] if _is_keyword(from_, KEYWORD_FROM):
            return table_name, None
        case [_, from_, table_name, where, *condition] if (
            condition
            and _is_keyword(from_, KEYWORD_FROM)
            and _is_keyword(where, KEYWORD_WHERE)
        ):
            return table_name, parse_condition(condition)
    raise ValueError(MSG_INVALID_VALUE.format(value=text.strip()))


def parse_update(text: str) -> tuple[str, Clause, Clause]:
    """Разбирает «update <таблица> set <присваивания> where <условие>».

    >>> parse_update('update users set age = 29 where name = "Sergei"')
    ('users', {'age': 29}, {'name': 'Sergei'})
    """
    match tokenize(text):
        case [_, table_name, set_, *rest] if _is_keyword(set_, KEYWORD_SET):
            keywords = [token.lower() for token in rest]
            if KEYWORD_WHERE in keywords[1:-1]:
                position = keywords.index(KEYWORD_WHERE)
                assignments = parse_assignments(rest[:position])
                return table_name, assignments, parse_condition(rest[position + 1 :])
    raise ValueError(MSG_INVALID_VALUE.format(value=text.strip()))


def parse_delete(text: str) -> tuple[str, Clause]:
    """Разбирает «delete from <таблица> where <условие>».

    >>> parse_delete("delete from users where ID = 1")
    ('users', {'ID': 1})
    """
    match tokenize(text):
        case [_, from_, table_name, where, *condition] if (
            condition
            and _is_keyword(from_, KEYWORD_FROM)
            and _is_keyword(where, KEYWORD_WHERE)
        ):
            return table_name, parse_condition(condition)
    raise ValueError(MSG_INVALID_VALUE.format(value=text.strip()))
