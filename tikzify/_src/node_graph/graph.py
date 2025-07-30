from __future__ import annotations

import itertools as it
from collections.abc import Generator, Mapping, Sequence
from copy import copy
from dataclasses import replace
from io import StringIO
from typing import Any, TextIO, override

import networkx as nx

from .anchor import CoordinateAnchor, IntersectionAnchor, NodeAnchor, RelativeAnchor
from .edge import Edge
from .multi_edge import angles, create_waypoints, default_waypoint_names
from .node import Alignment, Node, NodePosition, NodeText, TerminalSpacing, TextSize
from .tips import TipSpecification

__all__ = ['NodeGraph']


class NodeGraph:

    def __init__(self,
                 *,
                 tips: Mapping[str, TipSpecification] | None = None,
                 terminal_spacing: TerminalSpacing | None = None,
                 ) -> None:
        super().__init__()
        self.digraph = nx.MultiDiGraph()
        self.tips = {} if tips is None else tips
        self.terminal_spacing = terminal_spacing

    # Magic methods --------------------------------------------------------------------------------
    @override
    def __repr__(self) -> str:
        return repr(self.digraph)

    # Information methods --------------------------------------------------------------------------
    def nodes(self) -> Sequence[str]:
        return sorted(self.digraph)

    def _all_edges_connected_to(self, node_name: str) -> Generator[Edge]:
        for _, _, edge_dict in it.chain(self.digraph.in_edges(node_name, data=True),
                                        self.digraph.out_edges(node_name, data=True)):
            edge = edge_dict['edge']
            assert isinstance(edge, Edge)
            yield edge

    # Graph creation methods -----------------------------------------------------------------------
    def create_coordinate(self,
                          name: str,
                          position: tuple[float, float] | NodePosition
                          ) -> None:
        if isinstance(position, tuple):
            position = NodePosition(CoordinateAnchor(*position))
        node = Node(name, position, is_coordinate=True)
        self.create_node(node)

    def create_node(self, node: Node) -> None:
        if (node.position is None) == (node.container is None):
            raise ValueError
        self.digraph.add_node(node.name, node=node)

    def create_edge(self,
                    source: str,
                    target: str,
                    edge: Edge,
                    *,
                    via: tuple[bool, Sequence[str]] | None = None
                    ) -> None:
        if source not in self.digraph:
            msg = f"{source} not in graph."
            raise ValueError(msg)
        if target not in self.digraph:
            msg = f"{target} not in graph."
            raise ValueError(msg)
        self.digraph.add_edge(source, target, edge=edge, via=via)

    def create_edges(self,
                     left: str, right: str, top: str, bottom: str,
                     *,
                     margin_left: bool = True,
                     margin_right: bool = True,
                     margin_top: bool = True,
                     margin_bottom: bool = True,
                     margin: float | None = None) -> None:
        if left not in self.digraph:
            msg = f"{left} not in graph."
            raise ValueError(msg)
        if right not in self.digraph:
            msg = f"{right} not in graph."
            raise ValueError(msg)
        if top not in self.digraph:
            msg = f"{top} not in graph."
            raise ValueError(msg)
        if bottom not in self.digraph:
            msg = f"{bottom} not in graph."
            raise ValueError(msg)
        self.create_coordinate('left_edge',
                               NodePosition(RelativeAnchor(left, 'west'),
                                            left=margin if margin_left else None))
        self.create_coordinate('right_edge',
                               NodePosition(RelativeAnchor(right, 'east'),
                                            right=margin if margin_right else None))
        self.create_coordinate('top_edge',
                               NodePosition(RelativeAnchor(top, 'north'),
                                            above=margin if margin_top else None))
        self.create_coordinate('bottom_edge',
                               NodePosition(RelativeAnchor(bottom, 'south'),
                                            below=margin if margin_bottom else None))

    def create_node_terminals(self,
                              node_name: str,
                              left: int = 0,
                              right: int = 0,
                              above: int = 0,
                              below: int = 0,
                              *,
                              spacing: TerminalSpacing | None = None
                              ) -> None:
        if spacing is None:
            spacing = self.terminal_spacing
        if spacing is None:
            raise ValueError
        for num_anchors, cardinal, name_prefix, vertical in zip(
                [left, right, above, below],
                ['west', 'east', 'north', 'south'],
                ['left_of', 'right_of', 'above', 'below'],
                [True, True, False, False],
                strict=True):
            if num_anchors == 0:
                continue
            step = (spacing.vertical if vertical else spacing.horizontal)[num_anchors - 1]
            for i, j in enumerate(angles(0, num_anchors, step=step)):
                x = 0 if vertical else j
                y = j if vertical else 0
                self.create_coordinate(f'{name_prefix}_{node_name}{i}',
                                       NodePosition(RelativeAnchor(node_name, cardinal),
                                                    right=x,
                                                    above=y))

    def create_io(self,
                  node_name: str,
                  text: NodeText,
                  edge: str,
                  terminal: str,
                  relative: float | None = None) -> None:
        """Place an input/output on the edge, perpendicular to the terminal."""
        if edge in {'bottom_edge', 'top_edge'}:
            intersection = IntersectionAnchor(NodeAnchor(terminal), NodeAnchor(edge))
            key = 'above' if edge == 'top_edge' else 'below'
            text = replace(text, align=Alignment.center)
        else:
            intersection = IntersectionAnchor(NodeAnchor(edge), NodeAnchor(terminal))
            key = 'right' if edge == 'right_edge' else 'left'
            text = replace(text, align=Alignment.left if key == 'right' else Alignment.right)
        text = replace(text, standard_height=True)
        if text.size is None:
            text = replace(text, size=TextSize.footnote)
        position = NodePosition(intersection, **{key: 0.0 if relative is None else relative})
        node = Node(node_name, position, text=text)
        self.create_node(node)

    def create_legend(self,
                      position: NodePosition,
                      *,
                      link_heading: str = 'Link type',
                      arrow_heading: str = 'Arrowhead'
                      ) -> None:
        f = StringIO()
        pf(r"""
           \begin{threeparttable}
           \begin{tabular}{rl} \toprule
           \footnotesize “link_heading” & \footnotesize “arrow_heading” \\ \midrule
           """,
           f,
           link_heading=link_heading,
           arrow_heading=arrow_heading)

        all_tips = list(self.tips)
        tip_names = set[str]()
        for _, _, edge_dict in self.digraph.edges(data=True):
            edge = edge_dict['edge']
            assert isinstance(edge, Edge)
            if edge.from_:
                tip_names.add(edge.from_)
            if edge.to:
                tip_names.add(edge.to)

        for tip_name in sorted(tip_names, key=all_tips.index):
            color = self.tips[tip_name].color
            pf(r"""
               \footnotesize “name” & \tikz[baseline=-1mm]{\node[minimum height=2mm] at (0, 0) {};
                                                         \draw[“col, tip”] (0, 0) to (1, 0);} \\
               """,
               end='\n',
               col=color,
               name=self.tips[tip_name].name,
               tip='-tip_' + tip_name,
               file=f)
            assert f.getvalue().endswith('\n')

        pf(r"""
               \bottomrule
             \end{tabular}
           \end{threeparttable}
           """,
           f)
        legend = Node('legend', position, text=f.getvalue())
        self.create_node(legend)

    # Output methods -------------------------------------------------------------------------------
    def generate(self, f: TextIO) -> None:
        _, topo_sorted = self._dependencies()
        self._draw_nodes(f, topo_sorted)
        self._draw_edges(f, topo_sorted)

    def _draw_nodes(self, f: TextIO, topo_sorted: Sequence[str]) -> None:
        for name in topo_sorted:
            node = self.digraph.nodes[name]['node']
            assert isinstance(node, Node)
            assert isinstance(node.name, str)
            if isinstance(node.text, NodeText) and node.text.color is None:
                for edge in self._all_edges_connected_to(name):
                    if (color := edge.solve_for_color(self.tips)) is not None:
                        node = replace(node, color=color)
                        break
            node.generate(file=f)

    def _draw_edges(self, f: TextIO, topo_sorted: Sequence[str]) -> None:
        waypoint_names = default_waypoint_names()
        for source in topo_sorted:
            for (target, ed) in sorted(self.digraph.succ[source].items()):
                len_ed = len(ed)
                for i, edge_dict in enumerate(ed.values()):
                    edge: Edge = copy(edge_dict['edge'])
                    via = edge_dict.get('via', None)

                    if edge.loop is None:
                        bend = edge.bend
                        bend += (0
                                 if len_ed == 1 else
                                 (2 * i - 1) * 14
                                 if len_ed == 2 else  # noqa: PLR2004
                                 (i - 1) * 20
                                 if len_ed == 3 else  # noqa: PLR2004
                                 0)
                        edge.bend = bend

                    color = edge.solve_for_color(self.tips)

                    if via is not None:
                        vertical, turns = via
                        create_waypoints(f,
                                         edge,
                                         source,
                                         [*list(turns), target],
                                         waypoint_names,
                                         color,
                                         vertical=vertical)
                    else:
                        edge.pf(f, source, target, color=color)

    # Private methods ------------------------------------------------------------------------------
    def _dependencies(self) -> tuple[nx.DiGraph[Any], Sequence[str]]:
        """The dependencies of nodes in the graph.

        Returns:
            topo_sorted: A topological sort of the dependency graph.
            dependency_graph: The graph of dependencies.
        """
        g2 = nx.DiGraph()  # A graph with all dependencies.
        g2.add_nodes_from(self.digraph)
        for name in self.digraph:
            node = self.digraph.nodes[name]['node']
            if node.position is not None:
                for sub_node_name in node.position.anchor.base_nodes():
                    g2.add_edge(sub_node_name, name)
            if node.container is not None:
                for sub_node_name in node.container.nodes:
                    g2.add_edge(sub_node_name, node.name)
        try:
            return g2, list(nx.lexicographical_topological_sort(g2))
        except nx.NetworkXUnfeasible:
            raise ValueError("Cyclic dependencies: " + str(list(nx.simple_cycles(g2)))) from None
