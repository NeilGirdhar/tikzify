from collections.abc import Sequence
from typing import TextIO

from ..foundation.pf import pf, tikz_option
from ..node_graph import Edge, NodeText
from .draw import FUNCTION_GRAPH_WIDTH, MARK_HEIGHT, MARK_WIDTH

__all__ = ['Annotation', 'RectAnnotation', 'BraceAnnotation', 'CircleAnnotation', 'EdgeAnnotation']


BRACE_HEIGHT = 0.3
UNCIRCLED_HEIGHT = 0.15
CIRCLE_HEIGHT = 0.25  # Offset of annotation.
CIRCLE_SCALE = 0.7  # corresponds to tikz_flow.tex
ARROW_SPACING = 0.40
SWIPE_OFFSET = -0.6
SWIPE_ANGLE = 50
LOOP_LOOSENESS = 1.5


class Annotation:
    def __init__(self, text: None | NodeText):
        self.text = text

    def generate(self, f: TextIO) -> None:
        raise NotImplementedError


class RectAnnotation(Annotation):
    def __init__(self,  # noqa: PLR0913
                 left: float,
                 right: float,
                 top: float,
                 bottom: float,
                 color: str,
                 fill_color: str,
                 text: None | NodeText = None,
                 direction: str = 'above',
                 coordinate: str = 'top',
                 *,
                 widen: bool = True):
        super().__init__(text=text)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.color = color
        self.fill_color = fill_color
        self.widen = widen
        self.direction = direction
        self.coordinate = coordinate

    def generate(self, f: TextIO) -> None:
        left = self.left * FUNCTION_GRAPH_WIDTH - MARK_WIDTH * self.widen
        right = self.right * FUNCTION_GRAPH_WIDTH + MARK_WIDTH * self.widen
        top = self.top + BRACE_HEIGHT
        bottom = self.bottom - BRACE_HEIGHT
        pf(r"""
           \coordinate (ll) at (“left”, “bottom”);
           \coordinate (ur) at (“right”, “top”);
           \node [shape=rectangle, thin, draw=“color”, fill=“fill_color”, fill opacity=0.4,
                  fit={(ll) (ur)}] (A) {};
           \node [“color”, “direction”=0mm of A.“coordinate”] {“text”};
           """,
           coordinate=self.coordinate,
           top=top,
           left=left,
           right=right,
           bottom=bottom,
           color=self.color,
           fill_color=self.fill_color,
           direction=self.direction,
           text=None if self.text is None else self.text.latex(inherit_color=self.color),
           file=f)


class BraceAnnotation(Annotation):
    def __init__(self,
                 left: float,
                 right: float,
                 y: float,
                 color: str,
                 *,
                 text: None | NodeText = None,
                 direction: str = 'above',
                 text_size: str = r'\footnotesize',
                 widen: bool = True):
        super().__init__(text=text)
        self.text_size = text_size
        self.left = left
        self.right = right
        self.y = y
        self.widen = widen
        self.direction = direction
        self.color = color

    def generate(self, f: TextIO) -> None:
        left = self.left * FUNCTION_GRAPH_WIDTH - MARK_WIDTH * self.widen
        right = self.right * FUNCTION_GRAPH_WIDTH + MARK_WIDTH * self.widen
        amp = (right - left) * 1.0
        pf(r"""
           \draw [-, decoration={brace,amplitude=“amp”mm}, decorate, thick, “color”]
               (“left”, “y”) -- (“right”, “y”)
           node [midway, inner sep=1pt, “color”,
           “direction”=“ampx”mm] {“text_size” “text”};
           """,
           amp=amp,
           ampx=amp + 0.5,
           left=left,
           right=right,
           y=self.y + BRACE_HEIGHT,
           color=self.color,
           direction=self.direction,
           text=None if self.text is None else self.text.latex(self.color),
           text_size=self.text_size,
           file=f)


class CircleAnnotation(Annotation):
    def __init__(self,
                 x: float,
                 y: float,
                 color: str,
                 text: None | NodeText = None,
                 direction: str = 'above',
                 *,
                 draw_circle: bool = True):
        super().__init__(text=text)
        self.x = x
        self.y = y
        self.direction = direction
        self.draw_circle = draw_circle
        self.color = color

    def generate(self, f: TextIO) -> None:
        pf(r"""
           \node[shape=circle, “draw,” inner sep=1pt, “color,”
           “direction”=“circle_height”]
           at (“x”, “y”) {\footnotesize “text”};
           """,
           direction=self.direction,
           draw='draw' if self.draw_circle else None,
           circle_height=(CIRCLE_HEIGHT
                          if self.draw_circle
                          else UNCIRCLED_HEIGHT),
           color=self.color,
           x=self.x * FUNCTION_GRAPH_WIDTH,
           y=self.y,
           text=None if self.text is None else self.text.latex(inherit_color=self.color),
           file=f)


class EdgeAnnotation(Annotation):
    def __init__(self,
                 edge: Edge,
                 y_source: float,
                 y_targets: Sequence[float],
                 x_source: float,
                 *,
                 x_target: None | float = None,
                 swipe: None | bool = None,
                 # edge options
                 loop: None | str = None,
                 swipe_right: bool = False,
                 # edge label options
                 text: None | NodeText = None,
                 swap: bool = False,
                 pos: None | float = None):
        assert pos is None or isinstance(pos, float)
        super().__init__(text=text)
        self.swipe = swipe
        self.y_source = y_source
        self.y_targets = y_targets
        self.x_source = x_source
        self.x_target = (x_source
                         if x_target is None
                         else x_target)
        self.swap = swap
        self.pos = str(pos) if pos is not None else None
        self.loop = loop
        self.edge = edge
        self.swipe_right = swipe_right

    def generate(self, f: TextIO) -> None:  # noqa: PLR0915
        x_source = self.x_source
        x_target = self.x_target

        def possibly_reverse_angle(angle: float, *, reverse_angle: bool) -> float:
            return 180 - angle if reverse_angle else angle

        def create_node(name: str, x: float, y: float, *, space: bool) -> None:
            if space:
                pf((r"\node (“name”) at (“x”, “y”) "
                    r"[shape=rectangle, minimum width=“width”cm, "
                    r"minimum height=“height”cm] {};"),
                   name=name,
                   width=MARK_WIDTH,
                   height=MARK_HEIGHT,
                   x=x * FUNCTION_GRAPH_WIDTH,
                   y=y,
                   file=f)
            else:
                pf(r"\coordinate (“name”) at (“x”, “y”);",
                   name=name,
                   x=x * FUNCTION_GRAPH_WIDTH,
                   y=y,
                   file=f)
        y_source = self.y_source
        y_targets = sorted(self.y_targets)
        swap = self.swap
        swipe = len(y_targets) > 1 or self.swipe or self.loop

        # text
        direction: None | int
        if swipe:
            below = y_targets and y_source > y_targets[0]
            if below:
                y_targets.reverse()
                direction = -1
            else:
                swap = not swap
                direction = 1
        else:
            direction = None

        text_node = ({"col": self.edge.color,
                          "pos": tikz_option('pos', self.pos),
                          "swap": 'swap' if swap else None,
                          "text": self.text}
                     if self.text is not None
                     else None)

        # create source node
        create_node('source node', x_source, y_source, space=True)

        # create target nodes
        for i, y_target in enumerate(y_targets):
            create_node(f'node {i}', x_target, y_target, space=True)

        # create swipe nodes
        if swipe:
            assert direction is not None
            # self.edge.col = self.edge.color()
            dy = 0.7
            x = (min(x_source, x_target)
                 + (-1.0 if self.swipe_right else 1.0) * SWIPE_OFFSET / FUNCTION_GRAPH_WIDTH)
            create_node('swipe node source', x, y_source + direction * dy, space=False)
            for i, y in enumerate(y_targets):
                create_node(f'swipe node {i}', x, y - direction * dy, space=False)

            self.edge.out = possibly_reverse_angle((90 + SWIPE_ANGLE) * direction,
                                                   reverse_angle=self.swipe_right)
            self.edge.in_ = possibly_reverse_angle(-90 * direction,
                                                   reverse_angle=self.swipe_right)
            to, self.edge.to = self.edge.to, None
            self.edge.pf(f, 'source node', 'swipe node source',
                         text_node=text_node)

            self.edge.out = possibly_reverse_angle(90 * direction,
                                                   reverse_angle=self.swipe_right)
            from_, self.edge.from_ = self.edge.from_, None
            if y_targets:
                self.edge.pf(f, 'swipe node source', f'swipe node {len(y_targets) - 1}')

            self.edge.in_ = possibly_reverse_angle(-(90 + SWIPE_ANGLE) * direction,
                                                   reverse_angle=self.swipe_right)
            self.edge.from_ = from_
            self.edge.to = to
            for i, _ in enumerate(y_targets):
                self.edge.pf(f,
                             f'swipe node {i}',
                             f'node {i}')

            if self.loop:
                self.edge.out = (90) * direction
                self.edge.in_ = (90) * direction
                self.edge.looseness = LOOP_LOOSENESS
                self.edge.pf(f, 'swipe node source', 'source node')
        else:
            self.edge.pf(f,
                         'source node',
                         'node 0',
                         text_node=text_node)
