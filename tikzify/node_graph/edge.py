from functools import reduce
from typing import Any, Mapping, Optional, TextIO

from ..foundation.pf import formatter, pf, pf_option
from .node import generate_node

__all__ = ['Edge']


class Edge:
    color: Optional[str]

    def __init__(self,
                 edge_colors: Mapping[str, str],
                 from_: Optional[str] = None,
                 to: Optional[str] = None,
                 bend: float = 0,
                 in_: Optional[float] = None,
                 out: Optional[float] = None,
                 looseness: Optional[float] = None,
                 loop: Optional[str] = None,
                 opacity: float = 1,
                 dash: Optional[str] = None,
                 col: Optional[str] = None,
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
        self.thickness = thickness
        self.text_node = text_node

        if col is not None:
            self.color = col
        else:
            self.color = reduce(lambda x, y: min(x, y) if x and y else x or y,
                                [edge_colors.get(x, None)
                                 for x in [self.from_, self.to]
                                 if x is not None],
                                None)

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
                             a=pf_option(self.__dict__, 'in_', 'in'),
                             b=pf_option(self.__dict__, 'out'),
                             c=pf_option(self.__dict__, 'looseness'))

        return None

    def opacity_string(self) -> Optional[str]:
        if self.opacity == 1 or self.opacity is None:
            return None
        return 'opacity={}'.format(self.opacity)

    def pf(self, f: TextIO, source: str, target: str,
           color: Optional[str] = None,
           text_node: Optional[Mapping[str, Any]] = None,
           more_options: Optional[str] = None,
           to_command: str = 'to') -> None:
        text_node = text_node if text_node is not None else self.text_node
        pf(r"\draw [“tip, color, opacity, dash, thickness, more_options”] "
           + r"(“s”) “to_command” “bend ”",
           more_options=more_options,
           thickness=self.thickness,
           dash=self.dash,
           opacity=self.opacity_string(),
           tip=self.tip_string(),
           color=color or self.color,
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
