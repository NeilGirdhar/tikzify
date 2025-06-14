import re
from re import Match
from textwrap import dedent

__all__ = ['formatter']


def formatter(string_to_be_printed: str, **kwargs: object) -> str:
    """Perform recursive string formatting on a string.

    Any keywords enclosed in curly quotation marks are expanded using the keyword arguments passed
    into the function with a few details:
    * The formatter is applied recursively to the expanded string.  E.g.,
      formatter("“a”", a="expanded “b”", b="expanded c")

    Returns:
      'expanded expanded c'.
    * If a keyword is a comma-separated list like “a, b, c”, then each of the keywords "a", "b", and
      "c" are expanded and the results of joined with intervening commas.  If any expansion results
      in the None object, the formatter acts as if that term were not there.  E.g.,
      formatter("“a, b, c”", a="expanded a", b=None, c="expanded c")

    Returns:
      'expanded a, expanded c'.
    * Any keyword can contain a ':' in which case the Python string formatting applies, e.g.,
      “a:.6f” would look for 'a' in the keyword arguments and expanded the floating point number to
      six decimal places.
      formatter("“a:.3f, b:3d”", a=1.23456, b=7)

    Returns:
      '1.235, 007'
    Finally, the returned string is unindented, stripped of whitespace at either end, and line
    continuations (using backslash) are applied.
    """
    def repl(m: Match[str]) -> str:
        keyword = m.group(1)
        retval = []
        for x in keyword.split(','):
            add_space = x and x[-1] == ' '
            stripped_x = x.strip()
            if not stripped_x:
                retval.append('')
                continue
            if kwargs[stripped_x.split(':')[0]] is not None:
                y = str(('{' + stripped_x + '}').format(**kwargs))
                if add_space:
                    y += ' '
                retval.append(y)
        return ", ".join(retval)

    try:
        expanded_macros = re.sub(r"“(.+?)”", repl, string_to_be_printed)
        dedented = dedent(expanded_macros)
        stripped = dedented.strip('\n')
        retval = re.sub("%\n *", "", stripped)  # noqa: RUF039
    except KeyError as e:
        msg = (f'No key "{e.args[0]}" found in {kwargs} for formatted string '
               f"{string_to_be_printed}.")
        raise ValueError(msg) from None
    if '“' in retval:
        return formatter(retval, **kwargs)
    return retval
