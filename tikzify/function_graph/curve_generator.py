from typing import Iterable

import numpy as np
from more_itertools import mark_ends

from .curve_source import CurveSource

__all__ = ['generate_curve']


def _generate_curve(curve_source: CurveSource,
                    *,
                    fill: bool,
                    resolution: int) -> Iterable[np.ndarray]:
    for is_first, is_last, section in mark_ends(curve_source.times_and_values(resolution)):
        assert section.ndim == 2
        if section.shape[0] == 0:
            continue
        assert section.shape[1] == 2

        # Generate a Jump from 0.0 for the first key when filling.
        if is_first and fill and section[0, 1] != 0.0:
            yield np.array([[section[0, 0], 0.0]])

        yield section

        # Generate a Jump to 0.0 for the last key when filling.
        if is_last and fill:
            yield np.array([[curve_source.end_time, 0.0]])


def generate_curve(curve_source: CurveSource, *, fill: bool, resolution: int) -> np.ndarray:
    sections_and_jumps = list(_generate_curve(curve_source, fill=fill, resolution=resolution))
    if not sections_and_jumps:
        return np.zeros((0, 2))
    return np.concatenate(sections_and_jumps, axis=0)
