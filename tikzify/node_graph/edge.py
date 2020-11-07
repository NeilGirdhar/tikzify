from functools import reduce
from typing import Any, Dict, Mapping, Optional, TextIO

from ..foundation.pf import formatter, pf, tikz_option
from .node import NodeText, generate_node

__all__ = ['Edge', 'edge_text']


def edge_text(text: NodeText,
              arm: Optional[int] = None) -> Mapping[str, Any]:
    d: Dict[str, Any] = {}
    d['text'] = text
    if arm is not None:
        d['arm'] = arm
    return d


class Edge:

    def __init__(self,
                 from_: Optional[str] = None,
                 to: Optional[str] = None,
                 bend: float = 0,
                 in_: Optional[float] = None,
                 out: Optional[float] = None,
                 looseness: Optional[float] = None,
                 loop: Optional[str] = None,
                 opacity: float = 1,
                 dash: Optional[str] = None,
                 color: Optional[str] = None,
                 thickness: Optional[str] = None,
                 text_node: Mapping[str, Any] = None,
                 **kwargs: Any):
        """
        * loop can be "left", "right", "above", "below", etc.
        """
        super().__init__(**kwargs)  # type: ignore
        self.from_ = from_
        self.to = to
        self.bend = bend
        self.in_ = in_
        self.out = out
        self.looseness = looseness
        self.opacity = opacity
        self.dash = dash
        self.loop = loop
        self.color = color
        self.thickness = thickness
        self.text_node = text_node

    def tip_string(self) -> str:
        def tip_convert(x: Optional[str]) -> str:
            if not x:
                return ''
            if x in ['>', 'stealth', '|']:
                return x
            return 'tip_' + x
        return tip_convert(self.from_) + '-' + tip_convert(self.to)

    def bend_string(self, loop: bool) -> Optional[str]:
        if self.bend != 0:
            return '[bend {}={}]'.format(
                'left' if self.bend < 0 else 'right',
                abs(self.bend))
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

    def opacity_string(self) -> Optional[str]:
        if self.opacity == 1 or self.opacity is None:
            return None
        return tikz_option('opacity', str(self.opacity))

    def solve_for_color(self, edge_colors: Optional[Mapping[str, str]] = None) -> str:
        if self.color is not None:
            return self.color
        if edge_colors is None:
            raise ValueError
        retval = reduce(lambda x, y: min(x, y) if x and y else x or y,
                        [edge_colors.get(x, None)
                         for x in [self.from_, self.to]
                         if x is not None],
                        None)
        if retval is None:
            raise ValueError(f"No color found for tips {self.from_} and {self.to}")
        return retval

    def pf(self,
           f: TextIO,
           source: str,
           target: str,
           color: Optional[str] = None,
           text_node: Optional[Mapping[str, Any]] = None,
           more_options: Optional[str] = None,
           to_command: str = 'to') -> None:
        if color is None:
            color = self.color

        text_node = text_node if text_node is not None else self.text_node
        pf(r"\draw [“tip, color, opacity, dash, thickness, more_options”] "
           + r"(“s”) “to_command” “bend ”",
           more_options=more_options,
           thickness=self.thickness,
           dash=self.dash,
           opacity=self.opacity_string(),
           tip=self.tip_string(),
           color=color,
           bend=self.bend_string(source == target),
           to_command=to_command,
           s=source,
           end='',
           file=f)
        if text_node is not None:
            generate_node(None, text_node, file=f, end=' ')
        pf(r"(“t”);",
           t=target,
           file=f)
