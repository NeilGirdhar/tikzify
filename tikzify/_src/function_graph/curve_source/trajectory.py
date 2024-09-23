from __future__ import annotations

from collections.abc import Iterable
from typing import Any, override

import numpy as np
from scipy.signal import resample

from .curve_source import CurveSource

__all__ = ['TrajectoryCurveSource']


class TrajectoryCurveSource(CurveSource):

    def __init__(self,
                 times: np.ndarray[Any, Any],
                 values: np.ndarray[Any, Any]) -> None:
        assert times.ndim == 1
        super().__init__(times[0], times[-1])
        self.times = times
        self.values = values

    # Implemented methods --------------------------------------------------------------------------
    @override
    def times_and_values(self, resolution: int) -> Iterable[np.ndarray[Any, Any]]:
        data_length = len(self.times)
        use_resample = data_length > resolution
        return_length = resolution if use_resample else data_length

        times = self.times
        values = self.values
        assert values.ndim == 1
        assert values.shape[0] == data_length

        if use_resample:
            times = resample(times, return_length)
            values = resample(values, return_length)

        return [np.stack((times, values), axis=-1)]
