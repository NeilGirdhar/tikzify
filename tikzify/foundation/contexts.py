from contextlib import contextmanager
from typing import Generator, Iterable, Mapping, Optional, TextIO

from .pf import pf

__all__ = ['tex_pic', 'tex_file']


@contextmanager
def tex_pic(f: TextIO,
            filename: str,
            pic_type: str,
            options: Mapping[str, str] = None) -> Generator[None, None, None]:
    """
    A context manager that creates a tikzpicture environment in the given file.  filename is the
    name of the generated pdf for the tikz code.
    """
    if options is None:
        options = {}
    pf(r"""
       % “filename” (fold)
       “ext”
       \begin{tikzpicture}“pt”
       """,
       pt=r"[/“pic_type”]" if pic_type else "",
       pic_type=pic_type,
       ext=r"\tikzsetnextfilename{“filename”}" if filename else "",
       filename=filename,
       file=f,
       **options)
    yield
    pf(r"""
       \end{tikzpicture} % (end)
       """,
       end='\n\n',
       file=f)


@contextmanager
def tex_file(filename: str,
             inputs: Optional[Iterable[str]] = None,
             preamble: Optional[str] = None) -> Generator[TextIO, None, None]:
    if inputs is None:
        inputs = []
    input_string = "\n".join(rf"\input{{{i}.tex}}" for i in inputs)
    if preamble is not None:
        input_string += "\n" + preamble
    with open(filename, 'wt') as f:
        pf(r"""
           \documentclass{memoir}
           \setlrmarginsandblock{25mm}{25mm}{*}
           \setulmarginsandblock{25mm}{25mm}{*}
           \setheadfoot{13pt}{26pt}
           \setheaderspaces{*}{13pt}{*}
           \checkandfixthelayout
           \makeatletter
           “input_string”
           \begin{document}
           """,
           file=f,
           input_string=input_string)
        yield f
        pf(r"""
           \end{document}
           """,
           file=f)
