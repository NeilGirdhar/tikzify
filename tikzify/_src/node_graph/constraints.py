from __future__ import annotations

import itertools as it
from collections.abc import Iterable, Mapping, Reversible, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

__all__ = []


@dataclass
class Location:
    x: float
    y: float


class Constraints:  # noqa: PLR0904
    """Constraint-solver.

    This class transforms a set of constraints into two-dimensional positions
    that best satisfy those constraints.
    """

    def __init__(self, labels: Sequence[str]) -> None:
        super().__init__()
        self.labels = labels
        self.a = np.zeros((0, 2 * len(labels)))
        self.b = np.zeros((0,))

    # Properties --------------------------------------------------------------
    @property
    def num_labels(self) -> int:
        return len(self.labels)

    @property
    def num_constraints(self) -> int:
        return self.b.shape[0]

    # New methods -------------------------------------------------------------
    def add_constraint(self, a: np.ndarray[Any, Any], b: float) -> None:
        self.a = np.vstack((self.a, a.reshape((1, 2 * self.num_labels))))
        self.b = np.hstack((self.b, b))

    def blank(self) -> np.ndarray[Any, Any]:
        return np.zeros((2 * self.num_labels,))

    def index(self, coord: str, label: str) -> int:
        return self.labels.index(label) + (self.num_labels if coord == 'y' else 0)

    def set_value(self, coord: str, c: str, value: float = 0.0) -> None:
        a = self.blank()
        a[self.index(coord, c)] = 1.0
        self.add_constraint(a, value)

    def set_delta(self, coord: str, *args: str, delta: float | Iterable[float] = 0.0) -> None:
        if len(args) <= 1:
            raise ValueError
        deltas: Iterable[float]
        deltas = it.repeat(delta) if isinstance(delta, int | float) else delta
        for x, y, this_delta in zip(args, args[1:], deltas, strict=False):
            a = self.blank()
            a[self.index(coord, x)] = 1.0
            a[self.index(coord, y)] = -1.0
            self.add_constraint(a, this_delta)

    def set_deltas(self,
                   *args: str,
                   delta: tuple[float, float] | list[tuple[float, float]] = (0.0, 0.0)
                   ) -> None:
        deltas: Sequence[tuple[float, float]]
        deltas = [delta for _ in range(len(args))] if isinstance(delta, tuple) else delta
        self.set_delta_x(*args, delta_x=[x for x, _ in deltas])
        self.set_delta_y(*args, delta_y=[y for _, y in deltas])

    def set_x(self, c: str, x: float) -> None:
        self.set_value('x', c, x)

    def set_y(self, c: str, y: float) -> None:
        self.set_value('y', c, y)

    def set_delta_x(self, *args: str, delta_x: Reversible[float] | float = 0.0) -> None:
        """Stack each of the args horizontally, spaced by delta_x, from left to right."""
        if not isinstance(delta_x, int | float):
            delta_x = list(reversed(delta_x))
        self.set_delta('x', *reversed(args), delta=delta_x)

    def set_delta_y(self, *args: str, delta_y: Sequence[float] | float = 0.0) -> None:
        """Stack each of the args vertically, spaced by delta_y, from top to bottom."""
        self.set_delta('y', *args, delta=delta_y)

    def set_location(self, c: str, location: tuple[float, float]) -> None:
        """Set c.x, c.y = location."""
        if len(location) != 2:  # noqa: PLR2004
            raise ValueError
        self.set_x(c, location[0])
        self.set_y(c, location[1])

    def set_between(self,
                    coord: str,
                    *items: str,
                    ratios: None | Sequence[float] = None) -> None:
        """Space n items with spacing according to (n-1) ratios.

        E.g., ratios=[0, 1] puts item[1] at item[0]
        fraction = (d-c)/(d-c + (e-d)) => (d-c) = (e-c) * fraction.
        """
        if ratios is None:
            ratios = [1] * (len(items) - 1)
        for c, d, e, r1, r2 in zip(items, items[1:], items[2:], ratios, ratios[1:],
                                   strict=False):
            fraction = r1 / (r1 + r2)
            a = self.blank()
            a[self.index(coord, c)] += fraction - 1.0
            a[self.index(coord, d)] += 1.0
            a[self.index(coord, e)] -= fraction
            self.add_constraint(a, 0.0)

    def set_x_between(self, *items: str, ratios: None | Sequence[float] = None) -> None:
        self.set_between('x', *items, ratios=ratios)

    def set_y_between(self, *items: str, ratios: None | Sequence[float] = None) -> None:
        self.set_between('y', *items, ratios=ratios)

    def set_deltas_equal(self, c: str, d: str, e: str, f: str) -> None:
        self.set_delta_x_equal(c, d, e, f)
        self.set_delta_y_equal(c, d, e, f)

    def set_delta_equal(self, coord: str, c: str, d: str, e: str, f: str) -> None:
        """Set c - d = e - f."""
        a = self.blank()
        a[self.index(coord, c)] += 1.0
        a[self.index(coord, d)] -= 1.0
        a[self.index(coord, e)] -= 1.0
        a[self.index(coord, f)] += 1.0
        self.add_constraint(a, 0.0)

    def set_delta_x_equal(self, c: str, d: str, e: str, f: str) -> None:
        self.set_delta_equal('x', c, d, e, f)

    def set_delta_y_equal(self, c: str, d: str, e: str, f: str) -> None:
        self.set_delta_equal('y', c, d, e, f)

    def set_slope(self, slope: float, *args: str) -> None:
        if len(args) < 2:  # noqa: PLR2004
            raise ValueError
        for c, d in it.pairwise(args):
            a = self.blank()
            a[self.index('x', c)] += slope
            a[self.index('x', d)] -= slope
            a[self.index('y', c)] -= 1.0
            a[self.index('y', d)] += 1.0
            self.add_constraint(a, 0.0)

    def solve(self, decimals: int = 6) -> Mapping[str, Location]:
        solution, _, rank, _ = np.linalg.lstsq(self.a, self.b, rcond=None)
        # solution = np.linalg.solve(self.a, self.b)
        if rank != 2 * self.num_labels:
            msg = f"Only {rank} constraints provided for a problem that needs {2 * self.num_labels}"
            raise Constraints.InsufficientConstraintsError(msg)
        solution = np.around(solution, decimals=decimals)
        solution_is_zero = solution == 0.0
        solution = np.where(np.signbit(solution) & solution_is_zero, -solution, solution)
        return {name: Location(solution[self.index('x', name)], solution[self.index('y', name)])
                for name in self.labels}

    # Exceptions --------------------------------------------------------------
    class InsufficientConstraintsError(Exception):
        pass
