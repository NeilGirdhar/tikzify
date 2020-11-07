from __future__ import annotations

from typing import Any, Iterable, Union

import numpy as np

__all__ = ['Anchor', 'CoordinateAnchor', 'MidpointAnchor', 'RelativeAnchor', 'NodeAnchor',
           'IntersectionAnchor']


def _fix_node(x: Union[str, Anchor]) -> Anchor:
    if isinstance(x, Anchor):
        return x
    if not isinstance(x, str):
        raise TypeError
    return NodeAnchor(x)


class Anchor:

    def as_tikz(self) -> str:
        raise NotImplementedError

    def base_nodes(self) -> Iterable[str]:
        raise NotImplementedError


class CoordinateAnchor(Anchor):

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def as_tikz(self) -> str:
        return f"{self.x}, {self.y}"

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype='f')

    def base_nodes(self) -> Iterable[str]:
        return []

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.x:.4f}, {self.y:.4f})'


class MidpointAnchor(Anchor):

    def __init__(self,
                 x: Union[str, Anchor],
                 y: Union[str, Anchor],
                 fraction: float = 0.5):
        self.x = _fix_node(x)
        self.y = _fix_node(y)
        self.fraction = fraction

    def as_tikz(self) -> str:
        return "$({})!{}!({})$".format(self.x.as_tikz(),
                                       self.fraction,
                                       self.y.as_tikz())

    def base_nodes(self) -> Iterable[str]:
        yield from self.x.base_nodes()
        yield from self.y.base_nodes()


class RelativeAnchor(Anchor):

    def __init__(self, node: Union[str, Anchor], anchor: Any):
        self.node = _fix_node(node)
        self.anchor = str(anchor)

    def as_tikz(self) -> str:
        return f"{self.node.as_tikz()}.{self.anchor}"

    def base_nodes(self) -> Iterable[str]:
        yield from self.node.base_nodes()


class NodeAnchor(Anchor):

    def __init__(self, node: str):
        self.node = node

    def as_tikz(self) -> str:
        return self.node

    def base_nodes(self) -> Iterable[str]:
        return [self.node]


class IntersectionAnchor(Anchor):

    def __init__(self, xnode: Union[str, Anchor], ynode: Union[str, Anchor]):
        self.xnode = _fix_node(xnode)
        self.ynode = _fix_node(ynode)

    def as_tikz(self) -> str:
        return f"{self.xnode.as_tikz()} |- {self.ynode.as_tikz()}"

    def base_nodes(self) -> Iterable[str]:
        yield from self.xnode.base_nodes()
        yield from self.ynode.base_nodes()
