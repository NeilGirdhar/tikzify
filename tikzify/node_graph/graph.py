from __future__ import annotations

import itertools as it
import keyword
from collections import abc
from typing import Callable, Iterable, Mapping, Optional, Sequence, TextIO, Tuple, Union

import networkx as nx

from .anchor import Anchor
from .edge import Edge
from .multi_edge import create_waypoints
from .node import generate_node

__all__ = ['NodeGraph']


_C = Union[Callable[[str], str], Mapping[str, str], None]


class NodeGraph:

    def __init__(self,
                 nodes: Optional[Iterable[str]] = None,
                 edges: Optional[Iterable[Tuple[str, str]]] = None,
                 node_text: _C = None,
                 edge_colors: Optional[Mapping[str, str]] = None):
        """
        node_text and node_type are either
        * a callable that maps node names to *,
        * None in which case the map is the identity
        """
        self.edge_colors = ({}
                            if edge_colors is None
                            else edge_colors)
        self.digraph = nx.MultiDiGraph()
        if nodes:
            self.digraph.add_nodes_from(nodes)
        if edges:
            self.digraph.add_edges_from(edges)

        def lookup(y: _C, node: str) -> str:
            if callable(y):
                return y(node)
            if isinstance(y, abc.Mapping):
                return y[node]
            return node

        for node in self.digraph:
            node_dict = self.digraph.nodes[node]
            if 'text' not in node_dict:
                node_dict['text'] = lookup(node_text, node)

    @property
    def nodes(self) -> Sequence[str]:
        return sorted(self.digraph)

    def __repr__(self) -> str:
        return repr(self.digraph)

    @staticmethod
    def math_name(name: str) -> str:
        """
        Given "A3", returns "$A_3$".
        """
        if len(name) == 2 and name[1] != "'":
            name = name[0] + '_' + name[1]
        return '${}$'.format(name)

    def toposorted(self) -> Tuple[Sequence[str], nx.DiGraph]:
        g = self.digraph
        g2 = nx.DiGraph()
        g2.add_nodes_from(g)
        for name in g:
            node_dict = g.nodes[name]
            if 'fit' in node_dict:
                for fit in node_dict['fit']:
                    g2.add_edge(fit, name)
            if 'pos' in node_dict:
                rel_node = node_dict['pos']
                if not isinstance(rel_node, Anchor):
                    raise TypeError
                for node in rel_node.base_nodes():
                    g2.add_edge(node, name)
            if 'relpos' in node_dict:
                _, _, rel_node = node_dict['relpos']
                if not isinstance(rel_node, Anchor):
                    raise TypeError
                for node in rel_node.base_nodes():
                    g2.add_edge(node, name)
        try:
            return list(nx.lexicographical_topological_sort(g2)), g2
        except nx.nx.NetworkXUnfeasible:
            print("Cycles", list(nx.simple_cycles(g2)))
            raise

    def fix_opacity(self) -> None:
        g = self.digraph
        toposorted, dependency_graph = self.toposorted()
        for name in toposorted:
            o = g.nodes[name].get('opacity', 0.0)
            for successor in it.chain([name],
                                      dependency_graph.successors(name)):
                for ed in it.chain(g.succ[successor].values(),
                                   g.pred[successor].values()):
                    for tip in ed.values():
                        o = max(o, tip.get('opacity', 1.0))
            if not g.nodes[name].get('dimming_restrictive', False):
                for fit in g.nodes[name].get('fit', []):
                    o = max(o, g.nodes[fit].get('opacity', 1.0))
            g.nodes[name]['opacity'] = o

    def generate(self, f: TextIO) -> None:
        g = self.digraph
        toposorted, _ = self.toposorted()
        sorted_names = list(toposorted)

        for name in sorted_names:
            node_dict = g.nodes[name]
            if node_dict.get('draw', True):
                generate_node(name, node_dict, file=f)

        for source in sorted_names:
            for (target, ed) in sorted(g.succ[source].items()):
                len_ed = len(ed)
                for i, tip in enumerate(ed.values()):
                    tip = tip.copy()
                    # i_prime = (len_ed - i - 1) if bend_rev else i
                    if 'loop' not in tip:
                        bend = tip.get('bend', 0)
                        bend += (0
                                 if len_ed == 1 else
                                 (2 * i - 1) * 14
                                 if len_ed == 2 else
                                 (i - 1) * 20
                                 if len_ed == 3 else
                                 0)
                        tip['bend'] = bend

                    keywords_passed = set(keyword.kwlist) & set(tip)
                    if keywords_passed:
                        raise ValueError(
                            "Keyword passed as argument: {}".format(
                                keywords_passed.pop()))

                    via = tip.pop('via', None)
                    edge = Edge(**tip, edge_colors=self.edge_colors)
                    if via is not None:
                        vertical, turns, waypoint_names = via
                        create_waypoints(f,
                                         edge,
                                         source,
                                         list(turns) + [target],
                                         vertical,
                                         waypoint_names)
                    else:
                        edge.pf(f, source, target)
