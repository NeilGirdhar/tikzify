from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .anchor import CoordinateAnchor
from .constraints import Location
from .edge import Edge
from .graph import NodeGraph
from .node import Alignment, NodePosition, NodeText

__all__ = ['EdgeSpecification', 'create_links', 'create_nodes']


@dataclass
class EdgeSpecification:
    source: str
    target: str
    to: str
    present: list[str]
    opaque: list[str]
    via: None | tuple[bool, Sequence[str]] = None
    text_node: None | Mapping[str, Any] = None
    dash: None | str = None

    def is_present(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.present + self.opaque
        return any(dk in present_keywords
                   for dk in diagram_keywords)

    def is_opaque(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.opaque
        return any(dk in present_keywords
                   for dk in diagram_keywords)


def create_nodes(node_graph: NodeGraph,
                 positions: Mapping[str, Location],
                 node_name_to_text: Mapping[str, Sequence[str]],
                 node_size: tuple[float, float],
                 margin: float
                 ) -> None:
    for node_name, position in positions.items():
        if node_name in node_name_to_text:
            text_lines = node_name_to_text[node_name]
            text = NodeText(text_lines=text_lines,
                            wrap_command='nodename',
                            align=Alignment.center)
            node_graph.create_node(node_name,
                                   NodePosition(CoordinateAnchor(position)),
                                   text=text,
                                   size=node_size,
                                   shape='rectangle',
                                   opacity=None)
        else:
            node_graph.create_coordinate(node_name, (position.x, position.y))
    left = min(positions.items(), key=lambda n_location: n_location[1].x)[0]
    right = max(positions.items(), key=lambda n_location: n_location[1].x)[0]
    top = max(positions.items(), key=lambda n_location: n_location[1].y)[0]
    bottom = min(positions.items(), key=lambda n_location: n_location[1].y)[0]
    node_graph.create_edges(left, right, top, bottom, margin=margin)


def create_links(node_graph: NodeGraph,
                 links: Sequence[EdgeSpecification],
                 dimmed_opacity: float = 1.0,
                 diagram_keywords: None | Collection[str] = None) -> None:
    if diagram_keywords is None:
        diagram_keywords = []
    diagram_keywords = [*list(diagram_keywords), 'all']
    for edge_spec in links:
        if not edge_spec.is_present(diagram_keywords):
            continue
        opacity = 1.0 if edge_spec.is_opaque(diagram_keywords) else dimmed_opacity
        node_graph.create_edge(edge_spec.source, edge_spec.target,
                               Edge(to=edge_spec.to, opacity=opacity,
                                    text_node=edge_spec.text_node,
                                    dash=edge_spec.dash),
                               via=edge_spec.via)
