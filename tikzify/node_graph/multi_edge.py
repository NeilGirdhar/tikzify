import itertools as it
from copy import copy
from typing import Iterable, List, Sequence, TextIO

from ..foundation.pf import pf
from .edge import Edge

__all__: List[str] = []


def angles(around: float, n: int, step: float) -> Iterable[float]:
    for i in range(n):
        yield around + step * (i - ((n - 1) / 2))


def default_waypoint_names() -> Iterable[str]:
    for i in it.count():
        yield "w{}".format(i)


def create_waypoint(f: TextIO, edge: Edge, source: str, turn: str, stop: str, vertical: bool,
                    create: str, arm: int, color: str) -> None:
    """
    Prints a round edge in the direction of the waypoint.
    """
    edge_copy = copy(edge)
    edge_copy.to = None
    to_command = '|-' if vertical else '-|'
    pf(r"\coordinate (“create”) at "
       r"($(“source” “to_command” “turn”)!5mm!"
       r"(“stop” “to_command” “turn”)$);"
       "\n",
       source=source,
       to_command=to_command,
       create=create,
       turn=turn,
       stop=stop,
       file=f)
    if edge.text_node is not None:
        if edge.text_node['arm'] != arm:
            edge_copy.text_node = None
    edge_copy.pf(f,
                 source,
                 create,
                 color=color,
                 more_options='roundline',
                 to_command=to_command)


def create_waypoints(f: TextIO, edge: Edge, source: str, turns: Sequence[str], vertical: bool,
                     waypoint_names: Iterable[str],
                     color: str) -> None:
    drawn = False
    for arm, (turn, next_turn, create) in enumerate(zip(turns, turns[1:], waypoint_names)):
        create_waypoint(f, edge, source, turn, next_turn, vertical, create, arm, color)
        if not drawn:
            from_, edge.from_ = edge.from_, None
            drawn = True
        source = create
        vertical = not vertical
    to_command = '|-' if vertical else '-|'
    edge_copy = copy(edge)
    if edge.text_node is not None:
        if edge.text_node['arm'] != len(turns) - 1:
            edge_copy.text_node = None
    edge_copy.pf(f,
                 source,
                 turns[-1],
                 more_options='roundline',
                 to_command=to_command,
                 color=color)
    if drawn:
        edge.from_ = from_
