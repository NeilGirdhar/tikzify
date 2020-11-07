import re
from textwrap import dedent
from typing import Any, Match

__all__ = ['formatter']


def formatter(string_to_be_printed: str, **kwargs: Any) -> str:
    """
    Perform recursive string formatting on a string.  Any keywords enclosed in curly quotation marks
    are expanded using the keyword arguments passed into the function with a few details:
    * The formatter is applied recursively to the expanded string.  E.g.,
      formatter("“a”", a="expanded “b”", b="expanded c")
      returns
      'expanded expanded c'.
    * If a keyword is a comma-separated list like “a, b, c”, then each of the keywords "a", "b", and
      "c" are expanded and the results of joined with intervening commas.  If any expansion results
      in the None object, the formatter acts as if that term were not there.  E.g.,
      formatter("“a, b, c”", a="expanded a", b=None, c="expanded c")
      returns
      'expanded a, expanded c'.
    * Any keyword can contain a ':' in which case the Python string formatting applies, e.g.,
      “a:.6f” would look for 'a' in the keyword arguments and expanded the floating point number to
      six decimal places.
      formatter("“a:.3f, b:3d”", a=1.23456, b=7)
      returns
      '1.235, 007'
    Finally, the returned string is unindented and stripped of whitespace at either end.
    """
    def repl(m: Match[str]) -> str:
        keyword = m.group(1)
        retval = []
        for x in keyword.split(','):
            add_space = x and x[-1] == ' '
            x = x.strip()
            if x == '':
                retval.append('')
                continue
            if kwargs[x.split(':')[0]] is not None:
                y = str(('{' + x + '}').format(**kwargs))
                if add_space:
                    y += ' '
                retval.append(y)
        return ", ".join(retval)

    try:
        retval = re.sub(r"“(.+?)”", repl, dedent(string_to_be_printed)).strip('\n')
    except KeyError as e:
        raise Exception(f"No key \"{e.args[0]}\" found in {kwargs} for formatted string "
                        f"{string_to_be_printed}.") from None
    if '“' in retval:
        return formatter(retval, **kwargs)
    return retval
