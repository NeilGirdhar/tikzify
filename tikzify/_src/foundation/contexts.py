from collections.abc import Generator, Iterable, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

from .pf import pf

__all__ = ['tex_file', 'tex_pic']


@contextmanager
def tex_pic(f: TextIO,
            filename: str,
            pic_type: str,
            options: Mapping[str, str] | None = None
            ) -> Generator[None]:
    """A context manager that creates a tikzpicture environment in the given file.

    filename is the name of the generated pdf for the tikz code.
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
             inputs: Iterable[str] | None = None,
             preamble: str | None = None) -> Generator[TextIO, None, None]:
    if inputs is None:
        inputs = []
    input_string = "\n".join(rf"\input{{{i}.tex}}" for i in inputs)
    if preamble is not None:
        input_string += "\n" + preamble
    with Path(filename).open("w", encoding='utf-8') as f:
        pf(r"""
           \documentclass{memoir}
           \setlrmarginsandblock{25mm}{25mm}{*}
           \setulmarginsandblock{25mm}{25mm}{*}
           \setheadfoot{13pt}{26pt}
           \setheaderspaces{*}{13pt}{*}
           \checkandfixthelayout
           \makeatletter
           """,
           file=f)
        pf(input_string, file=f)
        pf(r"\begin{document}", file=f)
        yield f
        pf(r"\end{document}", file=f)
