from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

__all__ = ['CurveSource']


class CurveSource:
    """The base class for sources of a graphed curve.

    Args:
        start_time: The start time, which is inclusive.
        end_time: The end time, which is inclusive.
    """

    def __init__(self, start_time: float, end_time: float) -> None:
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time

    # Abstract methods -----------------------------------------------------------------------------
    def times_and_values(self, resolution: int) -> Iterable[np.ndarray[Any, Any]]:
        raise NotImplementedError
