from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from .anchor import CoordinateAnchor
from .constraints import Location
from .edge import Edge
from .graph import NodeGraph
from .node import Alignment, Node, NodePosition, NodeText

__all__ = ['EdgeSpecification', 'create_links', 'create_nodes']


@dataclass
class EdgeSpecification:
    source: str
    target: str
    to: str
    present: list[str] = field(default_factory=list)
    opaque: list[str] = field(default_factory=list)
    via: tuple[bool, Sequence[str]] | None = None
    text_node: Node | None = None
    dash: str | None = None

    def is_present(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.present + self.opaque
        if not present_keywords:
            return True
        return any(dk in present_keywords
                   for dk in diagram_keywords)

    def is_opaque(self, diagram_keywords: Iterable[str]) -> bool:
        present_keywords = self.opaque
        if not present_keywords:
            return True
        return any(dk in present_keywords
                   for dk in diagram_keywords)


def create_nodes(node_graph: NodeGraph,
                 positions: Mapping[str, Location],
                 node_name_to_text: Mapping[str, Sequence[str]],
                 node_size: tuple[float, float],
                 margin: float,
                 *,
                 containers: Sequence[Node] = ()
                 ) -> None:
    for node_name, position in positions.items():
        if node_name in node_name_to_text:
            text_lines = node_name_to_text[node_name]
            text = NodeText(text_lines=text_lines,
                            wrap_command='nodename',
                            align=Alignment.center)
            node = Node(node_name,
                        NodePosition(CoordinateAnchor(position)),
                        text=text,
                        size=node_size,
                        shape='rectangle')
            node_graph.create_node(node)
        else:
            node_graph.create_coordinate(node_name, (position.x, position.y))
    for container in containers:
        node_graph.create_node(container)
    extents = {}
    for name, node in node_graph.digraph.nodes(data='node'):
        assert isinstance(node, Node)
        extent = node.extent(node_graph)
        if extent is None:
            continue
        extents[name] = extent
    left = min(extents.items(), key=lambda n_ex: n_ex[1].mins[0])[0]
    right = max(extents.items(), key=lambda n_ex: n_ex[1].maxes[0])[0]
    top = max(extents.items(), key=lambda n_ex: n_ex[1].maxes[1])[0]
    bottom = min(extents.items(), key=lambda n_ex: n_ex[1].mins[1])[0]
    node_graph.create_edges(left, right, top, bottom, margin=margin)


def create_links(node_graph: NodeGraph,
                 links: Sequence[EdgeSpecification],
                 dimmed_opacity: float = 1.0,
                 diagram_keywords: Collection[str] | None = None) -> None:
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
