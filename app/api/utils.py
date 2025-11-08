import re

from .exc import validation_error


def to_snake(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    s = s.lower()
    return s


def check_numbers(value: str) -> str:
    if any(char.isdigit() for char in value):
        raise validation_error("Aliases must not contain numbers")
    return value
