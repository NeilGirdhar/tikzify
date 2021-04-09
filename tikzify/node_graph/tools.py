from dataclasses import dataclass
from typing import Any, Collection, Iterable, List, Mapping, Optional, Sequence, Tuple, Union, cast

from .anchor import CoordinateAnchor
from .constraints import Constraints
from .edge import Edge
from .graph import NodeGraph
from .node import Alignment, NodePosition, NodeText

__all__ = ['EdgeSpecification', 'create_nodes', 'create_links']


Real = Union[int, float]


@dataclass
class EdgeSpecification:
    source: str
    target: str
    to: str
    present: List[str]
    opaque: List[str]
    via: Optional[Tuple[bool, Sequence[str]]] = None
    text_node: Optional[Mapping[str, Any]] = None
    dash: Optional[str] = None

    def is_present(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.present + self.opaque
        return any(dk in present_keywords
                   for dk in diagram_keywords)

    def is_opaque(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.opaque
        return any(dk in present_keywords
                   for dk in diagram_keywords)


def create_nodes(node_graph: NodeGraph,
                 constraints: Constraints,
                 node_name_to_text: Mapping[str, Sequence[str]],
                 node_size: Tuple[Real, Real]) -> None:
    for node_name in constraints.labels:
        position = cast(Tuple[float, float], tuple(constraints.solved(node_name)))
        if node_name in node_name_to_text:
            text_lines = node_name_to_text[node_name]
            text = NodeText(text_lines=text_lines,
                            wrap_command='nodename',
                            align=Alignment.center)
            node_graph.create_node(node_name,
                                   NodePosition(CoordinateAnchor(*position)),
                                   text=text,
                                   size=node_size,
                                   shape='rectangle',
                                   opacity=None)
        else:
            node_graph.create_coordinate(node_name, position)


def create_links(node_graph: NodeGraph,
                 links: Sequence[EdgeSpecification],
                 dimmed_opacity: Real = 1.0,
                 diagram_keywords: Optional[Collection[str]] = None) -> None:
    if diagram_keywords is None:
        diagram_keywords = []
    diagram_keywords = list(diagram_keywords) + ['all']
    for edge_spec in links:
        if not edge_spec.is_present(diagram_keywords):
            continue
        opacity = 1.0 if edge_spec.is_opaque(diagram_keywords) else dimmed_opacity
        node_graph.create_edge(edge_spec.source, edge_spec.target,
                               Edge(to=edge_spec.to, opacity=opacity,
                                    text_node=edge_spec.text_node,
                                    dash=edge_spec.dash),
                               via=edge_spec.via)
