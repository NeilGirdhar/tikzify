from typing import Mapping, Optional, Sequence

from .curve_source import CurveSource
from .trait import GraphedTrait

__all__ = ['FunctionGraph']


class FunctionGraph:

    def __init__(self,
                 trait_to_curve: Optional[Mapping[GraphedTrait, CurveSource]] = None,
                 trait_to_marks: Optional[Mapping[GraphedTrait, Sequence[float]]] = None,
                 label: str = ""):
        self.trait_to_curve = {} if trait_to_curve is None else trait_to_curve
        self.trait_to_marks = {} if trait_to_marks is None else trait_to_marks
        self.label = label.replace('_', ' ')
