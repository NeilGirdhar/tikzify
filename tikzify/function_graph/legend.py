from typing import Any, Mapping, Sequence, TextIO

from ..foundation import tex_pic
from ..foundation.pf import pf

__all__ = ['generate_legend', 'LegendItem', 'LegendRect', 'LegendNode', 'LegendArrow']


def generate_legend(f: TextIO,
                    x: float,
                    y: float,
                    element_lists: Sequence[Sequence[Any]],
                    direction: str = 'right',
                    width: float = 1) -> None:
    longest_list_length = max(len(element_list)
                              for element_list in element_lists)
    pf(r"""
       \node[inner sep=0pt, minimum size=0.0mm, “direction”=2mm] at (“x”, “y”) {
         \footnotesize
         \begin{tabular}{r“l”}
       """,
       x=x,
       y=y,
       l=r"@{}l" * (longest_list_length - 1),
       direction=direction,
       file=f)
    for element_list in element_lists:
        for i, element in enumerate(element_list):
            if i == 0:
                pf(r"“text”",
                   text=element,
                   end=' ',
                   file=f)
            elif element is None:
                pass
            else:
                with tex_pic(
                        f,
                        'legend_' + element.id_ if element.id_ else None,
                        'Flow diagram, '
                        'baseline={([yshift=-3pt]mainnode.base)}'):
                    element.generate(f, 0.0, 0.0, width)
            if i < len(element_list) - 1:
                pf(r"&",
                   file=f)
            else:
                pf(r"\\",
                   file=f)

    pf(r"""
         \end{tabular}
       };
       """,
       file=f)


class LegendItem:

    def __init__(self, id_: str):
        self.id_ = id_

    def generate(self, f: TextIO, x: float, y: float, width: float) -> None:
        raise NotImplementedError


class LegendRect(LegendItem):

    def __init__(self, id_: str, draw: str, fill: str):
        super().__init__(id_)
        self.draw = draw
        self.fill = fill

    def generate(self, f: TextIO, x: float, y: float, width: float) -> None:
        pf(r"""
           \node[thin, -, shape=rectangle, right, draw=“draw”, fill=“fill”,
                 inner sep=0pt,
                 minimum width=“width”cm, minimum height=“height”cm]
                 (mainnode)
                 at ({“x”}, {“y”}) {};
           """,
           draw=self.draw,
           fill=self.fill,
           width=width,
           height=0.28,
           x=x,
           y=y,
           file=f)


class LegendNode(LegendItem):

    def __init__(self, nodetype: str, id_: str, scale: float = 1):
        super().__init__(id_)
        self.nodetype = nodetype
        self.scale = scale

    def generate(self, f: TextIO, x: float, y: float, width: float) -> None:
        pf(r"""
           \node[scale=“scale”, transform shape, “nodetype”,
                 inner sep=2pt,
                 right
                 %minimum width=“width”cm,
                 %minimum height=“height”cm
                ]
                (mainnode) at (“x”, “y”) {};
           """,
           nodetype=self.nodetype,
           width=width,
           height=0.28,
           x=x,
           y=y,
           scale=self.scale,
           file=f)


class LegendArrow(LegendItem):

    def __init__(self, edge_colors: Mapping[str, str], tip: str, scale: float = 1):
        super().__init__(tip)
        self.tip = 'tip_' + tip
        self.scale = scale
        self.col = edge_colors.get(tip, None)

    def generate(self, f: TextIO, x: float, y: float, width: float) -> None:
        pf(r"""
           \node (mainnode) at (“x”, “y”) {};
           \draw [-{“tip”[scale=“scale”]}] (mainnode) edge [“col”] (“x2”, “y”);
           """,
           tip=self.tip,
           col=self.col,
           x=x,
           x2=x + width,
           y=y,
           scale=self.scale,
           file=f)
