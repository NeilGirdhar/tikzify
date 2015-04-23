import sys
from typing import IO, Any, Mapping, Optional

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


def pf_option(dict_: Mapping[str, Optional[str]],
              name: str,
              key_name: Optional[str] = None) -> Optional[str]:
    if key_name is None:
        key_name = name
    if name in dict_ and dict_[name] is not None:
        value = dict_[name]
        if isinstance(value, (list, tuple)):
            value = ":".join(str(x) for x in value)
            retval = key_name + '=' + value
        elif value is True:
            retval = key_name
        else:
            value = str(value)
            retval = key_name + '=' + value
        return retval
    return None


def pf_option_value(name: str, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return "{}={}".format(name, value)
