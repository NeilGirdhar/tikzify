from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, TextIO

import numpy as np

from ..foundation.pf import pf

__all__ = ['function_graph_marks', 'function_graph_line', 'draw_curve']

# Drawing constants
FUNCTION_GRAPH_WIDTH = 8.5
FUNCTION_GRAPH_EXTRA = 0.2
FILL_OPACITY = 0.4
MARK_WIDTH = 0.06
MARK_HEIGHT = 0.3


def function_graph_mark(f: TextIO, x: float, y: float, col: None | str,
                        scale: float = 1.0) -> None:
    h = scale * MARK_HEIGHT * 0.5
    w = scale * MARK_WIDTH
    pf(r"""
       \draw[“col”, -, ultra thick] (“x”, “top”) -- (“x”, “bottom”);
       """,
       col=col,
       x=x,
       xl=x - w,
       xr=x + w,
       top=y + h,
       bottom=y - h,
       file=f)


def function_graph_marks(f: TextIO,
                         y: float,
                         marks: Iterable[float],
                         mark_color: None | str = None) -> None:
    for x in marks:
        function_graph_mark(f, x * FUNCTION_GRAPH_WIDTH, y, mark_color)


def function_graph_line(f: TextIO, label: str, y: float, *, arrow: bool = False) -> None:
    left = 0.0
    right = 1.0
    pf(r"""
       \node [left] at (“left”, “y”) {“label”};
       \path (“left”, “y”) edge [“arrow”] (“right”, “y”);
       """,
       label=label,
       arrow='->' if arrow else '-',
       y=y,
       left=left * FUNCTION_GRAPH_WIDTH,
       right=right * FUNCTION_GRAPH_WIDTH + (FUNCTION_GRAPH_EXTRA if arrow else 0.0),
       file=f)


def identity(x: float, y: float) -> tuple[float, float]:
    return x, y


def draw_curve(f: TextIO,
               color: str,
               fill_color: str,
               curve: np.ndarray[Any, Any],
               transform: Callable[[float, float], tuple[float, float]] = identity,
               options: None | str = None,
               clip: tuple[float, float] = (-10.0, 10.0),
               *,
               fill: bool) -> None:
    pf(r"""\“drawcmd” [-, thin, draw=“color”“,fill,options”]
       plot coordinates {
       """,
       options=options,
       drawcmd='filldraw' if fill else 'draw',
       fill=(r"“fill_color”, fill opacity=“fill_opacity”" if fill else ""),
       fill_opacity=FILL_OPACITY,
       color=color,
       fill_color=fill_color,
       end=' ',
       file=f)

    for time, value in curve:
        time, value = transform(time, value)
        value = clip[0] if np.isnan(value) else float(np.clip(value, *clip))
        pf(r'(“x:.6f”, “y:.6f”)', x=time, y=value, end=' ', file=f)

    pf('};', file=f)
