import sys
from typing import IO, Any

from .formatter import formatter

__all__ = ['pf']


def pf(string_to_be_printed: str,
       file: IO[str] = sys.stdout,
       end: str = '\n',
       **kwargs: Any) -> None:
    """Format the string using formatter and print it to file with the given ending character."""
    print(formatter(string_to_be_printed, **kwargs), end=end, file=file)


def tikz_option(name: str, value: None | str) -> None | str:
    if value is None:
        return None
    return f"{name}={value}"
