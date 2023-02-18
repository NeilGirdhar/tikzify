from __future__ import annotations

import itertools as it
from collections.abc import Mapping, Sequence
from copy import copy
from typing import TextIO

import networkx as nx

from .anchor import CoordinateAnchor, IntersectionAnchor, NodeAnchor, RelativeAnchor
from .edge import Edge
from .multi_edge import angles, create_waypoints, default_waypoint_names
from .node import NodeContainer, NodeLabel, NodePosition, NodeText, TerminalSpacing, generate_node

__all__ = ['NodeGraph']


class NodeGraph:

    def __init__(self, edge_colors: None | Mapping[str, str] = None):
        self.digraph = nx.MultiDiGraph()
        self.edge_colors = {} if edge_colors is None else edge_colors

    # Magic methods --------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return repr(self.digraph)

    # Information methods --------------------------------------------------------------------------
    def nodes(self) -> Sequence[str]:
        return sorted(self.digraph)

    def node_opacity(self, name: str, dependency_graph: nx.DiGraph) -> float:
        """Calcule the node opacity.

        This is based on the maximum opacity of the node, its afferent edges, its fit group (if it
        has one).
        """
        g = self.digraph
        node_dict = g.nodes[name]

        # Calculate the maximum opacity of the node and its afferent edges.
        o = node_dict.get('opacity', 0.0)
        for successor in it.chain([name], dependency_graph.successors(name)):
            for ed in it.chain(g.succ[successor].values(), g.pred[successor].values()):
                for tip in ed.values():
                    o = max(o, tip.get('opacity', 1.0))

        # If the node is in a fit group, consider that too.
        if 'container' in node_dict:
            container = node_dict['container']
            if not isinstance(container, NodeContainer):
                raise TypeError
            for node in container.nodes:
                o = max(o, self.node_opacity(node, dependency_graph))

        return o

    # Graph creation methods -----------------------------------------------------------------------
    def create_coordinate(self,
                          name: str,
                          position: tuple[float, float] | NodePosition) -> None:
        if isinstance(position, tuple):
            position = NodePosition(CoordinateAnchor(*position))
        self.digraph.add_node(name,
                              position=position,
                              is_coordinate=True)

    def create_node(self,
                    name: str,
                    position: None | NodePosition,
                    container: None | NodeContainer = None,
                    *,
                    # Text
                    text: None | str | NodeText = None,
                    label: None | NodeLabel = None,
                    # Appearance
                    size: None | tuple[float, float] = None,
                    shape: None | str = None,
                    color: None | str = None,
                    dash: None | str = None,
                    opacity: None | float = None,
                    inner_sep: None | float = None) -> None:
        if position is None and container is None:
            raise ValueError
        if position is not None and container is not None:
            raise ValueError
        if isinstance(text, str):
            text = NodeText([text])
        d = {"text": text,
                 "label": label,
                 "size": size,
                 "shape": shape,
                 "color": color,
                 "dash": dash,
                 "opacity": opacity,
                 "inner_sep": inner_sep,
                 "container": container}
        d = {key: value
             for key, value in d.items()
             if value is not None}
        self.digraph.add_node(name, position=position, **d)

    def create_edge(self,
                    source: str,
                    target: str,
                    edge: Edge,
                    *,
                    via: None | tuple[bool, Sequence[str]] = None) -> None:
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
                     margin: None | float = None) -> None:
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
                              spacing: TerminalSpacing,
                              left: int = 0,
                              right: int = 0,
                              above: int = 0,
                              below: int = 0) -> None:
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
                  relative: None | float = None) -> None:
        """Places an input/output on the edge, perpendicular to the terminal."""
        if edge in ['bottom_edge', 'top_edge']:
            intersection = IntersectionAnchor(NodeAnchor(terminal), NodeAnchor(edge))
            key = 'above' if edge == 'top_edge' else 'below'
        else:
            intersection = IntersectionAnchor(NodeAnchor(edge), NodeAnchor(terminal))
            key = 'right' if edge == 'right_edge' else 'left'
        position = NodePosition(intersection, **{key: 0.0 if relative is None else relative})

        self.create_node(node_name,
                         position,
                         text=text)

    # Output methods -------------------------------------------------------------------------------
    def generate(self, f: TextIO) -> None:
        g = self.digraph
        dependency_graph, topo_sorted = self._dependencies()
        waypoint_names = default_waypoint_names()

        # Draw nodes.
        for name in topo_sorted:
            node_dict = g.nodes[name]
            generate_node(name, node_dict, opacity=self.node_opacity(name, dependency_graph),
                          file=f)

        # Draw edges.
        for source in topo_sorted:
            for (target, ed) in sorted(g.succ[source].items()):
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

                    color = edge.solve_for_color(self.edge_colors)

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
    def _dependencies(self) -> tuple[Sequence[str], nx.DiGraph]:
        """The dependencies of nodes in the graph.

        Returns:
            topo_sorted: A topological sort of the dependency graph.
            dependency_graph: The graph of dependencies.
        """
        g = self.digraph
        g2 = nx.DiGraph()  # A graph with all dependencies.
        g2.add_nodes_from(g)
        for name in g:
            node_dict = g.nodes[name]
            position = node_dict.get('position', None)
            if position is not None:
                if not isinstance(position, NodePosition):
                    raise TypeError
                for node in position.anchor.base_nodes():
                    g2.add_edge(node, name)
            if 'container' in node_dict:
                container = node_dict['container']
                if not isinstance(container, NodeContainer):
                    raise TypeError
                for node in container.nodes:
                    g2.add_edge(node, name)
        try:
            return g2, list(nx.lexicographical_topological_sort(g2))
        except nx.NetworkXUnfeasible:
            raise ValueError("Cyclic dependencies: " + str(list(nx.simple_cycles(g2)))) from None
