from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, override

from .context import Context


def render_key(x: str, /) -> str:
    return x.replace('_', '-')


def render_value(x: object, /) -> str:  # noqa: PLR0911
    match x:
        case None:
            return "none"
        case str():
            return f'"{x}"'
        case bool():
            return "true" if x else "false"
        case int():
            return str(x)
        case float():
            return f"{x:.6f}"
        case tuple():
            mid = ", ".join(render_value(y) for y in x)
            return f"({mid})"
        case dict():
            mid = ", ".join(f"{render_key(key)}: {render_value(value)}"
                            for key, value in x.items())
            return f"({mid})"
        case Element():
            return x.render()
        case _:
            msg = f"Cannot render value of type {type(x).__name__}"
            raise TypeError(msg)


class Element:
    def render(self) -> str:
        raise NotImplementedError

    def multiline(self, c: Context) -> None:
        c.print(self.render())


@dataclass
class TypstObject(Element):
    name: str

    @override
    def render(self) -> str:
        return self.name


@dataclass
class Math(Element):
    value: str

    @override
    def render(self) -> str:
        return f"${self.value}$"


@dataclass
class Import(Element):
    from_: str
    what: tuple[str, ...] | Literal[True] | None = True

    @override
    def render(self) -> str:
        if self.what is None:
            return f'import "{self.from_}'
        what_str = '*' if self.what is True else ', '.join(self.what)
        return f'import "{self.from_}: {what_str}'


# @dataclass
# class Block(Element):
#     elements: list[Element]
#     delims: tuple[str, str]
#     mode: Mode
#
#     @override
#     def render(self, c: Context) -> None:
#         c.print(self.delims[0], need_code=True)
#         with c.indented(mode=self.mode) as indented:
#             for element in self.elements:
#                 element.render(indented)
#         c.print(self.delims[1])
#
#
# @dataclass
# class CodeBlock(Block):
#     delims: tuple[str, str] = ('{', '}')
#     mode: Mode = Mode.code
#
#
# @dataclass
# class ContentBlock(Block):
#     delims: tuple[str, str] = ('[', ']')
#     mode: Mode = Mode.content
