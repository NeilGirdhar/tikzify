import sys
from typing import IO, Any, Optional

from .formatter import formatter

__all__ = ['pf']


def pf(string_to_be_printed: str,
       file: IO[str] = sys.stdout,
       end: str = '\n',
       **kwargs: Any) -> None:
    """
    Format the string using formatter and print it to file with the given ending character.
    """
    print(formatter(string_to_be_printed, **kwargs), end=end, file=file)


def tikz_option(name: str, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return "{}={}".format(name, value)


def tikz_flag(name: str, value: Optional[bool]) -> Optional[str]:
    if value is None or not value:
        return None
    return name
