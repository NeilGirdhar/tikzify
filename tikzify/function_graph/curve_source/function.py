from collections import abc
from itertools import chain
from math import ceil
from typing import Callable, Iterable, Sequence

import numpy as np
from more_itertools import pairwise

from .curve_source import CurveSource

__all__ = ['FunctionCurveSource', 'FunctionSection']


class FunctionSection:

    def __init__(self, domain_start: float, function: Callable[[np.ndarray], np.ndarray]):
        self.domain_start = domain_start
        self.function = function


class FunctionCurveSource(CurveSource):

    def __init__(self, sections: Sequence[FunctionSection], end_time: float):
        """
        sections is a sequence.
        """
        if not isinstance(sections, abc.Sequence):
            raise ValueError
        for a, b in pairwise(sections):
            if a.domain_start > b.domain_start:
                raise ValueError
        start_time = (sections[0].domain_start
                      if sections
                      else end_time)
        super().__init__(start_time, end_time)
        self.sections = sections

    # Implemented methods --------------------------------------------------------------------------
    def times_and_values(self, resolution: int) -> Iterable[np.ndarray]:
        time_resolution = (self.end_time - self.start_time) / resolution
        for section, next_section in pairwise(chain(self.sections, [None])):
            assert section is not None
            section_start = section.domain_start
            section_end = self.end_time if next_section is None else next_section.domain_start
            section_period = section_end - section_start
            section_resolution = int(ceil(section_period / time_resolution))
            times = np.linspace(section_start, section_end, section_resolution, endpoint=True)
            values = section.function(times)
            yield np.stack((times, values), axis=-1)
