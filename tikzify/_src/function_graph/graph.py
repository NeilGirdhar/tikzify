from collections.abc import Mapping, Sequence

from .curve_source.curve_source import CurveSource
from .trait import GraphedTrait

__all__ = ['FunctionGraph']


class FunctionGraph:

    def __init__(self,
                 trait_to_curve: Mapping[GraphedTrait, CurveSource] | None = None,
                 trait_to_marks: Mapping[GraphedTrait, Sequence[float]] | None = None,
                 label: str = "") -> None:
        super().__init__()
        self.trait_to_curve = {} if trait_to_curve is None else trait_to_curve
        self.trait_to_marks = {} if trait_to_marks is None else trait_to_marks
        self.label = label.replace('_', ' ')
