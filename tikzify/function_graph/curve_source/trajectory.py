from typing import Any, Iterable, Tuple

import numpy as np
from scipy.signal import resample
from tjax import PlottableTrajectory

from .curve_source import CurveSource

__all__ = ['TrajectoryCurveSource']


class TrajectoryCurveSource(CurveSource):

    def __init__(self,
                 p_trajectory: PlottableTrajectory[Any],
                 name: str,
                 index: Tuple[int, ...]):
        super().__init__(p_trajectory.times[0], p_trajectory.times[-1])

        if not isinstance(p_trajectory, PlottableTrajectory):
            raise TypeError

        self.p_trajectory = p_trajectory
        self.name = name
        self.index = index

    # Implemented methods --------------------------------------------------------------------------
    def times_and_values(self, resolution: int) -> Iterable[np.ndarray]:
        data_length = len(self.p_trajectory.times)
        use_resample = data_length > resolution
        return_length = resolution if use_resample else data_length

        times = self.p_trajectory.times
        values = getattr(self.p_trajectory.trajectory, self.name)
        values = values[(slice(None), *self.index)]
        assert values.ndim == 1
        assert values.shape[0] == data_length

        if use_resample:
            values = resample(values, return_length)

        return [np.stack((times, values), axis=-1)]
