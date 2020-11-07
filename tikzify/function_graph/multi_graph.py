import string
from typing import Callable, Iterable, Sequence, TextIO, Tuple

from ..node_graph import NodeText
from .annotation import Annotation
from .curve_generator import generate_curve
from .curve_source import CurveSource
from .draw import (FILL_OPACITY, FUNCTION_GRAPH_WIDTH, draw_curve, function_graph_line,
                   function_graph_marks)
from .graph import FunctionGraph
from .legend import LegendRect, generate_legend
from .trait import GraphedTrait

__all__ = ['FunctionMultiGraph']


class FunctionMultiGraph:

    def __init__(self,
                 graphs: Sequence[FunctionGraph],
                 traits: Sequence[GraphedTrait],
                 palette: Sequence[Tuple[str, str]],
                 *,
                 graph_spacing: float = 1.4,
                 resolution: int = 200):
        # Store parameters.
        self.graphs = graphs
        self.traits = traits
        self.palette = palette
        self.graph_spacing = graph_spacing
        self.resolution = resolution

        # Memoize.
        self.altitudes = []
        altitude = 0.0
        for _ in graphs:
            self.altitudes.append(altitude)
            altitude -= graph_spacing

    def get_curve_transform(self, altitude: float, scale: float) -> (
            Callable[[float, float], Tuple[float, float]]):
        def curve_transform(x: float, y: float) -> Tuple[float, float]:
            return (x * FUNCTION_GRAPH_WIDTH,
                    y * scale + altitude)
        return curve_transform

    def generate_curves(self, f: TextIO) -> None:
        clip = (-self.graph_spacing * 0.95,
                self.graph_spacing * 0.95)
        for trait, (color, fill_color) in zip(self.traits, self.palette):
            for altitude, graphed_element in zip(self.altitudes, self.graphs):
                if trait in graphed_element.trait_to_curve:
                    curve_source = graphed_element.trait_to_curve[trait]
                    if not isinstance(curve_source, CurveSource):
                        raise TypeError
                    curve = generate_curve(curve_source, fill=True, resolution=self.resolution)

                    # value to paper: translate x, scale x and y, translate y
                    # clip happens on paper coordinates
                    transform = self.get_curve_transform(altitude, trait.scale)
                    this_clip = (clip[0] + altitude, clip[1] + altitude)
                    draw_curve(f, color, fill_color, curve, fill=True, transform=transform,
                               clip=this_clip)
                if trait in graphed_element.trait_to_marks:
                    marks = graphed_element.trait_to_marks[trait]
                    function_graph_marks(f, altitude, marks, color)

    def generate(self, f: TextIO) -> None:
        self.generate_curves(f)
        self.generate_graph_lines(f)
        self.generate_legend(f)

    def generate_graph_lines(self, f: TextIO) -> None:
        for altitude, graphed_element in zip(self.altitudes, self.graphs):
            function_graph_line(f, graphed_element.label, altitude, True)

    def generate_annotations(self, f: TextIO, annotations: Iterable[Annotation]) -> None:
        annotation_letter = 0
        for annotation in annotations:
            if annotation.text is None:
                annotation.text = NodeText([string.ascii_uppercase[annotation_letter]])
                annotation_letter += 1
            annotation.generate(f)

    def generate_legend(self, f: TextIO) -> None:
        legend = []
        for i, (trait, (color, fill_color)) in enumerate(
                zip(self.traits, self.palette)):
            legend_text = trait.legend_text
            dimmed_fill_color = f"{fill_color}!{FILL_OPACITY * 100}!white"
            legend.append((legend_text,
                           LegendRect(f"legend{i}",
                                      color,
                                      dimmed_fill_color)))

        x = FUNCTION_GRAPH_WIDTH
        generate_legend(f,
                        x,
                        -(len(self.graphs) - 1) / 2
                        * self.graph_spacing,
                        legend)
