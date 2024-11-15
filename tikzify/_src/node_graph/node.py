from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, TextIO

from ..foundation.formatter import formatter
from ..foundation.pf import pf, tikz_option
from .anchor import Anchor

__all__ = [
    'Alignment',
    'NodeContainer',
    'NodeLabel',
    'NodePosition',
    'NodeText',
    'TerminalSpacing',
    'TextSize',
]


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


def format_length(length: None | float) -> None | str:
    if length is None:
        return None
    if int(length) == length:
        length = int(length)
        if length % 10 == 0:
            return f"{length // 10}cm"
    return f"{length}mm"


def wrap_text(text_lines: Sequence[str],
              color: None | str,
              wrap_command: None | str,
              size: None | TextSize,
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
    wrap_command: None | str = None
    color: None | str = None
    width: None | float = None
    align: None | Alignment = None
    size: None | TextSize = None
    standard_height: bool = False

    def latex(self, inherit_color: None | str) -> str:
        return wrap_text(self.text_lines,
                         inherit_color if self.color is None else self.color,
                         self.wrap_command,
                         self.size,
                         standard_height=self.standard_height)

    def latex_options(self) -> None | str:
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
    location: None | str = None
    color: None | str = None
    size: None | TextSize = None
    standard_height: bool = False

    def latex(self, inherit_color: None | str) -> str:
        text_lines = self.text_lines

        color = inherit_color if self.color is None else self.color
        text = wrap_text(text_lines, color, None, self.size, standard_height=self.standard_height)
        if self.location:
            text = f'{self.location}:{text}'
        return 'label=' + text


@dataclass
class NodePosition:
    anchor: Anchor
    left: None | float = None
    right: None | float = None
    above: None | float = None
    below: None | float = None

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
    corner_text: None | NodeText = None
    corner_color: None | str = None

    def latex_fit(self) -> str:
        nodes = sorted('(' + node + ')' for node in self.nodes)
        return 'fit={' + " ".join(nodes) + '}'

    def latex_corner(self,
                     parent_name: str,
                     opacity: None | float,
                     inherit_color: None | str) -> str:
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


def generate_node(name: None | str,
                  node_dict: Mapping[str, Any],
                  *,
                  opacity: None | float = None,
                  file: TextIO,
                  end: str = ';\n') -> None:
    """Generate text for a node."""
    # Arguments.
    position = node_dict.get('position', None)
    coordinate = node_dict.get('is_coordinate', False)
    text = node_dict.get('text', None)
    label = node_dict.get('label', None)
    size = node_dict.get('size', None)
    shape = node_dict.get('shape', None)
    color = node_dict.get('color', None)
    dash = node_dict.get('dash', None)
    inner_sep = node_dict.get('inner_sep', None)
    container = node_dict.get('container', None)

    size_latex = (None
                  if size is None
                  else (f'minimum width={format_length(size[0])}, '
                        f'minimum height={format_length(size[1])}'))

    d = {"name": name,
             "position": None if position is None else position.latex_position(),
             "relative_position": None if position is None else position.latex_relative_position(),
             "text": None if text is None else text.latex(color),
             "text_options": None if text is None else text.latex_options(),
             "label": None if label is None else label.latex(color),
             "size": size_latex,
             "shape": shape,
             "color": color,
             "dash": dash,
             "opacity": None if opacity is None else tikz_option('opacity', str(opacity)),
             "inner_sep": tikz_option('inner sep', format_length(inner_sep)),
             "fit": None if container is None else container.latex_fit()}
    if coordinate:
        pf(r"\coordinate “relative_position” (“name”) “position”",
           **d,
           file=file,
           end=end)
    elif name is None:
        assert position is None
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
    if container is not None:
        print(container.latex_corner(name, opacity, color),
              file=file,
              end=end)
