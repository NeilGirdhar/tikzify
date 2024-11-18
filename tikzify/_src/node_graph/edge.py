from collections.abc import Mapping
from dataclasses import dataclass
from functools import reduce
from typing import Any, TextIO

from ..foundation.pf import formatter, pf, tikz_option
from .node import NodeText, generate_node

__all__ = ['Edge', 'edge_text']


def edge_text(text: NodeText,
              arm: int | None = None) -> Mapping[str, Any]:
    d: dict[str, Any] = {}
    d['text'] = text
    if arm is not None:
        d['arm'] = arm
    return d


@dataclass
class Edge:
    from_: str | None = None
    to: str | None = None
    bend: float = 0
    in_: float | None = None
    out: float | None = None
    looseness: float | None = None
    loop: str | None = None
    opacity: float = 1
    dash: str | None = None
    color: str | None = None
    thickness: str | None = None
    text_node: Mapping[str, Any] | None = None

    def tip_string(self) -> str:
        def tip_convert(x: str | None) -> str:
            if not x:
                return ''
            if x in {'>', 'stealth', '|'}:
                return x
            return 'tip_' + x
        return tip_convert(self.from_) + '-' + tip_convert(self.to)

    def bend_string(self, *, loop: bool) -> str | None:
        if self.bend != 0:
            direction = 'left' if self.bend < 0 else 'right'
            angle = abs(self.bend)
            return f'[bend {direction}={angle}]'
        if loop or self.in_ is not None or self.out is not None:
            return formatter("[“loop, a, b, c”]",
                             loop=(None
                                   if not loop
                                   else ('loop ' + self.loop
                                         if self.loop
                                         else 'loop')),
                             a=tikz_option('in', str(self.in_)),
                             b=tikz_option('out', str(self.out)),
                             c=tikz_option('looseness', str(self.looseness)))

        return None

    def opacity_string(self) -> str | None:
        if self.opacity == 1:
            return None
        return tikz_option('opacity', str(self.opacity))

    def solve_for_color(self, edge_colors: Mapping[str, str] | None = None) -> str:
        if self.color is not None:
            return self.color
        if edge_colors is None:
            raise ValueError

        def choose_color(x: str | None, y: str | None) -> str | None:
            return min(x, y) if x and y else x or y

        retval = reduce(choose_color,
                        [edge_colors.get(x, None)
                         for x in [self.from_, self.to]
                         if x is not None],
                        None)
        if retval is None:
            msg = f"No color found for tips {self.from_} and {self.to}"
            raise ValueError(msg)
        return retval

    def pf(self,
           f: TextIO,
           source: str,
           target: str,
           color: str | None = None,
           text_node: Mapping[str, Any] | None = None,
           more_options: str | None = None,
           to_command: str = 'to') -> None:
        if color is None:
            color = self.color

        text_node = text_node if text_node is not None else self.text_node
        pf((r"\draw [“tip, color, opacity, dash, thickness, more_options”] "
            r"(“s”) “to_command” “bend ”"),
           more_options=more_options,
           thickness=self.thickness,
           dash=self.dash,
           opacity=self.opacity_string(),
           tip=self.tip_string(),
           color=color,
           bend=self.bend_string(loop=source == target),
           to_command=to_command,
           s=source,
           end='',
           file=f)
        if text_node is not None:
            generate_node(None, text_node, file=f, end=' ')
        pf(r"(“t”);",
           t=target,
           file=f)
