from __future__ import annotations

from collections.abc import Iterable
from typing import Any, overload, override
from .constraints import Location

import numpy as np

__all__ = [
    'Anchor',
    'CoordinateAnchor',
    'IntersectionAnchor',
    'MidpointAnchor',
    'NodeAnchor',
    'RelativeAnchor',
]


def _fix_node(x: str | Anchor) -> Anchor:
    if isinstance(x, Anchor):
        return x
    return NodeAnchor(x)


class Anchor:
    def as_tikz(self) -> str:
        raise NotImplementedError

    def base_nodes(self) -> Iterable[str]:
        raise NotImplementedError


class CoordinateAnchor(Anchor):
    @overload
    def __init__(self, location: Location, /) -> None: ...
    @overload
    def __init__(self, x: float, y: float, /) -> None: ...
    def __init__(self, x: float | Location, y: float | None = None, /) -> None:
        super().__init__()
        if isinstance(x, Location):
            assert y is None
            self.x = x.x
            self.y = x.y
            return
        assert isinstance(x, int | float)
        assert isinstance(y, int | float)
        self.x = x
        self.y = y

    @override
    def as_tikz(self) -> str:
        return f"{self.x}, {self.y}"

    def as_array(self) -> np.ndarray[Any, Any]:
        return np.array([self.x, self.y], dtype='f')

    @override
    def base_nodes(self) -> Iterable[str]:
        return []

    @override
    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.x:.4f}, {self.y:.4f})'


class MidpointAnchor(Anchor):
    def __init__(self,
                 x: str | Anchor,
                 y: str | Anchor,
                 fraction: float = 0.5) -> None:
        super().__init__()
        self.x = _fix_node(x)
        self.y = _fix_node(y)
        self.fraction = fraction

    @override
    def as_tikz(self) -> str:
        return f"$({self.x.as_tikz()})!{self.fraction}!({self.y.as_tikz()})$"

    @override
    def base_nodes(self) -> Iterable[str]:
        yield from self.x.base_nodes()
        yield from self.y.base_nodes()


class RelativeAnchor(Anchor):
    def __init__(self, node: str | Anchor, anchor: Any) -> None:
        super().__init__()
        self.node = _fix_node(node)
        self.anchor = str(anchor)

    @override
    def as_tikz(self) -> str:
        return f"{self.node.as_tikz()}.{self.anchor}"

    @override
    def base_nodes(self) -> Iterable[str]:
        yield from self.node.base_nodes()


class NodeAnchor(Anchor):
    def __init__(self, node: str) -> None:
        super().__init__()
        self.node = node

    @override
    def as_tikz(self) -> str:
        return self.node

    @override
    def base_nodes(self) -> Iterable[str]:
        return [self.node]


class IntersectionAnchor(Anchor):
    def __init__(self, xnode: str | Anchor, ynode: str | Anchor) -> None:
        super().__init__()
        self.xnode = _fix_node(xnode)
        self.ynode = _fix_node(ynode)

    @override
    def as_tikz(self) -> str:
        return f"{self.xnode.as_tikz()} |- {self.ynode.as_tikz()}"

    @override
    def base_nodes(self) -> Iterable[str]:
        yield from self.xnode.base_nodes()
        yield from self.ynode.base_nodes()
