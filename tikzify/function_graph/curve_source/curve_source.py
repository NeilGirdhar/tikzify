from typing import Iterable

import numpy as np

__all__ = ['CurveSource']


class CurveSource:

    def __init__(self, start_time: float, end_time: float):
        """
        Args:
            start_time: The start time, which is inclusive.
            end_time: The end time, which is inclusive.
        """
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time

    # Abstract methods -----------------------------------------------------------------------------
    def times_and_values(self, resolution: int) -> Iterable[np.ndarray]:
        raise NotImplementedError
