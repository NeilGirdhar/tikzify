from copy import copy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence, TextIO

from ..foundation.pf import pf, pf_option
from .anchor import Anchor

__all__ = ['Label']


@dataclass
class Label:
    lines: Sequence[str]
    location: Optional[str] = None
    color: Optional[str] = None

    def latex(self) -> str:
        lines = self.lines
        if self.color is not None:
            lines = [r'\textcolor{' + self.color + '}{' + line + '}'
                     for line in lines]
        retval = r' \\ '.join(lines)
        if '\\' in retval:
            retval = '{' + retval + '}'
        if self.location:
            retval = f'{self.location}:{retval}'
        return retval


def generate_node(name: Optional[str],
                  node_dict: Mapping[str, Any],
                  *,
                  file: TextIO,
                  end: str = ';\n') -> None:
    fit: Optional[str] = None
    if 'fit' in node_dict:
        def get_fits() -> Iterable[str]:
            for fit in node_dict['fit']:
                assert isinstance(fit, str)
                yield '(' + fit + ')'
        fit = 'fit={' + " ".join(get_fits()) + '}'

    relpos = pos = None
    if node_dict.get('pos', None) is not None:
        pos_node = node_dict['pos']
        assert isinstance(pos_node, Anchor)
        pos = 'at ({}) '.format(pos_node.as_tikz())
    if 'relpos' in node_dict:
        x, y, rel_node = node_dict['relpos']
        words = []
        values = []
        if x == 0 and y == 0:
            pos = 'at ({}) '.format(rel_node.as_tikz())
        else:
            if isinstance(y, tuple):
                words.append('above' if y[0] else 'below')
                values.append(y[1])
            elif y > 0:
                words.append('above')
                values.append(y)
            elif y < 0:
                words.append('below')
                values.append(-y)
            if isinstance(x, tuple):
                words.append('right' if x[0] else 'left')
                values.append(x[1])
            elif x > 0:
                words.append('right')
                values.append(x)
            elif x < 0:
                words.append('left')
                values.append(-x)
            relpos = '[{}={} of {}] '.format(
                " ".join(words),
                " and ".join(str(v) for v in values),
                rel_node.as_tikz())
    text = node_dict.get('text', None)
    state = node_dict.get('state', None)
    coordinate = node_dict.get('coordinate', False)
    col = node_dict.get('col', None)
    label = node_dict.get('label', None)
    if label is not None:
        assert isinstance(label, Label)
        if label.color is None:
            label = copy(label)
            label.color = col
        label = 'label=' + label.latex()
    d = dict(name=name,
             text=text,
             state=state,
             label=label,
             fit=fit,
             pos=pos,
             relpos=relpos,
             col=col,
             opacity=pf_option(node_dict, 'opacity'),
             inner_sep=pf_option(node_dict, 'inner_sep', 'inner sep'),
             text_width=pf_option(node_dict, 'text_width', 'text width'),
             text_centered=pf_option(node_dict,
                                     'text_centered',
                                     'text centered'),
             dash=node_dict.get('dash', None),
             nodepos=pf_option(node_dict, 'nodepos', 'pos'),
             swap=pf_option(node_dict, 'swap'))
    if coordinate:
        pf(r"""
           \coordinate “relpos” (“name”) “pos”
           """,
           **d,
           file=file,
           end=end)
    else:
        if name is None:
            pf(r"""
               node[“state,opacity,fit,col,dash,inner_sep,label,text_width,text_centered,swap,nodepos”] {“text”}
               """,
               **d,
               file=file,
               end=end)
        else:
            pf(r"""
               \node[“state,opacity,fit,col,dash,inner_sep,label,text_width,text_centered”] “pos”(“name”) “relpos”{“text”}
               """,
               **d,
               file=file,
               end=end)
    if 'corner' in node_dict:
        conditional_dictionary = {}
        if 'opacity' in d:
            conditional_dictionary['opacity'] = d['opacity']
        pf(r"""
           \node[“col,opacity,”align=right, below left] at (“name”.north east) {“text”}
           """,
           name=name,
           col=node_dict['corner'].get('col', col),
           text=node_dict['corner']['text'],
           **conditional_dictionary,
           file=file,
           end=end)
