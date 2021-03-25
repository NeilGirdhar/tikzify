from __future__ import annotations

import itertools as it
from copy import copy
from typing import Mapping, Optional, Sequence, TextIO, Tuple, Union

import networkx as nx

from .anchor import CoordinateAnchor, IntersectionAnchor, NodeAnchor, RelativeAnchor
from .edge import Edge
from .multi_edge import angles, create_waypoints, default_waypoint_names
from .node import NodeContainer, NodeLabel, NodePosition, NodeText, TerminalSpacing, generate_node

__all__ = ['NodeGraph']


class NodeGraph:

    def __init__(self, edge_colors: Optional[Mapping[str, str]] = None):
        self.digraph = nx.MultiDiGraph()
        self.edge_colors = {} if edge_colors is None else edge_colors

    # Magic methods --------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return repr(self.digraph)

    # Information methods --------------------------------------------------------------------------
    def nodes(self) -> Sequence[str]:
        return sorted(self.digraph)

    def node_opacity(self, name: str, dependency_graph: nx.DiGraph) -> float:
        """
        Calculate the maximum opacity of the node, its afferent edges, its fit group (if it has
        one), and set the node's opacity accordingly.
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
                          position: Union[Tuple[float, float], NodePosition]) -> None:
        if isinstance(position, tuple):
            position = NodePosition(CoordinateAnchor(*position))
        self.digraph.add_node(name,
                              position=position,
                              is_coordinate=True)

    def create_node(self,
                    name: str,
                    position: Optional[NodePosition],
                    container: Optional[NodeContainer] = None,
                    *,
                    # Text
                    text: Optional[Union[str, NodeText]] = None,
                    label: Optional[NodeLabel] = None,
                    # Appearance
                    size: Optional[Tuple[float, float]] = None,
                    shape: Optional[str] = None,
                    color: Optional[str] = None,
                    dash: Optional[str] = None,
                    opacity: Optional[float] = None,
                    inner_sep: Optional[float] = None) -> None:
        if position is None and container is None:
            raise ValueError
        if position is not None and container is not None:
            raise ValueError
        if isinstance(text, str):
            text = NodeText([text])
        d = dict(text=text,
                 label=label,
                 size=size,
                 shape=shape,
                 color=color,
                 dash=dash,
                 opacity=opacity,
                 inner_sep=inner_sep,
                 container=container)
        d = {key: value
             for key, value in d.items()
             if value is not None}
        self.digraph.add_node(name, position=position, **d)

    def create_edge(self,
                    source: str,
                    target: str,
                    edge: Edge,
                    *,
                    via: Optional[Tuple[bool, Sequence[str]]] = None) -> None:
        if source not in self.digraph:
            raise ValueError(f"{source} not in graph.")
        if target not in self.digraph:
            raise ValueError(f"{target} not in graph.")
        self.digraph.add_edge(source, target, edge=edge, via=via)

    def create_edges(self,
                     left: str, right: str, top: str, bottom: str,
                     margin_left: bool = True,
                     margin_right: bool = True,
                     margin_top: bool = True,
                     margin_bottom: bool = True,
                     *,
                     margin: Optional[float] = None) -> None:
        if left not in self.digraph:
            raise ValueError(f"{left} not in graph.")
        if right not in self.digraph:
            raise ValueError(f"{right} not in graph.")
        if top not in self.digraph:
            raise ValueError(f"{top} not in graph.")
        if bottom not in self.digraph:
            raise ValueError(f"{bottom} not in graph.")
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
                [True, True, False, False]):
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
                  relative: Optional[float] = None) -> None:
        """
        Places an input/output on the edge, perpendicular to the terminal.
        """
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
        D = default_waypoint_names()

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
                                 if len_ed == 2 else
                                 (i - 1) * 20
                                 if len_ed == 3 else
                                 0)
                        edge.bend = bend

                    color = edge.solve_for_color(self.edge_colors)

                    if via is not None:
                        vertical, turns = via
                        create_waypoints(f,
                                         edge,
                                         source,
                                         list(turns) + [target],
                                         vertical,
                                         D,
                                         color)
                    else:
                        edge.pf(f, source, target, color=color)

    # Private methods ------------------------------------------------------------------------------
    def _dependencies(self) -> Tuple[Sequence[str], nx.DiGraph]:
        """
        Returns:
            dependency_graph: The graph of dependencies.
            topo_sorted: A topological sort of the dependency graph
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
