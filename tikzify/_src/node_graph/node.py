from collections.abc import Collection, Sequence
from dataclasses import KW_ONLY, dataclass
from enum import Enum, auto
from functools import reduce
from typing import TYPE_CHECKING, TextIO

import numpy as np
from rectangle import Rect

from .anchor import Anchor

if TYPE_CHECKING:
    from .graph import NodeGraph


class Alignment(Enum):
    left = auto()
    right = auto()
    center = auto()


class TextSize(Enum):
    tiny = auto()
    script = auto()
    footnote = auto()
    small = auto()
    normalsize = auto()
    large = auto()
    Large = auto()
    LARGE = auto()
    huge = auto()
    Huge = auto()


def format_length(length: float | None) -> str | None:
    if length is None:
        return None
    if int(length) == length:
        length = int(length)
    return f"{length}cm"


def wrap_text(text_lines: Sequence[str],
              color: str | None,
              wrap_command: str | None,
              size: TextSize | None,
              *,
              standard_height: bool) -> str:
    def wrap(line: str) -> str:
        if standard_height:
            line = r'\vphantom{Ag}' + line
        if size is not None:
            size_text = '\\' + (size.name + 'size'
                                if size in {TextSize.script, TextSize.footnote}
                                else size.name) + ' '
            line = size_text + line
        if color is not None:
            line = r'\textcolor{' + color + '}{' + line + '}'
        elif size is not None:
            line = '{' + line + '}'
        if wrap_command is not None:
            line = rf"\{wrap_command}{{{line}}}"
        return line
    retval = r' \\ '.join(wrap(line) for line in text_lines)
    # if '\\' in retval:
    #     retval = '{' + retval + '}'
    return retval  # noqa: RET504


@dataclass
class TerminalSpacing:
    horizontal: Sequence[float]
    vertical: Sequence[float]


@dataclass
class NodeText:
    text_lines: Sequence[str]
    color: str | None = None
    _: KW_ONLY
    wrap_command: str | None = None
    width: float | None = None
    align: Alignment | None = None
    size: TextSize | None = None
    standard_height: bool = False

    def latex(self, inherit_color: str | None) -> str:
        return wrap_text(self.text_lines,
                         inherit_color if self.color is None else self.color,
                         self.wrap_command,
                         self.size,
                         standard_height=self.standard_height)

    def latex_options(self) -> str | None:
        if self.align is None and len(self.text_lines) >= 2:  # noqa: PLR2004
            msg = "No alignment specified"
            raise ValueError(msg)
        retval = formatter("“text_width,align”",
                           text_width=tikz_option('text width', format_length(self.width)),
                           align=(None
                                  if self.align is None
                                  else tikz_option('align', self.align.name)))
        return retval or None


@dataclass
class NodeLabel:
    text_lines: Sequence[str]
    location: str | None = None
    color: str | None = None
    size: TextSize | None = None
    standard_height: bool = False

    def latex(self, inherit_color: str | None) -> str:
        text_lines = self.text_lines

        color = inherit_color if self.color is None else self.color
        text = wrap_text(text_lines, color, None, self.size, standard_height=self.standard_height)
        if self.location:
            text = f'{self.location}:{text}'
        return 'label=' + text


@dataclass
class NodePosition:
    anchor: Anchor
    left: float | None = None
    right: float | None = None
    above: float | None = None
    below: float | None = None

    def __post_init__(self) -> None:
        assert self.left is None or self.right is None
        assert self.above is None or self.below is None

    def is_relative(self) -> bool:
        return not all(x is None for x in [self.left, self.right, self.above, self.below])

    def latex_position(self) -> str:
        if self.is_relative():
            return ""
        return f'at ({self.anchor.as_tikz()}) '

    def latex_relative_position(self) -> str:
        if not self.is_relative():
            return ""
        words = []
        values = []
        if self.above is not None:
            words.append('above')
            values.append(self.above)
        elif self.below is not None:
            words.append('below')
            values.append(self.below)
        if self.left is not None:
            words.append('left')
            values.append(self.left)
        elif self.right is not None:
            words.append('right')
            values.append(self.right)
        words_str = " ".join(words)
        direction_str = " and ".join(str(v) for v in values)
        return f'[{words_str}={direction_str} of {self.anchor.as_tikz()}] '


@dataclass
class NodeContainer:
    nodes: Collection[str]
    corner_text: NodeText | None = None
    corner_color: str | None = None

    def latex_fit(self) -> str:
        nodes = sorted('(' + node + ')' for node in self.nodes)
        return 'fit={' + " ".join(nodes) + '}'

    def latex_corner(self,
                     parent_name: str,
                     opacity: float | None,
                     inherit_color: str | None) -> str:
        if self.corner_text is None:
            return ""
        color = self.corner_color if self.corner_color is not None else inherit_color
        return formatter(
            r"\node[“color,opacity,text_options,”align=right, below left] at (“name”.north east) "
            r"{“text”}",
            name=parent_name,
            text_options=self.corner_text.latex_options(),
            text=self.corner_text.latex(color),
            color=color,
            opacity=None if opacity is None else tikz_option('opacity', str(opacity)))


@dataclass
class Node:
    name: str | None = None
    position: NodePosition | None = None
    container: NodeContainer | None = None
    _: KW_ONLY
    # Text
    text: str | NodeText | None = None
    label: NodeLabel | None = None
    # Appearance
    size: tuple[float, float] | None = None
    shape: str | None = None
    color: str | None = None
    dash: str | None = None
    opacity: float | None = None
    inner_sep: float | None = None
    is_coordinate: bool = False

    def extent(self, node_graph: 'NodeGraph') -> Rect | None:
        if self.position is not None:
            from .anchor import CoordinateAnchor  # noqa: PLC0415
            if isinstance(self.position.anchor, CoordinateAnchor):
                position = np.asarray([self.position.anchor.x, self.position.anchor.y])
                size = np.asarray(self.size) if self.size else np.zeros(2)
                return Rect.from_point(position).bordered(size / 2)
        elif self.container is not None:
            nodes: list[Node] = [node_graph.digraph.nodes[node]['node']
                                 for node in self.container.nodes]
            extents = [node.extent(node_graph) for node in nodes]
            if not extents or any(extent is None for extent in extents):
                return None
            non_none_extents = [extent for extent in extents if extent is not None]
            combined = reduce(Rect.union, non_none_extents)
            return combined.bordered(self.inner_sep) if self.inner_sep else combined
        return None

    def generate(self,
                 file: TextIO,
                 end: str = ';\n'
                 ) -> None:
        """Generate text for a node."""
        text = NodeText([self.text]) if isinstance(self.text, str) else self.text
        size_latex = (None
                      if self.size is None
                      else (f'minimum width={format_length(self.size[0])}, '
                            f'minimum height={format_length(self.size[1])}'))
        opacity = (None if self.opacity is None or self.opacity == 1
                   else tikz_option('opacity', str(self.opacity)))

        d = {"name": self.name,
             "position": None if self.position is None else self.position.latex_position(),
             "relative_position": (
                 None if self.position is None else self.position.latex_relative_position()),
             "text": None if text is None else text.latex(self.color),
             "text_options": None if text is None else text.latex_options(),
             "label": None if self.label is None else self.label.latex(self.color),
             "size": size_latex,
             "shape": self.shape,
             "color": self.color,
             "dash": self.dash,
             "opacity": opacity,
             "inner_sep": tikz_option('inner sep', format_length(self.inner_sep)),
             "fit": None if self.container is None else self.container.latex_fit()}
        if self.is_coordinate:
            pf(r"\coordinate “relative_position” (“name”) “position”",
               **d,
               file=file,
               end=end)
        elif self.name is None:
            assert self.position is None
            pf(r"node[“text_options,label,shape,size,color,dash,opacity,inner_sep,fit”] {“text”}",
               **d,
               file=file,
               end=end)
        else:
            pf(r"\node[“text_options,label,shape,size,color,dash,opacity,inner_sep,fit”] "
               r"“position” (“name”) “relative_position” {“text”}",
               **d,
               file=file,
               end=end)
        if self.container is not None:
            assert isinstance(self.name, str)
            print(self.container.latex_corner(self.name, self.opacity, self.color),
                  file=file,
                  end=end)
