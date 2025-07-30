from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from textwrap import dedent, indent
from typing import TextIO


class Mode(Enum):
    code = auto()
    content = auto()


@dataclass
class Context:
    f: TextIO
    indent_level: int = 0
    indentation: int = 2

    @classmethod
    @contextmanager
    def create(cls, path: Path) -> Generator[Context]:
        f = path.open('w', encoding="utf-8")
        with f:
            yield Context(f)

    @contextmanager
    def nest(self) -> Generator[None]:
        self.indent_level += 1
        try:
            yield
        finally:
            self.indent_level -= 1

    def print(self, x: str) -> None:
        x = indent(dedent(x).strip(), " " * (self.indent_level * self.indentation))
        print(x, file=self.f)
