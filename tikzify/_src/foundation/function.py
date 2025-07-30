from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import MISSING, dataclass
from inspect import signature
from types import FunctionType
from typing import override

from .context import Context
from .elements import Element, render_key, render_value


@dataclass
class CalledFunction(Element):
    f: Function
    args: tuple[object, ...]
    kwargs: Mapping[str, object]
    inline: bool = False

    @override
    def render(self) -> str:
        raise NotImplementedError

    @override
    def multiline(self, c: Context) -> None:
        defaults = {} if self.f.defaults is None else self.f.defaults
        c.print(f"{self.f.name}(")  # )
        with c.nest():
            for value in self.args:
                c.print(f"{render_value(value)},")
            for key, value in self.kwargs.items():
                if key in defaults and value == defaults[key]:
                    continue
                c.print(f"{render_key(key)}: {render_value(value)},")
        c.print(")")


@dataclass
class Function:
    name: str
    defaults: Mapping[str, object] | None = None

    def __call__(self,
                 *args: object,
                 inline: bool = False,
                 **kwargs: object
                 ) -> CalledFunction:
        return CalledFunction(self, args, kwargs, inline=inline)


def function() -> Callable[[FunctionType], Function]:
    def inner(f: FunctionType) -> Function:
        sig = signature(f)
        defaults = {}
        for name, parameter in sig.parameters.items():
            if parameter.default is not MISSING:
                defaults[name.replace('_', '-')] = parameter.default
        return Function(f.__name__, defaults)
    return inner
